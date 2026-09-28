"""Alles wat met de SQLite-database te maken heeft.

De database is één bestand: data/autos.db. Je kunt hem openen met het
gratis programma "DB Browser for SQLite" als je zelf wilt kijken.
"""

import json
import sqlite3
from datetime import datetime, timedelta

from .instellingen import DATA_MAP

TABELLEN = """
CREATE TABLE IF NOT EXISTS advertenties (
    id                   INTEGER PRIMARY KEY,
    site                 TEXT NOT NULL,
    advertentie_id       TEXT NOT NULL,
    link                 TEXT,
    titel                TEXT,
    beschrijving         TEXT,
    beschrijving_volledig INTEGER DEFAULT 0,
    merk                 TEXT,
    model                TEXT,
    generatie            TEXT,
    uitvoering           TEXT,
    motor                TEXT,
    motor_sleutel        TEXT,
    brandstof            TEXT,
    transmissie          TEXT,
    bouwjaar             INTEGER,
    kilometerstand       INTEGER,
    vraagprijs           INTEGER,
    locatie              TEXT,
    kenteken             TEXT,
    eerst_gevonden       TEXT,
    laatst_gezien        TEXT,
    duplicaat_van        INTEGER,
    rdw_gegevens         TEXT,
    rdw_opgehaald        TEXT,
    melding_bij_prijs    INTEGER,
    UNIQUE (site, advertentie_id)
);
CREATE TABLE IF NOT EXISTS prijswijzigingen (
    id             INTEGER PRIMARY KEY,
    advertentie    INTEGER NOT NULL REFERENCES advertenties(id),
    oude_prijs     INTEGER,
    nieuwe_prijs   INTEGER,
    datum          TEXT
);
CREATE TABLE IF NOT EXISTS site_status (
    site             TEXT PRIMARY KEY,
    geblokkeerd_tot  TEXT,
    reden            TEXT
);
CREATE INDEX IF NOT EXISTS idx_vergelijk ON advertenties (merk, model, generatie, motor_sleutel, transmissie);
CREATE INDEX IF NOT EXISTS idx_kenteken ON advertenties (kenteken);
"""


def nu():
    return datetime.now().isoformat(timespec="seconds")


