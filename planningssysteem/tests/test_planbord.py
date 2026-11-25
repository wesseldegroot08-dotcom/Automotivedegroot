"""Testplan 9 t/m 13: slot, LFD en kosten, dubbele boeking, statussen. Plus override en publiceren."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import select

from app import models as m
from app.planner.context import laad_dag
from app.planner.ritten import plan_rit
from app.ports.clock import NL, VasteKlok, nl_tijd, zet_klok
from app.rules.basis import HARD, OK, WAARSCHUWING
from app.rules.kosten import DDBand, dd_kosten
from app.rules.planning import binnen_slot, open_harde_regels, regel_lfd, regel_slot, toets_rit
from app.statussen import OngeldigeOvergang, zet_status
from app.web.planbord import maak_override
from tests.conftest import csrf_van, inloggen

MORGEN = date(2026, 11, 26)


def rit_van(ctx, ref: str) -> m.Rit:
    return next(r for r in ctx.ritten if r.order.klantreferentie == ref)


def trekker(db, nr: str) -> m.Trekker:
    return db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == nr))


def chauffeur(db, naam: str) -> m.Chauffeur:
    return db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == naam))


# ------------------------------------------------------------------ testplan 9: slot


def test_binnen_slot_met_tolerantie():
    van, tot = datetime(2026, 11, 26, 6, 0, tzinfo=NL), datetime(2026, 11, 26, 8, 0, tzinfo=NL)
    assert binnen_slot(datetime(2026, 11, 26, 8, 30, tzinfo=NL), van, tot, 30)
    assert binnen_slot(datetime(2026, 11, 26, 5, 30, tzinfo=NL), van, tot, 30)
    assert not binnen_slot(datetime(2026, 11, 26, 8, 31, tzinfo=NL), van, tot, 30)
    assert not binnen_slot(datetime(2026, 11, 26, 5, 29, tzinfo=NL), van, tot, 30)


def test_aankomst_binnen_ect_slot_van_2_uur_slaagt_buiten_faalt(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1007")  # slot 06:00-08:00 bij ECT Euromax, tolerantie 30 min
    rit.gepland_start = nl_tijd(MORGEN, 8, 20)
    slot = [u for u in regel_slot(ctx, rit) if u.nr == 9]
    assert slot and slot[0].niveau == OK, slot
    rit.gepland_start = nl_tijd(MORGEN, 8, 45)
    slot = [u for u in regel_slot(ctx, rit) if u.nr == 9]
    assert slot[0].niveau == HARD
    assert "past niet in slot 06:00-08:00" in slot[0].uitleg


def test_geen_slot_bij_terminal_is_hard(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1004")  # RWG, geen slot
    assert any(u.nr == 9 and u.niveau == HARD and "Geen slot" in u.uitleg for u in regel_slot(ctx, rit))


def test_wijziging_na_begin_slot_geeft_no_show_waarschuwing(db):
    zet_klok(VasteKlok(datetime(2026, 11, 26, 6, 30, tzinfo=NL)))
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1007")
    rit.gepland_start = nl_tijd(MORGEN, 7, 0)
    waarschuwing = [u for u in regel_slot(ctx, rit) if u.niveau == WAARSCHUWING]
    assert waarschuwing and "no-show" in waarschuwing[0].uitleg
    assert "€ 100,00" in waarschuwing[0].uitleg


def test_voor_begin_slot_geen_no_show_waarschuwing(db):
    ctx = laad_dag(db, MORGEN)  # klok: 25-11 10:00
    rit = rit_van(ctx, "DEMO-1007")
    rit.gepland_start = nl_tijd(MORGEN, 7, 0)
    assert not any("no-show" in u.uitleg for u in regel_slot(ctx, rit))


# ------------------------------------------------------------------ testplan 10: LFD en kosten


def test_demurrage_exact_bedrag_met_4_vrije_dagen():
    # Maersk 20ft DC (voorbeeld): 4 vrije dagen, dag 5-8 € 85, dag 9-13 € 130, dag 14+ € 190
    banden = [DDBand(4, 5, 8, 8500), DDBand(4, 9, 13, 13000), DDBand(4, 14, None, 19000)]
    begin = date(2026, 11, 1)
    assert dd_kosten(banden, begin, date(2026, 11, 4)) == (0, 0)  # dag 4: nog vrij
    assert dd_kosten(banden, begin, date(2026, 11, 5)) == (8500, 1)
    # dag 10: 4 x 85 + 2 x 130 = 600 euro
    assert dd_kosten(banden, begin, date(2026, 11, 10)) == (4 * 8500 + 2 * 13000, 6)
    # dag 15: 4 x 85 + 5 x 130 + 2 x 190 = 1370 euro
    assert dd_kosten(banden, begin, date(2026, 11, 15)) == (137000, 11)


def test_lfd_waarschuwing_toont_het_bedrag(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1005")  # Maersk 20 DC, ontlaad 23-11 (dag 1), LFD 26-11 (dag 4)
    rit.gepland_start = nl_tijd(MORGEN + timedelta(days=2), 10)  # 28-11 = dag 6
    u = regel_lfd(ctx, rit)
    assert u.niveau == WAARSCHUWING
    assert u.bedrag_cent == 2 * 8500
    assert "€ 170,00" in u.uitleg


def test_lfd_op_tijd_noemt_kosten_van_een_dag_later(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1005")
    rit.gepland_start = nl_tijd(MORGEN, 10)
    u = regel_lfd(ctx, rit)
    assert u.niveau == OK
    assert "een dag later kost € 85,00" in u.uitleg


# ------------------------------------------------------------------ testplan 11: dubbele boeking


def test_dubbele_boeking_trekker_en_chauffeur_is_hard(db):
    ctx = laad_dag(db, MORGEN)
    bezet = rit_van(ctx, "DEMO-1004")  # 06:00 trekker 15 met Celine
    rit = rit_van(ctx, "DEMO-1002")
    plan_rit(ctx, rit, bezet.gepland_start + timedelta(minutes=30), bezet.trekker_id, bezet.chassis_id,
             bezet.chauffeur_id)
    u = next(x for x in toets_rit(ctx, rit).uitslagen if x.nr == 1)
    assert u.niveau == HARD
    assert "trekker staat ook op rit" in u.uitleg and "chauffeur staat ook op rit" in u.uitleg


def test_afwezige_chauffeur_is_hard(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1002")
    t = trekker(db, "11")
    plan_rit(ctx, rit, nl_tijd(MORGEN, 12), t.id, t.vaste_chassis_id, chauffeur(db, "Fenna").id)
    u = next(x for x in toets_rit(ctx, rit).uitslagen if x.nr == 1)
    assert u.niveau == HARD and "niet beschikbaar" in u.uitleg


# ------------------------------------------------------------------ testplan 12: statussen


def test_ongeldige_statusovergang_geeft_fout_en_verandert_niets(db):
    rit = db.scalar(select(m.Rit).where(m.Rit.status == "Concept"))
    with pytest.raises(OngeldigeOvergang, match="kan niet van 'Concept' naar 'Afgerond'"):
        zet_status(rit, "rit", "Afgerond")
    assert rit.status == "Concept"
    with pytest.raises(OngeldigeOvergang, match="geen bestaande status"):
        zet_status(rit, "rit", "Verzonnen")
    assert rit.status == "Concept"


def test_ongeldige_status_via_planbord_wordt_niet_opgeslagen(client, db):
    inloggen(client)
    rit = db.scalar(select(m.Rit).where(m.Rit.status == "Concept"))
    token = csrf_van(client, "/planbord")
    r = client.post(f"/planbord/rit/{rit.id}/status", data={"status": "Afgerond", "csrf": token,
                                                            "datum": MORGEN.isoformat()})
    assert r.status_code == 200
    assert "kan niet van" in r.text
    db.expire_all()
    assert db.get(m.Rit, rit.id).status == "Concept"


def test_plannen_zet_rit_en_order_op_gepland_en_terug(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1002")
    t = trekker(db, "11")
    plan_rit(ctx, rit, nl_tijd(MORGEN, 12), t.id, t.vaste_chassis_id, chauffeur(db, "Bas").id)
    assert rit.status == "Gepland" and rit.order.status == "Gepland"
    plan_rit(ctx, rit, nl_tijd(MORGEN, 12), t.id, t.vaste_chassis_id, None)
    assert rit.status == "Concept" and rit.order.status == "Nieuw"


def test_gestarte_rit_staat_vast(db):
    ctx = laad_dag(db, MORGEN)
    rit = rit_van(ctx, "DEMO-1004")
    rit.vastheid = "gestart"
    with pytest.raises(ValueError, match="gestart"):
        plan_rit(ctx, rit, None, None, None, None)


# ------------------------------------------------------------------ override en publiceren


def test_override_zonder_reden_faalt(db):
    rit = db.get(m.Rit, 1)
    with pytest.raises(ValueError, match="redencode"):
        maak_override(db, rit, 9, HARD, "Geen slot", "", "klant belt", "planner")
    with pytest.raises(ValueError, match="waarom"):
        maak_override(db, rit, 9, HARD, "Geen slot", "KLANT", "  ", "planner")


def test_override_met_reden_komt_in_logboek(db):
    rit = db.get(m.Rit, 1)
    maak_override(db, rit, 9, HARD, "Geen slot", "GECONTROLEERD", "Slot telefonisch bevestigd", "planner")
    db.commit()
    log = db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "override"))
    assert log and log.reden_code == "GECONTROLEERD" and "telefonisch" in log.reden


def test_override_zonder_reden_via_planbord(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    r = client.post("/planbord/rit/1/override", data={"regel_nr": "9", "niveau": "hard", "uitleg": "x",
                                                      "reden_code": "KLANT", "reden": "", "csrf": token,
                                                      "datum": MORGEN.isoformat()})
    assert "Override niet opgeslagen" in r.text
    assert db.scalar(select(m.Override)) is None


def test_publiceren_geblokkeerd_door_harde_regel_en_daarna_met_override(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    r = client.post("/planbord/publiceren", data={"datum": MORGEN.isoformat(), "csrf": token})
    assert "Niet gepubliceerd" in r.text
    db.expire_all()
    assert not any(r.gepubliceerd for r in db.scalars(select(m.Rit)))

    ctx = laad_dag(db, MORGEN)
    for rit in ctx.ritten:
        t = toets_rit(ctx, rit)
        if t.toegewezen:
            for u in open_harde_regels(ctx, t):
                maak_override(db, rit, u.nr, u.niveau, u.uitleg, "GECONTROLEERD", "Getest in de demo", "planner")
    db.commit()
    r = client.post("/planbord/publiceren", data={"datum": MORGEN.isoformat(), "csrf": token})
    assert "Planning van 26-11-2026 gepubliceerd" in r.text
    db.expire_all()
    assert sum(1 for r in db.scalars(select(m.Rit)) if r.gepubliceerd) == 2
    assert db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "publiceren"))


# ------------------------------------------------------------------ planbord in de browser


def test_toewijzen_via_formulier(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    rit = db.scalar(select(m.Rit).join(m.Order).where(m.Order.klantreferentie == "DEMO-1002"))
    t = trekker(db, "11")
    r = client.post(f"/planbord/rit/{rit.id}/toewijzen", data={
        "datum": MORGEN.isoformat(), "start": "12:00", "trekker_id": t.id, "chassis_id": t.vaste_chassis_id,
        "chauffeur_id": chauffeur(db, "Bas").id, "csrf": token})
    assert r.status_code == 200 and "Opgeslagen en gecontroleerd" in r.text
    db.expire_all()
    rit = db.get(m.Rit, rit.id)
    assert rit.status == "Gepland" and rit.gepland_start.astimezone(NL).hour == 12


def test_slepen_rondt_af_op_kwartier(client, db):
    inloggen(client)
    token = csrf_van(client, "/planbord")
    rit = db.scalar(select(m.Rit).join(m.Order).where(m.Order.klantreferentie == "DEMO-1002"))
    t = trekker(db, "11")
    r = client.post(f"/planbord/rit/{rit.id}/verplaats", data={
        "datum": MORGEN.isoformat(), "rij_id": t.id, "minuten": "487", "per": "trekker", "csrf": token})
    assert r.status_code == 200
    db.expire_all()
    rit = db.get(m.Rit, rit.id)
    start = rit.gepland_start.astimezone(NL)
    assert (start.hour, start.minute) == (12, 0)  # 04:00 + 487 min -> 480 min = 12:00
    assert rit.trekker_id == t.id and rit.chassis_id == t.vaste_chassis_id


def test_zonder_csrf_wordt_geweigerd(client, db):
    inloggen(client)
    r = client.post("/planbord/publiceren", data={"datum": MORGEN.isoformat()})
    assert r.status_code == 403


def test_chauffeur_mag_niet_op_planbord(client):
    inloggen(client, "chauffeur")
    r = client.get("/planbord", follow_redirects=False)
    assert r.status_code in (303, 403)
