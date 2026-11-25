"""Het plan maakt zichzelf. Jij geeft één keer akkoord.

- zorg_voor_plan: is er voor deze dag nog geen (actueel) voorstel, dan start de solver vanzelf op de achtergrond.
  Zelfde invoer = zelfde taak, dus vaak openen of dubbel klikken rekent niet steeds opnieuw.
- stand_van_de_dag: alles voor het startscherm: hoeveel is gepland en wat moet jij nog doen.
- akkoord: voorstel goedkeuren, aanmelden bij de terminals (simulator) en versturen naar de chauffeurs.
  Ritten met een probleem worden NIET verstuurd; die komen in de lijst 'Moet jij naar kijken'.
"""

import json
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.eenvoudig import kort_reden, regel_zin
from app.jobs import plaats_job
from app.planner.context import laad_dag
from app.planner.voorstel import (
    VoorstelFout,
    blokkades_voor_publiceren,
    goedkeuren,
    huidige_hash,
    noodstop_aan,
    regelversie,
)
from app.rules.planning import toets_dag
from app.statussen import zet_status


@dataclass
class Actiepunt:
    niveau: str  # hard, waarschuwing, info
    titel: str
    wat: str
    link: str | None = None

    @property
    def icoon(self) -> str:
        return {"hard": "⛔", "waarschuwing": "⚠", "info": "ℹ"}.get(self.niveau, "•")


@dataclass
class Stand:
    datum: date
    noodstop: bool
    voorstel: m.Voorstel | None
    job: m.Job | None
    totaal: int = 0
    gepland: int = 0
    verstuurd: int = 0
    fase: str = ""  # rekenen, klaar_voor_akkoord, verstuurd, deels, handmatig, leeg, fout
    acties: list[Actiepunt] = field(default_factory=list)


def laatste_voorstel(db: Session, d: date) -> m.Voorstel | None:
    return db.scalar(select(m.Voorstel).where(m.Voorstel.datum == d).order_by(m.Voorstel.id.desc()))


def _lopende_job(db: Session, d: date) -> m.Job | None:
    for j in db.scalars(select(m.Job).where(m.Job.soort == "voorstel", m.Job.status.in_(["wachtend", "bezig"]))
                        .order_by(m.Job.id.desc())):
        if json.loads(j.payload).get("datum") == d.isoformat():
            return j
    return None


def zorg_voor_plan(db: Session, d: date, gebruiker: str) -> m.Job | None:
    """Start de solver als dat nodig is. Geeft de taak terug die (nog) moet draaien, anders None."""
    if noodstop_aan(db):
        return None
    lopend = _lopende_job(db, d)
    if lopend:
        return lopend
    v = laatste_voorstel(db, d)
    if v and v.status in ("Goedgekeurd", "Gepubliceerd"):
        return None  # na akkoord rekenen we niet vanzelf opnieuw (stabiel rooster); de knop 'Plan opnieuw' kan het
    h = huidige_hash(db, d)
    if v and v.invoer_hash == h:
        return None  # het voorstel is actueel (of al afgekeurd voor precies deze invoer)
    ctx = laad_dag(db, d)
    if not ctx.ritten:
        return None
    job = plaats_job(db, "voorstel", {"datum": d.isoformat(), "gebruiker": f"automatisch ({gebruiker})"},
                     f"voorstel:{d}:{h}:{regelversie(db)}")
    db.commit()
    return job if job.status in ("wachtend", "bezig") else None


def _naam(rit: m.Rit) -> str:
    return f"{rit.order.klantreferentie} · {rit.order.klant.naam.replace(' (demo)', '')}"