def verbind(pad=None):
    if pad is None:
        DATA_MAP.mkdir(exist_ok=True)
        pad = DATA_MAP / "autos.db"
    conn = sqlite3.connect(pad, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(TABELLEN)
    return conn


VELDEN = ["link", "titel", "beschrijving", "beschrijving_volledig", "merk", "model", "generatie",
          "uitvoering", "motor", "motor_sleutel", "brandstof", "transmissie", "bouwjaar",
          "kilometerstand", "vraagprijs", "locatie", "kenteken"]


def sla_op(conn, adv, tijd=None):
    """Slaat een advertentie op of werkt hem bij.

    Geeft (id, status) terug. status is "nieuw", "prijs_gewijzigd" of "bekend".
    """
    tijd = tijd or nu()
    bestaand = conn.execute("SELECT * FROM advertenties WHERE site=? AND advertentie_id=?",
                            (adv.site, adv.advertentie_id)).fetchone()
    waarden = {v: getattr(adv, v) for v in VELDEN}
    waarden["beschrijving_volledig"] = int(adv.beschrijving_volledig)

    if bestaand is None:
        kolommen = ["site", "advertentie_id", *VELDEN, "eerst_gevonden", "laatst_gezien"]
        conn.execute(
            f"INSERT INTO advertenties ({','.join(kolommen)}) VALUES ({','.join('?' * len(kolommen))})",
            [adv.site, adv.advertentie_id, *waarden.values(), tijd, tijd])
        pk = conn.execute("SELECT id FROM advertenties WHERE site=? AND advertentie_id=?",
                          (adv.site, adv.advertentie_id)).fetchone()["id"]
        _markeer_duplicaat(conn, pk)
        conn.commit()
        return pk, "nieuw"

    pk = bestaand["id"]
    status = "bekend"
    if adv.vraagprijs and bestaand["vraagprijs"] and adv.vraagprijs != bestaand["vraagprijs"]:
        conn.execute("INSERT INTO prijswijzigingen (advertentie, oude_prijs, nieuwe_prijs, datum) VALUES (?,?,?,?)",
                     (pk, bestaand["vraagprijs"], adv.vraagprijs, tijd))
        status = "prijs_gewijzigd"

    # Een volledige beschrijving (van de advertentiepagina) niet overschrijven
    # met het korte stukje uit de zoeklijst.
    if bestaand["beschrijving_volledig"] and not adv.beschrijving_volledig:
        for veld in ("beschrijving", "beschrijving_volledig"):
            waarden.pop(veld)
    # Lege waarden overschrijven geen bekende waarden.
    waarden = {k: v for k, v in waarden.items() if v is not None}
    zet = ", ".join(f"{k}=?" for k in waarden)
    conn.execute(f"UPDATE advertenties SET {zet}, laatst_gezien=? WHERE id=?", [*waarden.values(), tijd, pk])
    if waarden.get("kenteken") and not bestaand["kenteken"]:
        _markeer_duplicaat(conn, pk)
    conn.commit()
    return pk, status


def _markeer_duplicaat(conn, pk):
    """Is dit dezelfde auto als een eerdere advertentie? Dan markeren we hem als duplicaat.

    Zelfde auto = zelfde kenteken, of zelfde merk/model/bouwjaar/motor met
    precies dezelfde kilometerstand (bijvoorbeeld opnieuw geplaatst).
    """
    a = conn.execute("SELECT * FROM advertenties WHERE id=?", (pk,)).fetchone()
    origineel = None
    if a["kenteken"]:
        origineel = conn.execute(
            "SELECT id FROM advertenties WHERE kenteken=? AND id<>? AND duplicaat_van IS NULL ORDER BY id LIMIT 1",
            (a["kenteken"], pk)).fetchone()
    if origineel is None and a["kilometerstand"] and a["bouwjaar"] and a["motor_sleutel"]:
        origineel = conn.execute(
            """SELECT id FROM advertenties WHERE merk=? AND model=? AND bouwjaar=? AND kilometerstand=?
               AND motor_sleutel=? AND id<>? AND duplicaat_van IS NULL ORDER BY id LIMIT 1""",
            (a["merk"], a["model"], a["bouwjaar"], a["kilometerstand"], a["motor_sleutel"], pk)).fetchone()
    if origineel is not None and origineel["id"] < pk:
        conn.execute("UPDATE advertenties SET duplicaat_van=? WHERE id=?", (origineel["id"], pk))


def haal_auto(conn, pk):
    return conn.execute("SELECT * FROM advertenties WHERE id=?", (pk,)).fetchone()


def is_bekend(conn, site, advertentie_id):
    return conn.execute("SELECT 1 FROM advertenties WHERE site=? AND advertentie_id=?",
                        (site, advertentie_id)).fetchone() is not None


def doelautos(conn, inst, max_dagen=30):
    """Alle auto's die aan jouw zoekcriteria voldoen en recent online stonden."""
    z = inst["zoeken"]
    grens = (datetime.now() - timedelta(days=max_dagen)).isoformat(timespec="seconds")
    rijen = conn.execute(
        """SELECT * FROM advertenties
           WHERE duplicaat_van IS NULL AND laatst_gezien >= ?
             AND vraagprijs BETWEEN ? AND ?""",
        (grens, z["min_prijs"], z["max_prijs"])).fetchall()
    return [r for r in rijen if voldoet_aan_criteria(r, inst)]


def voldoet_aan_criteria(auto, inst):
    z = inst["zoeken"]
    modellen = {(m["merk"].lower(), m["model"].lower()) for m in z["modellen"]}
    if (str(auto["merk"]).lower(), str(auto["model"]).lower()) not in modellen:
        return False
    if auto["vraagprijs"] is None or not (z["min_prijs"] <= auto["vraagprijs"] <= z["max_prijs"]):
        return False
    if auto["bouwjaar"] is not None and auto["bouwjaar"] < z["min_bouwjaar"]:
        return False
    # Onbekende km laten we door: dat wordt een rode vlag, geen reden om te verbergen.
    if auto["kilometerstand"] is not None and auto["kilometerstand"] > z["max_km"]:
        return False
    if auto["brandstof"] is not None and auto["brandstof"] not in z["brandstof"]:
        return False
    if auto["transmissie"] is not None and auto["transmissie"] not in z["transmissie"]:
        return False
    return True


def vergelijkbare_autos(conn, auto, inst):
    """Zoekt auto's die echt te vergelijken zijn met deze auto."""
    v = inst["vergelijken"]
    grens = (datetime.now() - timedelta(days=v["max_leeftijd_dagen"])).isoformat(timespec="seconds")
    return conn.execute(
        """SELECT * FROM advertenties
           WHERE merk=? AND model=? AND generatie=? AND motor_sleutel=? AND transmissie=?
             AND ABS(bouwjaar - ?) <= ? AND ABS(kilometerstand - ?) <= ?
             AND id <> ? AND duplicaat_van IS NULL AND vraagprijs > 0
             AND laatst_gezien >= ?
           ORDER BY vraagprijs""",
        (auto["merk"], auto["model"], auto["generatie"], auto["motor_sleutel"], auto["transmissie"],
         auto["bouwjaar"], v["max_bouwjaar_verschil"], auto["kilometerstand"], v["max_km_verschil"],
         auto["id"], grens)).fetchall()


def prijsgeschiedenis(conn, pk):
    return conn.execute("SELECT * FROM prijswijzigingen WHERE advertentie=? ORDER BY datum", (pk,)).fetchall()


def sla_rdw_op(conn, pk, gegevens):
    conn.execute("UPDATE advertenties SET rdw_gegevens=?, rdw_opgehaald=? WHERE id=?",
                 (json.dumps(gegevens), nu(), pk))
    conn.commit()


def markeer_melding(conn, pk, prijs):
    conn.execute("UPDATE advertenties SET melding_bij_prijs=? WHERE id=?", (prijs, pk))
    conn.commit()


def site_geblokkeerd_tot(conn, site):
    r = conn.execute("SELECT geblokkeerd_tot FROM site_status WHERE site=?", (site,)).fetchone()
    if r and r["geblokkeerd_tot"] and r["geblokkeerd_tot"] > nu():
        return r["geblokkeerd_tot"]
    return None


def blokkeer_site(conn, site, uren, reden):
    tot = (datetime.now() + timedelta(hours=uren)).isoformat(timespec="seconds")
    conn.execute("INSERT INTO site_status (site, geblokkeerd_tot, reden) VALUES (?,?,?) "
                 "ON CONFLICT(site) DO UPDATE SET geblokkeerd_tot=excluded.geblokkeerd_tot, reden=excluded.reden",
                 (site, tot, reden))
    conn.commit()
    return tot


def alle_site_statussen(conn):
    return {r["site"]: dict(r) for r in conn.execute("SELECT * FROM site_status")}


def aantal_advertenties(conn):
    return conn.execute("SELECT COUNT(*) FROM advertenties WHERE duplicaat_van IS NULL").fetchone()[0]
