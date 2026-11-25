"""Pre-notificaties versturen: één bewaakte, idempotente functie.

Afspraken:
- Zelfde rit, terminal en ETA = zelfde bericht. Twee keer sturen geeft geen tweede melding of tweede slot.
- Een andere ETA betekent: annuleren en opnieuw sturen met HETZELFDE label. Dat mag alleen met akkoord van de
  planner (bevestig_wijziging=True). Na het begin van het slot telt dat als no-show (waarschuwing in het logboek).
- Nooit "claimen en annuleren": we sturen alleen voor ritten die echt gepland zijn.
- Noodstop aan = geen automatische berichten.
"""

import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.jobs import handler
from app.planner.context import laad_dag
from app.planner.voorstel import noodstop_aan
from app.ports.clock import NL, klok
from app.ports.portbase import PreNotificatie, gateway
from app.rules.planning import no_show_geheven, terminal_bezoeken
from app.statussen import zet_status

ACTIEF = ("Aangevraagd", "Toegekend", "Gewijzigd")


class BerichtFout(ValueError):
    pass


@dataclass
class Uitkomst:
    terminal: str
    tekst: str
    nieuw: bool  # False = er was al precies dit bericht (idempotent)
    code: str | None = None


def _release_vrij(ctx, rit: m.Rit) -> bool:
    for c in rit.order.containers:
        v = ctx.vrijgave_per_container.get(c.id)
        if not v or v.status != "Vrij" or not (v.commercieel and v.douane and v.terminal_status and v.inspectie_vrij):
            return False
    return True


def stuur_prenotificaties(db: Session, rit_id: int, gebruiker: str, bevestig_wijziging: bool = False) -> list[Uitkomst]:
    if noodstop_aan(db):
        raise BerichtFout("De noodstop staat aan. Automatische berichten zijn uit.")
    rit = db.get(m.Rit, rit_id)
    if not rit or not rit.gepland_start:
        raise BerichtFout("Deze rit heeft nog geen begintijd. Plan de rit eerst in.")
    if rit.status not in ("Gepland", "Geaccepteerd"):
        raise BerichtFout(f"Een pre-notificatie kan alleen voor een geplande rit (nu: '{rit.status}').")
    d = rit.gepland_start.astimezone(NL).date()
    ctx = laad_dag(db, d)
    rit = next(r for r in ctx.ritten if r.id == rit_id)
    uit: list[Uitkomst] = []
    for bezoek in terminal_bezoeken(ctx, rit):
        tr = ctx.terminalregels.get(bezoek.locatie.id)
        if not tr or tr.slotsysteem == "geen":
            continue
        uit.append(_een_terminal(db, ctx, rit, bezoek, tr, gebruiker, bevestig_wijziging))
    if not uit:
        uit.append(Uitkomst("-", "Deze rit gaat niet langs een terminal met pre-notificatie.", False))
    return uit


