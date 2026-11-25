"""Testplan 8: rij- en rusttijden (regel 7) en arbeidstijd (regel 8)."""

from datetime import UTC, date, datetime, timedelta

import pytest

from app.rules.basis import RegelBoek
from app.rules.rijtijd import Activiteit, Geschiedenis, controleer_dag

DAG = date(2026, 11, 26)
BEGIN = datetime(2026, 11, 26, 5, 0, tzinfo=UTC)


@pytest.fixture
def boek(db):
    return RegelBoek.laad(db)


def dag(*blokken: tuple[str, int]) -> list[Activiteit]:
    """Maak een dag van blokken achter elkaar, bijvoorbeeld ('rijden', 120), ('pauze', 45)."""
    t = BEGIN
    uit = []
    for soort, minuten in blokken:
        uit.append(Activiteit(soort, t, t + timedelta(minutes=minuten), rit_id=1))
        t += timedelta(minutes=minuten)
    return uit


def regel7(uitslag):
    return [o.tekst for o in uitslag.overtredingen]


def test_meer_dan_4_5_uur_rijden_zonder_pauze_faalt(boek):
    u = controleer_dag(boek, DAG, dag(("rijden", 280)))
    assert any("zonder pauze" in t for t in regel7(u))


def test_precies_4_5_uur_rijden_mag(boek):
    u = controleer_dag(boek, DAG, dag(("rijden", 270), ("pauze", 45), ("rijden", 60)))
    assert u.ok, regel7(u)


def test_werk_is_geen_pauze(boek):
    # Laden/wachten telt als werk, dus de teller voor 4,5 uur rijden loopt door.
    u = controleer_dag(boek, DAG, dag(("rijden", 200), ("werk", 45), ("rijden", 100)))
    assert any("zonder pauze" in t for t in regel7(u))


def test_gesplitste_pauze_15_plus_30_slaagt(boek):
    u = controleer_dag(boek, DAG, dag(("rijden", 150), ("pauze", 15), ("rijden", 120), ("pauze", 30),
                                      ("rijden", 200)))
    assert u.ok, regel7(u)


def test_gesplitste_pauze_omgekeerd_30_plus_15_faalt(boek):
    # Eerst 30 en dan 15 telt niet als gesplitste pauze: het tweede deel moet minimaal 30 zijn.
    u = controleer_dag(boek, DAG, dag(("rijden", 150), ("pauze", 30), ("rijden", 100), ("pauze", 15),
                                      ("rijden", 100)))
    assert any("zonder pauze" in t for t in regel7(u))


def _lange_dag(rij_min: int) -> list[Activiteit]:
    blokken = []
    over = rij_min
    while over > 0:
        stuk = min(240, over)
        blokken.append(("rijden", stuk))
        over -= stuk
        if over > 0:
            blokken.append(("pauze", 45))
    return dag(*blokken)


def test_meer_dan_9_uur_rijden_zonder_verlengde_dagen_over_faalt(boek):
    g = Geschiedenis(verlengde_dagen_deze_week=2)
    u = controleer_dag(boek, DAG, _lange_dag(560), g)
    assert any("Rijtijd vandaag" in t for t in regel7(u))


def test_10_uur_mag_als_er_nog_een_verlengde_dag_over_is(boek):
    u = controleer_dag(boek, DAG, _lange_dag(600), Geschiedenis(verlengde_dagen_deze_week=1))
    assert not any("Rijtijd vandaag" in t for t in regel7(u))
    assert u.verlengde_dag


def test_10_uur_een_derde_keer_in_de_week_faalt(boek):
    u = controleer_dag(boek, DAG, _lange_dag(600), Geschiedenis(verlengde_dagen_deze_week=2))
    assert any("2 keer per week" in t for t in regel7(u))


def test_meer_dan_10_uur_faalt_altijd(boek):
    u = controleer_dag(boek, DAG, _lange_dag(610))
    assert any("meer dan 10 uur" in t for t in regel7(u))


def test_dienst_langer_dan_13_uur_faalt(boek):
    u = controleer_dag(boek, DAG, dag(("rijden", 120), ("pauze", 45), ("werk", 300), ("pauze", 120),
                                      ("werk", 200), ("pauze", 30), ("rijden", 30)))
    assert any("Dienst duurt" in t for t in regel7(u))


def test_weekgrens_56_uur(boek):
    u = controleer_dag(boek, DAG, _lange_dag(240), Geschiedenis(rijtijd_deze_week_min=53 * 60))
    assert any("deze week" in t for t in regel7(u))


def test_twee_weken_90_uur(boek):
    g = Geschiedenis(rijtijd_deze_week_min=40 * 60, rijtijd_vorige_week_min=48 * 60)
    u = controleer_dag(boek, DAG, _lange_dag(180), g)
    assert any("twee weken" in t for t in regel7(u))


def test_6_tot_9_uur_werk_vraagt_30_minuten_pauze(boek):
    zonder = controleer_dag(boek, DAG, dag(("werk", 200), ("rijden", 100), ("pauze", 20), ("werk", 120)))
    assert any("minimaal 30 min pauze" in o.tekst for o in zonder.arbeid)
    met = controleer_dag(boek, DAG, dag(("werk", 200), ("rijden", 100), ("pauze", 30), ("werk", 120)))
    assert not any("min pauze" in o.tekst for o in met.arbeid)


def test_meer_dan_9_uur_werk_vraagt_45_minuten(boek):
    u = controleer_dag(boek, DAG, dag(("werk", 250), ("pauze", 30), ("werk", 200), ("rijden", 120)))
    assert any("minimaal 45 min pauze" in o.tekst for o in u.arbeid)


def test_overwerk_boven_contracturen(boek):
    u = controleer_dag(boek, DAG, dag(("werk", 240), ("pauze", 30), ("werk", 300)), contracturen_week=40)
    assert u.overwerk_min == 540 - 480
