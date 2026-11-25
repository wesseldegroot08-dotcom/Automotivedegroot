"""Order inlezen: tekst -> order-concept -> controle door een mens -> order.

Harde controles (gewone code): verplichte velden, containernummer (ISO 6346), maat en type, terminal of depot
uit de lijst, tijd niet in het verleden, eindtijd na begintijd, dubbele order (zelfde klant en referentie).
Bij twijfel (meldingen van de uitlezer) gaat het concept naar 'Te controleren'.
"""

import json
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.keuzes import CONTAINER_MATEN, CONTAINER_TYPES, ORDER_TYPES
from app.planner.ritten import maak_rit_voor_order
from app.ports.clock import NL, klok
from app.ports.order_extractor import extractor
from app.rules.iso6346 import controleer_containernummer
from app.statussen import zet_status

VERPLICHT = {"klant_id": "Klant", "klantreferentie": "Referentie", "type": "Soort order",
             "terminal_id": "Terminal of depot", "klantlocatie_id": "Adres klant", "datum": "Datum",
             "venster_van": "Tijd vanaf", "venster_tot": "Tijd tot", "containernummer": "Containernummer",
             "maat": "Maat", "container_type": "Type container", "vgm_kg": "Gewicht (VGM)", "rederij_id": "Rederij"}


def _zoeklijsten(db: Session):
    terminals, locaties, klanten = {}, {}, {}
    for loc in db.scalars(select(m.Locatie).where(m.Locatie.actief.is_(True))):
        if loc.type in ("terminal", "depot"):
            terminals[loc.naam.lower()] = str(loc.id)
            if loc.terminalcode:
                terminals[loc.terminalcode.lower()] = str(loc.id)
            # korte naam zonder toevoeging, bijvoorbeeld "euromax"
            kort = loc.naam.lower().replace("ect ", "").replace("terminals ", "")
            if len(kort) >= 4:
                terminals.setdefault(kort, str(loc.id))
        elif loc.type == "klant":
            locaties[loc.naam.lower().replace(" (demo)", "")] = str(loc.id)
    for k in db.scalars(select(m.Klant).where(m.Klant.actief.is_(True))):
        klanten[k.naam.lower().replace(" (demo)", "")] = str(k.id)
        klanten[k.naam.lower().replace(" bv (demo)", "").replace(" (demo)", "")] = str(k.id)
    return terminals, locaties, klanten


def controles(db: Session, v: dict, concept_id: int | None = None) -> list[dict]:
    """Geeft meldingen: {'soort': 'fout' of 'twijfel', 'veld': ..., 'tekst': ...}. Een fout blokkeert."""
    uit = []

    def fout(veld: str, tekst: str) -> None:
        uit.append({"soort": "fout", "veld": veld, "tekst": tekst})

    for veld, label in VERPLICHT.items():
        if not str(v.get(veld, "")).strip():
            fout(veld, f"{label} ontbreekt.")
    nr = v.get("containernummer", "")
    if nr:
        iso = controleer_containernummer(nr)
        if not iso.geldig:
            fout("containernummer", f"Containernummer: {iso.melding}")
        else:
            v["containernummer"] = iso.genormaliseerd
    if v.get("maat") and v["maat"] not in CONTAINER_MATEN:
        fout("maat", f"Maat '{v['maat']}' bestaat niet. Kies 20, 40 of 45.")
    if v.get("container_type") and v["container_type"] not in CONTAINER_TYPES:
        fout("container_type", f"Type '{v['container_type']}' is onbekend.")
    if v.get("maat") == "45" and v.get("container_type") not in ("HC", None, ""):
        fout("container_type", "Een 45ft is altijd High Cube (HC).")
    if v.get("type") and v["type"] not in ORDER_TYPES:
        fout("type", "Kies import, export, leeg of ITT.")
    if v.get("terminal_id"):
        loc = db.get(m.Locatie, int(v["terminal_id"])) if str(v["terminal_id"]).isdigit() else None
        if not loc or loc.type not in ("terminal", "depot"):
            fout("terminal_id", "Terminal of depot staat niet in de lijst.")
    if v.get("klantlocatie_id"):
        loc = db.get(m.Locatie, int(v["klantlocatie_id"])) if str(v["klantlocatie_id"]).isdigit() else None
        if not loc or loc.type != "klant":
            fout("klantlocatie_id", "Adres van de klant staat niet in de lijst.")
    if v.get("vgm_kg"):
        try:
            kg = int(str(v["vgm_kg"]).replace(".", ""))
            if not 1000 <= kg <= 45000:
                fout("vgm_kg", "Gewicht moet tussen 1.000 en 45.000 kg liggen.")
        except ValueError:
            fout("vgm_kg", "Gewicht moet een getal in kg zijn.")
    try:
        if v.get("datum") and v.get("venster_van"):
            van = _moment(v["datum"], v["venster_van"])
            if van < klok().nu():
                fout("datum", "Deze tijd ligt in het verleden.")
            if v.get("venster_tot") and _moment(v["datum"], v["venster_tot"]) <= van:
                fout("venster_tot", "De eindtijd moet na de begintijd liggen.")
    except ValueError:
        fout("datum", "Datum of tijd klopt niet (gebruik jjjj-mm-dd en uu:mm).")
    if v.get("klant_id") and v.get("klantreferentie"):
        dubbel = db.scalar(select(m.Order).where(m.Order.klant_id == int(v["klant_id"]),
                                                 m.Order.klantreferentie == v["klantreferentie"]))
        if dubbel:
            uit.append({"soort": "fout", "veld": "klantreferentie",
                        "tekst": f"Dubbele order: referentie {v['klantreferentie']} bestaat al (order {dubbel.id})."})
    if not v.get("boeking_bl"):
        uit.append({"soort": "twijfel", "veld": "boeking_bl", "tekst": "Geen boeking- of B/L-nummer gevonden."})
    return uit