def _een_terminal(db, ctx, rit, bezoek, tr, gebruiker, bevestig_wijziging) -> Uitkomst:
    naam = bezoek.locatie.naam
    handling = "ophalen" if bezoek.locatie.id == rit.van_locatie_id else "brengen"
    bestaand = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id, m.Slot.terminal_id == bezoek.locatie.id,
                                              m.Slot.status.in_(ACTIEF)).order_by(m.Slot.id.desc()))
    label = (bestaand.label if bestaand and bestaand.label else None) or f"PN-{rit.id}-{bezoek.locatie.id}"
    sleutel = f"pn:{label}:{bezoek.aankomst.isoformat()}"
    eerder = db.scalar(select(m.Bericht).where(m.Bericht.sleutel == sleutel))
    if eerder:
        return Uitkomst(naam, f"Al verstuurd met deze ETA (label {label}). Er is niets dubbel gestuurd.", False,
                        eerder.code)
    gw = gateway()
    if bestaand and bestaand.status in ("Toegekend", "Gewijzigd"):
        if not bevestig_wijziging:
            raise BerichtFout(f"Er is al een slot bij {naam} ({bestaand.slot_van.astimezone(NL):%H:%M}-"
                              f"{bestaand.slot_tot.astimezone(NL):%H:%M}). Een andere ETA betekent annuleren en "
                              "opnieuw sturen met hetzelfde label. Bevestig dat eerst.")
        if klok().nu() >= bestaand.slot_van:
            bedrag = tr.no_show_kosten_cent or 0
            geheven = no_show_geheven(ctx.instellingen, tr, ctx.datum)
            log_actie(db, "no-show", tabel="slot", record_id=bestaand.id,
                      na={"label": label, "bedrag_cent": bedrag if geheven else 0,
                          "tekst": "Wijziging na begin van het slot telt als no-show"
                                   + ("" if geheven else " (kosten nog niet geheven)")})
        antwoord = gw.annuleer(label)
        db.add(m.Bericht(sleutel=f"annuleer:{label}:{bestaand.id}", soort="annulering", rit_id=rit.id,
                         slot_id=bestaand.id, label=label, verzoek=json.dumps({"label": label}),
                         antwoord=antwoord.tekst, code=antwoord.code, gebruiker=gebruiker))
        zet_status(bestaand, "slot", "Geannuleerd")
    elif bestaand:  # Aangevraagd zonder antwoord: vervangen
        zet_status(bestaand, "slot", "Geannuleerd")
    bezet: dict = {}
    for s in db.scalars(select(m.Slot).where(m.Slot.terminal_id == bezoek.locatie.id,
                                             m.Slot.status.in_(("Toegekend", "Gewijzigd")))):
        if s.slot_van:
            bezet[s.slot_van.astimezone(NL)] = bezet.get(s.slot_van.astimezone(NL), 0) + 1
    pn = PreNotificatie(label, bezoek.locatie.terminalcode or bezoek.locatie.naam, handling,
                        [c.nummer for c in rit.order.containers], bezoek.aankomst, _release_vrij(ctx, rit),
                        tr.slotlengte_min or 120, tr.capaciteit_per_slot, bezet)
    antwoord = gw.stuur_prenotificatie(pn)
    slot = m.Slot(rit_id=rit.id, terminal_id=bezoek.locatie.id, handlingtype=handling, label=label,
                  status="Aangevraagd")
    db.add(slot)
    db.flush()
    if antwoord.toegekend:
        slot.slot_van, slot.slot_tot, slot.tar = antwoord.slot_van, antwoord.slot_tot, antwoord.tar
        zet_status(slot, "slot", "Toegekend")
    else:
        slot.afwijzingscode = antwoord.code
        zet_status(slot, "slot", "Geweigerd")
    db.add(m.Bericht(sleutel=sleutel, soort="prenotificatie", rit_id=rit.id, slot_id=slot.id, label=label,
                     verzoek=json.dumps({"label": label, "terminal": pn.terminalcode, "handling": handling,
                                         "containers": pn.containernummers, "eta": pn.eta.isoformat()}),
                     antwoord=antwoord.tekst, code=antwoord.code, gebruiker=gebruiker))
    log_actie(db, "pre-notificatie", tabel="slot", record_id=slot.id,
              na={"label": label, "code": antwoord.code, "terminal": naam, "simulator": True})
    tekst = f"{antwoord.code}: {antwoord.tekst}"
    if antwoord.toegekend:
        van, tot = antwoord.slot_van.astimezone(NL), antwoord.slot_tot.astimezone(NL)
        tekst += f" Slot {van:%H:%M}-{tot:%H:%M}, {antwoord.tar}."
    return Uitkomst(naam, tekst, True, antwoord.code)


def _job(db: Session, payload: dict, job) -> dict:
    uit = stuur_prenotificaties(db, int(payload["rit_id"]), payload.get("gebruiker", "systeem"),
                                bool(payload.get("bevestig")))
    return {"teksten": [f"{u.terminal}: {u.tekst}" for u in uit]}


handler("prenotificatie")(_job)
