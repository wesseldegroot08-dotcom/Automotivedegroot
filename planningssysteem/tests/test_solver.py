"""Testplan 14: de solver en het voorstel (voorstel -> akkoord -> publiceren)."""

from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app import models as m
from app.jobs import plaats_job
from app.planner.context import laad_dag
from app.planner.probleem import EenheidInvoer, Probleem, Taak
from app.planner.ritten import plan_rit
from app.planner.solver import CpSatSolver
from app.planner.voorstel import (
    VoorstelFout,
    _u,
    exacte_controle,
    goedkeuren,
    keuzes_van,
    maak_voorstel,
)
from app.ports.clock import NL, nl_tijd
from tests.conftest import csrf_van, inloggen

DAG = date(2026, 11, 27)  # vrijdag: een kleine dag met 6 orders
KLEINE_DAG = ["DEMO-1001", "DEMO-1002", "DEMO-1009", "DEMO-1012", "DEMO-1015", "DEMO-1016"]


def zet_instelling(db, sleutel, waarde):
    db.get(m.Instelling, sleutel).waarde = waarde


@pytest.fixture
def kleine_dag(db):
    """Verplaats 6 gewone orders (en hun ritten) naar vrijdag 27-11."""
    for ref in KLEINE_DAG:
        o = db.scalar(select(m.Order).where(m.Order.klantreferentie == ref))
        o.venster_van += timedelta(days=1)
        o.venster_tot += timedelta(days=1)
    zet_instelling(db, "solver_tijdlimiet_sec", "10")
    db.commit()
    return db


def ritten_van_dag(db, d=DAG):
    return {r.order.klantreferentie: r for r in laad_dag(db, d).ritten}


def test_kleine_dag_alles_gepland_zonder_harde_regel(kleine_dag):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    assert v.status == "Voorgesteld"
    assert v.ingepland == 6 and v.ongepland == 0, [r.reden for r in v.regels if not r.ingepland]
    assert v.exact_ok
    # zelfstandig nog eens controleren: geen enkele harde regel (ook 3, 7, 11) geschonden
    controle = exacte_controle(DAG, keuzes_van(v))
    assert controle.fouten() == {}
    assert all(r.harde_problemen is None for r in v.regels)


def test_order_die_niet_past_komt_in_lijst_met_reden(kleine_dag):
    db = kleine_dag
    # ADR-tank order erbij, maar de enige chauffeurs met ADR doen vandaag niet mee
    o = db.scalar(select(m.Order).where(m.Order.klantreferentie == "DEMO-1010"))
    o.venster_van += timedelta(days=1)
    o.venster_tot += timedelta(days=1)
    for naam in ("Arend", "Bas"):
        db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == naam)).actief = False
    db.commit()
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    niet = {r.rit.order.klantreferentie: r.reden for r in v.regels if not r.ingepland}
    assert "DEMO-1010" in niet
    assert "ADR" in niet["DEMO-1010"]
    assert "DEMO-1012" in niet  # ADR basis (klasse 9): ook geen chauffeur
    assert v.ingepland >= 4  # de rest gaat gewoon door
    assert len(v.regels) == 7 and v.ingepland + v.ongepland == 7  # niets stil laten vallen
    assert all(reden for reden in niet.values())


def test_solver_crasht_niet_bij_rare_invoer():
    p = Probleem(datum="2026-11-27", standplaats_id=None)
    p.taken = [Taak(1, "x", 1, 2, 30, 60, 50, 30, 600, 500), Taak(2, "y", 1, 2, 30, 60, 50, 30, 0, 1000)]
    p.eenheden = [EenheidInvoer("1-1", 1, 1, "t")]
    p.toegestaan = {2: [("bestaat-niet", 99)]}
    uit = CpSatSolver().los_op(p, 1)
    assert set(uit.ongepland) | set(uit.toewijzingen) == {1, 2}


