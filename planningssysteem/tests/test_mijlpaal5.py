"""Testplan 16 (noodstop), 18 (order inlezen), Portbase-simulator, chauffeurspagina, export en factuur."""

import json
from datetime import date, datetime

from sqlalchemy import select

from app import models as m
from app.berichten import BerichtFout, stuur_prenotificaties
from app.orders_inlezen import keur_goed, lees_in
from app.planner.context import laad_dag
from app.planner.ritten import plan_rit
from app.ports.clock import NL, VasteKlok, nl_tijd, zet_klok
from tests.conftest import csrf_van, inloggen

MORGEN = date(2026, 11, 26)


def _plan(db, ref, uur, trekker="11", chauffeur="Bas"):
    ctx = laad_dag(db, MORGEN)
    rit = next(r for r in ctx.ritten if r.order.klantreferentie == ref)
    t = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == trekker))
    c = db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == chauffeur))
    plan_rit(ctx, rit, nl_tijd(MORGEN, uur), t.id, t.vaste_chassis_id, c.id)
    db.commit()
    return rit


# ------------------------------------------------------------------ Portbase-simulator


def test_prenotificatie_geeft_slot_en_tar_uit_de_eta(db):
    rit = _plan(db, "DEMO-1001", 9)  # ophalen bij ECT Delta om 09:00, ECT-slots van 2 uur
    uit = stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    assert uit[0].code == "COR" and uit[0].nieuw
    slot = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id))
    assert slot.status == "Toegekend" and slot.tar.startswith("TAR-SIM-")
    assert slot.slot_van.astimezone(NL).hour == 8 and slot.slot_tot.astimezone(NL).hour == 10


def test_twee_keer_sturen_geeft_geen_dubbel_slot(db):
    rit = _plan(db, "DEMO-1001", 9)
    stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    tweede = stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    assert not tweede[0].nieuw
    assert len(db.scalars(select(m.Slot).where(m.Slot.rit_id == rit.id)).all()) == 1
    assert len(db.scalars(select(m.Bericht).where(m.Bericht.soort == "prenotificatie")).all()) == 1


def test_andere_eta_alleen_met_akkoord_en_zelfde_label(db):
    rit = _plan(db, "DEMO-1001", 9)
    stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    label = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id)).label
    _plan(db, "DEMO-1001", 12)
    try:
        stuur_prenotificaties(db, rit.id, "planner")
        raise AssertionError("had moeten weigeren")
    except BerichtFout as e:
        assert "annuleren" in str(e)
    db.rollback()
    stuur_prenotificaties(db, rit.id, "planner", bevestig_wijziging=True)
    db.commit()
    slots = db.scalars(select(m.Slot).where(m.Slot.rit_id == rit.id).order_by(m.Slot.id)).all()
    assert [s.status for s in slots] == ["Geannuleerd", "Toegekend"]
    assert slots[0].label == slots[1].label == label
    assert slots[1].slot_van.astimezone(NL).hour == 12


def test_wijzigen_na_begin_slot_is_no_show_in_logboek(db):
    rit = _plan(db, "DEMO-1001", 9)
    stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    zet_klok(VasteKlok(datetime(2026, 11, 26, 8, 30, tzinfo=NL)))
    _plan(db, "DEMO-1001", 12)
    stuur_prenotificaties(db, rit.id, "planner", bevestig_wijziging=True)
    db.commit()
    log = db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "no-show"))
    assert log and "nog niet geheven" in log.na


def test_release_niet_vrij_geeft_blt(db):
    rit = _plan(db, "DEMO-1023", 9)
    uit = stuur_prenotificaties(db, rit.id, "planner")
    db.commit()
    assert uit[0].code == "BLT"
    assert db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id)).status == "Geweigerd"


# ------------------------------------------------------------------ testplan 16: noodstop


def test_noodstop_alleen_admin_en_zet_berichten_uit(client, db):
    inloggen(client, "planner")
    token = csrf_van(client, "/instellingen")
    assert client.post("/noodstop", data={"csrf": token, "stand": "aan"}).status_code == 403
    client.get("/logout")
    inloggen(client, "admin")
    token = csrf_van(client, "/instellingen")
    r = client.post("/noodstop", data={"csrf": token, "stand": "aan", "reden": "test"})
    assert "De noodstop staat AAN" in r.text
    db.expire_all()
    assert db.get(m.Instelling, "noodstop").waarde == "aan"
    assert db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "noodstop aan"))
    rit = _plan(db, "DEMO-1001", 9)
    try:
        stuur_prenotificaties(db, rit.id, "admin")
        raise AssertionError("berichten hadden uit moeten staan")
    except BerichtFout as e:
        assert "noodstop" in str(e).lower()
    pb = client.get("/planbord")
    assert pb.status_code == 200 and "Noodstop staat aan" in pb.text
    assert "Maak voorstel voor deze dag" not in pb.text
    assert "Stuur pre-notificaties" not in pb.text


# ------------------------------------------------------------------ testplan 18: order inlezen

TEKST = """Graag ophalen bij ECT Euromax: container CSQU3054383 (40ft HC), VGM 21.500 kg.
Onze ref: ALFA-7781. B/L nummer MAEU12345678.
Leveren bij Alfa DC Waalwijk op 27-11-2026 tussen 09:00 - 13:00. Groet, Alfa Logistiek"""