def _moment(d: str, t: str) -> datetime:
    return datetime.combine(date.fromisoformat(d), time.fromisoformat(t)).replace(tzinfo=NL)


def lees_in(db: Session, tekst: str, gebruiker: str) -> m.OrderConcept:
    c = m.OrderConcept(bron_tekst=tekst, status="Ontvangen", gebruiker=gebruiker)
    db.add(c)
    db.flush()
    ex = extractor()
    gelezen = ex.lees(tekst, *_zoeklijsten(db))
    if gelezen.velden.get("klantlocatie_id") and not gelezen.velden.get("klant_id"):
        loc = db.get(m.Locatie, int(gelezen.velden["klantlocatie_id"]))
        if loc and loc.klant_id:  # klant afleiden uit het afleveradres
            gelezen.velden["klant_id"] = str(loc.klant_id)
    c.uitlezer = ex.naam
    zet_status(c, "order_concept", "Gelezen")
    meldingen = controles(db, gelezen.velden, c.id) + [{"soort": "twijfel", "veld": "", "tekst": t}
                                                        for t in gelezen.twijfel]
    c.velden = json.dumps(gelezen.velden, ensure_ascii=False)
    c.meldingen = json.dumps(meldingen, ensure_ascii=False)
    if meldingen:
        zet_status(c, "order_concept", "Te controleren")
    log_actie(db, "order ingelezen", tabel="order_concept", record_id=c.id,
              na={"status": c.status, "meldingen": len(meldingen)})
    return c


def bewaar(db: Session, c: m.OrderConcept, velden: dict) -> list[dict]:
    meldingen = controles(db, velden, c.id)
    c.velden = json.dumps(velden, ensure_ascii=False)
    c.meldingen = json.dumps(meldingen, ensure_ascii=False)
    if meldingen and c.status == "Gelezen":
        zet_status(c, "order_concept", "Te controleren")
    return meldingen


def keur_goed(db: Session, c: m.OrderConcept, velden: dict, gebruiker: str) -> m.Order:
    meldingen = bewaar(db, c, velden)
    fouten = [x for x in meldingen if x["soort"] == "fout"]
    if fouten:
        raise ValueError("Nog niet goed: " + " ".join(x["tekst"] for x in fouten))
    v = velden
    terminal = db.get(m.Locatie, int(v["terminal_id"]))
    klantloc = db.get(m.Locatie, int(v["klantlocatie_id"]))
    van, naar = (terminal, klantloc) if v["type"] == "import" else (klantloc, terminal)
    o = m.Order(klant_id=int(v["klant_id"]), klantreferentie=v["klantreferentie"], type=v["type"],
                boeking_bl=v.get("boeking_bl") or "onbekend", venster_van=_moment(v["datum"], v["venster_van"]),
                venster_tot=_moment(v["datum"], v["venster_tot"]), van_locatie_id=van.id, naar_locatie_id=naar.id,
                land_route="NL" if klantloc.land == "NL" else f"{klantloc.land}-intermodaal",
                opmerkingen=f"Ingelezen uit tekst (concept {c.id}).")
    db.add(o)
    db.flush()
    db.add(m.Container(nummer=v["containernummer"], rederij_id=int(v["rederij_id"]), order_id=o.id, maat=v["maat"],
                       type=v["container_type"], vgm_kg=int(str(v["vgm_kg"]).replace(".", ""))))
    db.flush()
    db.refresh(o)
    maak_rit_voor_order(db, o)
    c.order_id = o.id
    zet_status(c, "order_concept", "Goedgekeurd")
    log_actie(db, "order goedgekeurd", tabel="order_concept", record_id=c.id, na={"order_id": o.id})
    return o


def keur_af(db: Session, c: m.OrderConcept) -> None:
    if c.status == "Gelezen":
        zet_status(c, "order_concept", "Te controleren")
    zet_status(c, "order_concept", "Afgekeurd")
