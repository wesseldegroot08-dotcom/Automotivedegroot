"""Het nieuwe ontwerp: plannen op de chauffeur, rustig planbord, wagenpark koppelen, startscherm met akkoord."""

from datetime import date

from sqlalchemy import select

from app import models as m
from app.jobs import voer_uit
from app.planner.automatisch import akkoord, laatste_voorstel, stand_van_de_dag, zorg_voor_plan
from app.planner.context import laad_dag
from app.ports.clock import NL
from tests.conftest import csrf_van, inloggen

MORGEN = date(2026, 11, 26)


def chauffeur(db, naam: str) -> m.Chauffeur:
    return db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == naam))


def trekker(db, nr: str) -> m.Trekker:
    return db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == nr))


def rit(db, ref: str) -> m.Rit:
    return db.scalar(select(m.Rit).join(m.Order).where(m.Order.klantreferentie == ref))


# ------------------------------------------------------------------ plannen op de chauffeur


def test_plannen_op_chauffeur_neemt_eigen_trekker_en_trailer_mee(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    r = rit(db, "DEMO-1002")
    bas = chauffeur(db, "Bas")
    res = client.post(f"/planbord/rit/{r.id}/toewijzen", data={
        "datum": MORGEN.isoformat(), "start": "12:00", "chauffeur_id": bas.id, "csrf": token})
    assert res.status_code == 200 and "Opgeslagen" in res.text
    db.expire_all()
    r = db.get(m.Rit, r.id)
    t13 = trekker(db, "13")
    assert r.chauffeur_id == bas.id and r.trekker_id == t13.id and r.chassis_id == t13.vaste_chassis_id
    assert r.gepland_start.astimezone(NL).hour == 12


def test_chauffeur_zonder_trekker_geeft_duidelijke_melding(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    r = rit(db, "DEMO-1002")
    res = client.post(f"/planbord/rit/{r.id}/toewijzen", data={
        "datum": MORGEN.isoformat(), "start": "12:00", "chauffeur_id": chauffeur(db, "Gijs").id, "csrf": token})
    assert "Gijs heeft geen trekker" in res.text
    db.expire_all()
    assert db.get(m.Rit, r.id).chauffeur_id is None


def test_slepen_naar_chauffeur(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    r = rit(db, "DEMO-1002")
    celine = chauffeur(db, "Celine")
    client.post(f"/planbord/rit/{r.id}/verplaats", data={
        "datum": MORGEN.isoformat(), "rij_id": celine.id, "minuten": "480", "csrf": token})
    db.expire_all()
    r = db.get(m.Rit, r.id)
    assert r.chauffeur_id == celine.id and r.trekker_id == trekker(db, "15").id


def test_andere_trekker_voor_een_dag(client, db):
    inloggen(client)
    token = csrf_van(client, "/wagenpark/koppelen")
    bas, t11 = chauffeur(db, "Bas"), trekker(db, "11")
    res = client.post("/wagenpark/inzet", data={"datum": MORGEN.isoformat(), "chauffeur_id": bas.id,
                                                 "trekker_id": t11.id, "csrf": token})
    assert res.status_code == 200 and "Bas rijdt op 26-11 trekker 11" in res.text
    assert laad_dag(db, MORGEN).trekker_van(bas) == t11.id
    assert laad_dag(db, date(2026, 11, 27)).trekker_van(bas) == trekker(db, "13").id


def test_koppelen_trekker_en_trailer(client, db):
    inloggen(client)
    token = csrf_van(client, "/wagenpark/koppelen")
    gijs, t16 = chauffeur(db, "Gijs"), trekker(db, "16")
    trailer = db.scalar(select(m.Chassis).where(m.Chassis.nummer == "C-205"))
    res = client.post(f"/wagenpark/koppelen/{gijs.id}", data={"trekker_id": t16.id, "trailer_id": trailer.id,
                                                              "csrf": token})
    assert "trekker 16 met trailer C-205" in res.text
    db.expire_all()
    assert chauffeur(db, "Gijs").voorkeur_trekker_id == t16.id and trekker(db, "16").vaste_chassis_id == trailer.id


def test_trekker_van_een_ander_wordt_geweigerd(client, db):
    inloggen(client)
    token = csrf_van(client, "/wagenpark/koppelen")
    res = client.post(f"/wagenpark/koppelen/{chauffeur(db, 'Gijs').id}",
                      data={"trekker_id": trekker(db, "13").id, "csrf": token})
    assert "al van Bas" in res.text


# ------------------------------------------------------------------ rustig planbord


def test_planbord_toont_alleen_chauffeurs(client, db):
    inloggen(client)
    html = client.get(f"/planbord?datum={MORGEN}").text
    for naam in ("Arend", "Bas", "Celine", "Dirk", "Esra"):
        assert naam in html
    assert "afwezig (Verlof)" in html  # Fenna
    assert "geen trekker" in html  # Gijs en Hamza
    assert "Maak voorstel" not in html and "Publiceer planning" not in html
    assert "01-DTB-1" not in html  # geen kentekens op het bord


# ------------------------------------------------------------------ startscherm: plan maakt zichzelf


def test_plan_maakt_zichzelf_en_akkoord_verstuurt(db):
    job = zorg_voor_plan(db, MORGEN, "planner")
    assert job is not None
    assert zorg_voor_plan(db, MORGEN, "planner").id == job.id  # tweede keer: zelfde taak, niet opnieuw
    voer_uit(job.id)
    db.expire_all()
    s = stand_van_de_dag(db, MORGEN)
    assert s.fase == "klaar_voor_akkoord" and s.gepland > 0
    assert zorg_voor_plan(db, MORGEN, "planner") is None  # plan is actueel
    assert not any(r.gepubliceerd for r in laad_dag(db, MORGEN).ritten)  # nog niets verstuurd

    uit = akkoord(db, laatste_voorstel(db, MORGEN), "planner")
    db.expire_all()
    assert uit.verstuurd > 0
    assert sum(1 for r in laad_dag(db, MORGEN).ritten if r.gepubliceerd) == uit.verstuurd
    assert db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "akkoord en versturen"))
    assert stand_van_de_dag(db, MORGEN).fase in ("verstuurd", "deels")


def test_noodstop_geen_automatisch_plan(db):
    db.get(m.Instelling, "noodstop").waarde = "aan"
    db.commit()
    assert zorg_voor_plan(db, MORGEN, "planner") is None
    assert stand_van_de_dag(db, MORGEN).fase == "handmatig"


def test_startscherm_opent(client, db):
    inloggen(client)
    html = client.get("/").text
    assert "Moet jij naar kijken" in html


def test_planbord_toont_plan_als_concept_voor_akkoord(client, db):
    job = zorg_voor_plan(db, MORGEN, "planner")
    voer_uit(job.id)
    inloggen(client)
    html = client.get(f"/planbord?datum={MORGEN}").text
    assert "Dit is het automatische plan" in html and "tl-blok niveau-ok concept" in html
    assert not any(r.gepubliceerd for r in laad_dag(db, MORGEN).ritten)