def test_herbereken_verschuift_toegezegde_en_gestarte_ritten_niet(kleine_dag):
    db = kleine_dag
    ctx = laad_dag(db, DAG)
    per_ref = {r.order.klantreferentie: r for r in ctx.ritten}
    t13 = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == "13"))
    t15 = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == "15"))
    dirk = db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == "Dirk"))
    celine = db.scalar(select(m.Chauffeur).where(m.Chauffeur.pseudoniem == "Celine"))
    toegezegd, gestart = per_ref["DEMO-1015"], per_ref["DEMO-1016"]
    plan_rit(ctx, toegezegd, nl_tijd(DAG, 11, 0), t13.id, t13.vaste_chassis_id, dirk.id)
    toegezegd.vastheid = "toegezegd"
    plan_rit(ctx, gestart, nl_tijd(DAG, 10, 0), t15.id, t15.vaste_chassis_id, celine.id)
    gestart.vastheid = "gestart"
    db.commit()
    voor = {r.id: (r.gepland_start, r.trekker_id, r.chassis_id, r.chauffeur_id) for r in (toegezegd, gestart)}

    for _ in range(2):  # voorstel en daarna "herbereken"
        v = maak_voorstel(db, DAG, "planner")
        db.commit()
        for r in v.regels:
            if r.rit_id in voor:
                assert r.vast
                assert (r.start, r.trekker_id, r.chassis_id, r.chauffeur_id) == voor[r.rit_id]
    goedkeuren(db, v, "planner")
    db.commit()
    db.expire_all()
    for rid, waarden in voor.items():
        rit = db.get(m.Rit, rid)
        assert (rit.gepland_start, rit.trekker_id, rit.chassis_id, rit.chauffeur_id) == waarden


def test_uitleg_bevat_alleen_getallen_uit_de_controle(kleine_dag):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    controle = exacte_controle(DAG, keuzes_van(v))
    for r in v.regels:
        if not r.ingepland:
            continue
        c = controle.per_rit[r.rit_id]
        assert f"Nog {_u(c.rest_rijtijd_min)} rijtijd over" in r.uitleg
        assert c.uitslagen[3][1].rstrip(".") in r.uitleg  # gewicht uit de controle
        assert c.uitslagen[7][1].rstrip(".") in r.uitleg  # rijtijd uit de controle
        assert f"klaar om {c.eind.astimezone(NL).strftime('%H:%M')}" in r.uitleg or c.eind is None
        assert f"Leeg rijden ervoor: {r.lege_min} min ({r.lege_km} km)" in r.uitleg


def test_exacte_rijtijdcontrole_faalt_dan_niet_publiceren(kleine_dag, client):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    goedkeuren(db, v, "planner")
    db.commit()
    # De regel verandert: nog maar 1 uur rijden per dag. Het goedgekeurde voorstel haalt de exacte controle niet.
    for r in db.scalars(select(m.Regel).where(m.Regel.code.in_(["rijtijd.dag", "rijtijd.dag.verlengd"]))):
        r.waarde = 60
    db.commit()
    controle = exacte_controle(DAG, keuzes_van(v))
    assert any("Regel 7" in p for fouten in controle.fouten().values() for p in fouten)

    inloggen(client)
    token = csrf_van(client, "/planbord")
    # alle 'gewone' harde regels (zoals een ontbrekend slot) zijn overruled; regel 7 juist niet
    from app.planner.voorstel import blokkades_voor_publiceren, goedgekeurd_voorstel
    from app.rules.planning import open_harde_regels, toets_dag
    from app.web.planbord import maak_override

    ctx = laad_dag(db, DAG)
    for t in toets_dag(ctx).values():
        for u in open_harde_regels(ctx, t):
            if t.toegewezen:
                maak_override(db, t.rit, u.nr, u.niveau, u.uitleg, "GECONTROLEERD", "slot via portaal", "planner")
    db.commit()
    ctx = laad_dag(db, DAG)
    assert any(u.nr == 7 for _r, u in blokkades_voor_publiceren(ctx, toets_dag(ctx), goedgekeurd_voorstel(db, DAG)))
    r = client.post("/planbord/publiceren", data={"datum": DAG.isoformat(), "csrf": token})
    assert "Niet gepubliceerd" in r.text and "regel 7" in r.text
    db.expire_all()
    assert not any(x.gepubliceerd for x in db.scalars(select(m.Rit)))