def test_geldige_tekst_wordt_order_concept(db):
    c = lees_in(db, TEKST, "planner")
    v = json.loads(c.velden)
    assert v["containernummer"] == "CSQU3054383"
    assert v["klantreferentie"] == "ALFA-7781"
    assert v["boeking_bl"] == "MAEU12345678"
    assert (v["maat"], v["container_type"], v["vgm_kg"]) == ("40", "HC", "21500")
    assert (v["datum"], v["venster_van"], v["venster_tot"]) == ("2026-11-27", "09:00", "13:00")
    assert v["type"] == "import" and v.get("terminal_id") and v.get("klantlocatie_id") and v.get("klant_id")
    assert db.scalar(select(m.Order).where(m.Order.klantreferentie == "ALFA-7781")) is None  # nog geen order
    # de rederij staat niet in de mail: een mens moet die kiezen
    assert c.status == "Te controleren"
    v["rederij_id"] = str(db.scalar(select(m.Rederij)).id)
    o = keur_goed(db, c, v, "planner")
    db.commit()
    assert o.containers[0].nummer == "CSQU3054383" and c.status == "Goedgekeurd"
    assert db.scalar(select(m.Rit).where(m.Rit.order_id == o.id))


def test_iso_type_45g1_is_40ft_high_cube(db):
    c = lees_in(db, TEKST.replace("(40ft HC)", "type 45G1"), "planner")
    v = json.loads(c.velden)
    assert (v["maat"], v["container_type"]) == ("40", "HC")


def test_ongeldig_containernummer_geeft_controlefout(db):
    c = lees_in(db, TEKST.replace("CSQU3054383", "CSQU3054384"), "planner")
    meldingen = json.loads(c.meldingen)
    assert c.status == "Te controleren"
    assert any(x["soort"] == "fout" and "Controlecijfer" in x["tekst"] for x in meldingen)
    v = json.loads(c.velden)
    v["rederij_id"] = "1"
    try:
        keur_goed(db, c, v, "planner")
        raise AssertionError("had geweigerd moeten worden")
    except ValueError as e:
        assert "Controlecijfer" in str(e)


def test_dubbele_referentie_wordt_gemeld(db):
    tekst = TEKST.replace("ALFA-7781", "DEMO-1001")
    c = lees_in(db, tekst, "planner")
    assert any("Dubbele order" in x["tekst"] for x in json.loads(c.meldingen))


def test_tijd_in_het_verleden_wordt_gemeld(db):
    c = lees_in(db, TEKST.replace("27-11-2026", "20-11-2026"), "planner")
    assert any("verleden" in x["tekst"] for x in json.loads(c.meldingen))


def test_order_inlezen_via_scherm(client, db):
    inloggen(client)
    token = csrf_van(client, "/orders/inlezen")
    r = client.post("/orders/inlezen", data={"csrf": token, "tekst": TEKST})
    assert r.status_code == 200 and "CSQU3054383" in r.text and "Rederij ontbreekt" in r.text


# ------------------------------------------------------------------ chauffeurspagina


def test_chauffeur_ziet_alleen_eigen_gepubliceerde_rit_en_tijden_worden_bewaard(client, db):
    arend = db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == "Arend"))
    zet_klok(VasteKlok(datetime(2026, 11, 26, 7, 0, tzinfo=NL)))
    rit = _plan(db, "DEMO-1001", 9, trekker="12", chauffeur="Arend")
    inloggen(client, "chauffeur")
    assert "DEMO-1001" not in client.get("/chauffeur").text  # nog niet gepubliceerd
    rit = db.get(m.Rit, rit.id)
    rit.gepubliceerd = True
    db.commit()
    pagina = client.get("/chauffeur")
    assert "DEMO-1001" in pagina.text and "Vertrek" in pagina.text
    token = csrf_van(client, "/chauffeur")
    for actie, uur, minuut in [("vertrek", 8, 0), ("aangekomen", 8, 50), ("bezig", 9, 0), ("klaar", 9, 40)]:
        zet_klok(VasteKlok(datetime(2026, 11, 26, uur, minuut, tzinfo=NL)))
        r = client.post(f"/chauffeur/rit/{rit.id}/{actie}", data={"csrf": token})
        assert r.status_code == 200 and "⛔" not in r.text, r.text[:300]
    db.expire_all()
    rit = db.get(m.Rit, rit.id)
    assert rit.status == "Klaar" and rit.vastheid == "gestart"
    eerste = sorted(rit.stops, key=lambda s: s.volgnr)[0]
    assert eerste.wachttijd_min == 50
    # een andere chauffeur mag niet aan deze rit komen
    rit.chauffeur_id = db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == "Bas")).id
    db.commit()
    assert client.post(f"/chauffeur/rit/{rit.id}/vertrek", data={"csrf": token}).status_code == 403
    _ = arend


# ------------------------------------------------------------------ export en factuur


def test_rooster_export_csv_en_print(client, db):
    inloggen(client)
    r = client.get("/export/rooster?datum=2026-11-26")
    assert r.status_code == 200 and "Celine" in r.text and "DEMO-1004" in r.text
    csv = client.get("/export/rooster.csv?datum=2026-11-26")
    assert csv.status_code == 200 and "text/csv" in csv.headers["content-type"]
    assert "DEMO-1004" in csv.text and "chauffeur;start" in csv.text


def test_factuurconcept_en_csv(client, db):
    inloggen(client)
    r = client.get("/facturen?datum=2026-11-26")
    assert r.status_code == 200 and "concept" in r.text and "DEMO-1004" in r.text
    csv = client.get("/facturen.csv?datum=2026-11-26")
    assert "DEMO-1004" in csv.text


def test_backup_script_maakt_leesbare_kopie(tmp_path, db):
    import sqlite3

    from scripts.backup import maak_backup

    bron = tmp_path / "bron.db"
    with sqlite3.connect(bron) as c:
        c.execute("create table x (a int)")
        c.execute("insert into x values (1)")
    doel = maak_backup(bron, tmp_path / "b", houd=2)
    with sqlite3.connect(doel) as c:
        assert c.execute("select a from x").fetchone()[0] == 1