def stand_van_de_dag(db: Session, d: date, job: m.Job | None = None) -> Stand:
    v = laatste_voorstel(db, d)
    s = Stand(d, noodstop_aan(db), v, job or _lopende_job(db, d))
    ctx = laad_dag(db, d)
    s.totaal = len(ctx.ritten)
    s.gepland = sum(1 for r in ctx.ritten if r.gepland_start and r.chauffeur_id)
    s.verstuurd = sum(1 for r in ctx.ritten if r.gepubliceerd)
    link = f"/planbord?datum={d}&rit="
    if not ctx.ritten:
        s.fase = "leeg"
        return s
    if s.noodstop:
        s.fase = "handmatig"
    elif s.job:
        s.fase = "rekenen"
    elif v and v.status == "Voorgesteld":
        s.fase = "klaar_voor_akkoord"
        s.gepland = v.ingepland
    elif v and v.status in ("Goedgekeurd", "Gepubliceerd"):
        s.fase = "verstuurd" if s.verstuurd and s.verstuurd >= s.gepland else "deels"
    else:
        s.fase = "fout" if v is None else "handmatig"

    if s.fase == "klaar_voor_akkoord":
        for r in v.regels:
            if not r.ingepland:
                s.acties.append(Actiepunt("hard", _naam(r.rit), kort_reden(r.reden), link + str(r.rit_id)))
            elif r.harde_problemen:
                s.acties.append(Actiepunt("waarschuwing", _naam(r.rit), kort_reden(r.harde_problemen),
                                          link + str(r.rit_id)))
    else:
        toetsen = toets_dag(ctx)
        blok = blokkades_voor_publiceren(ctx, toetsen, v if v and v.status == "Goedgekeurd" else None)
        per_rit: dict[int, list] = {}
        for rit, u in blok:
            per_rit.setdefault(rit.id, []).append(u)
        for rit in ctx.ritten:
            if not (rit.gepland_start and rit.chauffeur_id):
                reden = next((x.reden for x in (v.regels if v else []) if x.rit_id == rit.id and x.reden), None)
                s.acties.append(Actiepunt("hard", _naam(rit), kort_reden(reden) if reden else "Nog niet gepland.",
                                          link + str(rit.id)))
            elif rit.id in per_rit and not rit.gepubliceerd:
                u = per_rit[rit.id][0]
                s.acties.append(Actiepunt("hard", _naam(rit), regel_zin(u.nr, u.uitleg), link + str(rit.id)))
        if v and v.status in ("Goedgekeurd", "Gepubliceerd"):
            nieuw = [r for r in ctx.ritten if r.id not in {x.rit_id for x in v.regels}]
            if nieuw:
                s.acties.insert(0, Actiepunt("info", f"{len(nieuw)} nieuwe order(s) sinds je akkoord",
                                             "Druk op 'Plan opnieuw' om ze mee te nemen.", None))
    # Kosten die eraan komen: laatste gratis dag
    for rit in ctx.ritten:
        for c in rit.order.containers:
            vr = ctx.vrijgave_per_container.get(c.id)
            if vr and vr.lfd <= d and rit.order.type == "import":
                s.acties.append(Actiepunt("waarschuwing", _naam(rit), f"Laatste gratis dag is {vr.lfd:%d-%m}. "
                                          "Later ophalen kost geld (demurrage).", link + str(rit.id)))
    # Chauffeurs zonder trekker of afwezig
    zonder = [c.pseudoniem for c in db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True)))
              if not ctx.is_afwezig(chauffeur_id=c.id) and not ctx.trekker_van(c)]
    if zonder:
        s.acties.append(Actiepunt("info", "Zonder eigen trekker: " + ", ".join(zonder),
                                  "Deze chauffeurs krijgen geen ritten. Koppel een trekker in Wagenpark.",
                                  "/wagenpark/koppelen"))
    afwezig = sorted({db.get(m.Chauffeur, a.chauffeur_id).pseudoniem for a in ctx.afwezig if a.chauffeur_id})
    if afwezig:
        s.acties.append(Actiepunt("info", "Afwezig: " + ", ".join(afwezig), "Krijgen deze dag geen ritten.", None))
    volgorde = {"hard": 0, "waarschuwing": 1, "info": 2}
    s.acties.sort(key=lambda a: volgorde.get(a.niveau, 3))
    return s


@dataclass
class AkkoordUitkomst:
    verstuurd: int = 0
    wacht: int = 0
    aangemeld: int = 0
    meldingen: list[str] = field(default_factory=list)


def akkoord(db: Session, v: m.Voorstel, gebruiker: str) -> AkkoordUitkomst:
    """Eén tik: goedkeuren, aanmelden bij de terminal, versturen wat in orde is."""
    from app.berichten import BerichtFout, stuur_prenotificaties

    uit = AkkoordUitkomst()
    if v.status == "Voorgesteld":
        goedkeuren(db, v, gebruiker)  # doet opnieuw de exacte controle
        db.commit()
    elif v.status != "Goedgekeurd":
        raise VoorstelFout(f"Dit plan staat op '{v.status}'.")
    ctx = laad_dag(db, v.datum)
    for rit in ctx.ritten:
        if rit.status in ("Gepland", "Geaccepteerd") and not db.scalar(
                select(m.Slot).where(m.Slot.rit_id == rit.id, m.Slot.status.in_(["Toegekend", "Gewijzigd"]))):
            if not any(loc.type == "terminal" for loc in (rit.van_locatie, rit.naar_locatie)):
                continue
            try:
                for x in stuur_prenotificaties(db, rit.id, gebruiker):
                    if x.nieuw and x.code == "COR":
                        uit.aangemeld += 1
                    elif x.code and x.code != "COR":
                        uit.meldingen.append(f"{rit.order.klantreferentie}: terminal antwoordt {x.code}.")
                db.commit()
            except BerichtFout as e:
                db.rollback()
                uit.meldingen.append(f"{rit.order.klantreferentie}: {e}")
    ctx = laad_dag(db, v.datum)
    toetsen = toets_dag(ctx)
    blok = {rit.id for rit, _u in blokkades_voor_publiceren(ctx, toetsen, v)}
    for t in toetsen.values():
        if not t.toegewezen:
            continue
        if t.rit.id in blok:
            uit.wacht += 1
        elif not t.rit.gepubliceerd:
            t.rit.gepubliceerd = True
            uit.verstuurd += 1
    if not blok:
        zet_status(v, "voorstel", "Gepubliceerd")
    log_actie(db, "akkoord en versturen", tabel="voorstel", record_id=v.id,
              na={"verstuurd": uit.verstuurd, "wacht": uit.wacht, "aangemeld": uit.aangemeld})
    db.commit()
    return uit