def test_goedkeuren_geweigerd_als_het_plan_veranderd_is(kleine_dag):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    o = db.scalar(select(m.Order).where(m.Order.klantreferentie == "DEMO-1015"))
    o.venster_tot += timedelta(hours=1)
    db.commit()
    with pytest.raises(VoorstelFout, match="veranderd"):
        goedkeuren(db, v, "planner")


def test_voorstel_staat_in_logboek_met_invoer_en_regelversie(kleine_dag):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    log = db.scalar(select(m.AuditLog).where(m.AuditLog.actie == "voorstel berekend"))
    assert log and v.regelversie in log.na and "keuzes" in log.na
    assert v.invoer and v.invoer_hash


def test_noodstop_zet_voorstellen_uit_planbord_werkt(client, db):
    zet_instelling(db, "noodstop", "aan")
    db.commit()
    with pytest.raises(VoorstelFout, match="noodstop"):
        maak_voorstel(db, DAG, "planner")
    inloggen(client)
    token = csrf_van(client, "/voorstellen")
    r = client.post("/voorstellen/maken", data={"datum": DAG.isoformat(), "csrf": token})
    assert "Noodstop" in r.text or "noodstop" in r.text
    assert db.scalar(select(m.Job)) is None
    assert client.get("/planbord").status_code == 200


def test_job_is_idempotent(db):
    a = plaats_job(db, "voorstel", {"datum": "2026-11-27"}, "voorstel:test")
    b = plaats_job(db, "voorstel", {"datum": "2026-11-27"}, "voorstel:test")
    assert a.id == b.id
    assert len(db.scalars(select(m.Job)).all()) == 1


def test_voorstel_via_de_app_maken_en_goedkeuren(kleine_dag, client):
    inloggen(client)
    token = csrf_van(client, "/voorstellen")
    r = client.post("/voorstellen/maken", data={"datum": DAG.isoformat(), "csrf": token})
    assert r.status_code == 200
    assert "Voorstel" in r.text and "Kan niet gepland worden" in r.text, r.text[:500]
    v = kleine_dag.scalar(select(m.Voorstel))
    assert v and v.status == "Voorgesteld"
    # dubbel klikken: zelfde invoer = hetzelfde voorstel
    r2 = client.post("/voorstellen/maken", data={"datum": DAG.isoformat(), "csrf": token})
    assert "bestaat al" in r2.text
    assert len(kleine_dag.scalars(select(m.Voorstel)).all()) == 1
    r = client.post(f"/voorstellen/{v.id}/goedkeuren", data={"csrf": token})
    assert "Voorstel goedgekeurd" in r.text
    kleine_dag.expire_all()
    assert kleine_dag.get(m.Voorstel, v.id).status == "Goedgekeurd"
    gepland = [x for x in ritten_van_dag(kleine_dag).values() if x.status == "Gepland"]
    assert len(gepland) == 6


def test_afkeuren_verandert_niets_op_het_planbord(kleine_dag, client):
    db = kleine_dag
    v = maak_voorstel(db, DAG, "planner")
    db.commit()
    inloggen(client)
    token = csrf_van(client, f"/voorstellen/{v.id}")
    r = client.post(f"/voorstellen/{v.id}/afkeuren", data={"csrf": token, "reden": "Klant belt nog"})
    assert "afgekeurd" in r.text
    db.expire_all()
    assert db.get(m.Voorstel, v.id).status == "Afgekeurd"
    assert all(x.gepland_start is None for x in ritten_van_dag(db).values())
