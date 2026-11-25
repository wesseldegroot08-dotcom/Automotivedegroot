"""Tests 2 tot en met 5 uit het testplan: gewicht en aslast.

We gebruiken precies de getallen uit de opdracht. De trekker van 8.000 kg is een aanname.
"""

from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.rules.basis import HARD, OK, WAARSCHUWING, RegelBoek
from app.rules.voertuig import (
    ChassisInvoer,
    ContainerInvoer,
    TrekkerInvoer,
    aslast_grens,
    bereken_gewicht,
    lege_combinatie,
    max_lading,
    regel_aslast,
    regel_gewicht,
)

DAG = date(2026, 11, 26)


@pytest.fixture
def boek(db):
    return RegelBoek.laad(db)


def trekker(kg=8000, aandrijving="4x2", bron="aanname"):
    return TrekkerInvoer("trekker test", aandrijving, kg, bron)


def chassis(kg, assen=3, **kw):
    return ChassisInvoer("chassis test", kw.pop("type", "40ft"), assen, kg, "fabrikant", **kw)


# ---------------------------------------------------------------- voorbeeld 1: 40ft HC


def test_voorbeeld1_lege_combinatie_en_max_lading(boek):
    leeg = lege_combinatie(8000, 4540, [4150])
    assert leeg == 16690
    assert max_lading(50000, leeg) == 33310
    assert max_lading(44000, leeg) == 27310
    assert max_lading(42000, leeg) == 25310
    assert max_lading(40000, leeg) == 23310


def test_voorbeeld1_via_de_regeltabel(boek):
    lading = 26330
    hc = ContainerInvoer("40", "HC", vgm_kg=lading + 4150, tarra_kg=4150, tarra_aanname=False)
    g = bereken_gewicht(boek, DAG, trekker(), chassis(4540, twistlock_40=True), [hc])
    per = {r.code: r for r in g.per_grens}
    assert g.lege_combinatie_kg == 16690
    assert per["gewicht.NL"].max_lading_kg == 33310
    assert per["gewicht.intermodaal.3as"].max_lading_kg == 27310
    assert per["gewicht.intermodaal.2as"].max_lading_kg == 25310
    assert per["gewicht.DE"].max_lading_kg == 23310
    # 26.330 kg lading past bij 44 t (net: 980 kg marge), niet bij 42 t of 40 t
    assert per["gewicht.intermodaal.3as"].past and per["gewicht.intermodaal.3as"].marge_kg == 980
    assert not per["gewicht.intermodaal.2as"].past
    assert not per["gewicht.DE"].past
    # De trekker is een aanname, dus de uitkomst is onzeker
    assert g.zekerheid == "onzeker door aanname"


def test_voorbeeld1_zwaarste_trekker_die_nog_past_bij_44t(boek):
    # 44.000 - 4.540 - 4.150 - 26.330 = 8.980
    hc = ContainerInvoer("40", "HC", vgm_kg=26330 + 4150, tarra_kg=4150, tarra_aanname=False)
    ch = chassis(4540, twistlock_40=True)
    past = bereken_gewicht(boek, DAG, trekker(8980), ch, [hc], ["gewicht.intermodaal.3as"]).per_grens[0]
    te_zwaar = bereken_gewicht(boek, DAG, trekker(8981), ch, [hc], ["gewicht.intermodaal.3as"]).per_grens[0]
    assert past.past and past.marge_kg == 0
    assert not te_zwaar.past and te_zwaar.marge_kg == -1


# ---------------------------------------------------------------- voorbeeld 2: twee 20ft


def test_voorbeeld2_twee_20ft(boek):
    assert lege_combinatie(8000, 5300, [2250, 2250]) == 17800
    c = [ContainerInvoer("20", "DC", 2250, 2250, False), ContainerInvoer("20", "DC", 2250, 2250, False)]
    g = bereken_gewicht(boek, DAG, trekker(), chassis(5300, type="multi", twistlock_20=True), c)
    per = {r.code: r.max_lading_kg for r in g.per_grens}
    assert per["gewicht.intermodaal.3as"] == 26200
    assert per["gewicht.NL"] == 32200


# ---------------------------------------------------------------- voorbeeld 3: zware 20ft en aslast


def test_voorbeeld3_zware_20ft_past_bij_44t_maar_niet_op_de_assen(boek):
    zwaar = [ContainerInvoer("20", "DC", 30480, 2250, False)]
    t = trekker(aandrijving="6x2")  # 44 t geldt voor een 3-assige trekker
    ch2 = chassis(3450, assen=2, type="20ft", twistlock_20=True)
    g = regel_gewicht(boek, DAG, t, ch2, zwaar, "NL-intermodaal")
    assert g.niveau == OK  # 41.930 kg binnen 44 t
    assert "41,9 t van 44,0 t" in g.uitleg
    # De opdracht rekent met een 2-assige trekker voor de as-grens: 10.000 + 11.500 + 18.000 = 39.500
    a = regel_aslast(boek, DAG, trekker(aandrijving="4x2"), ch2, zwaar)
    assert a.niveau == WAARSCHUWING
    assert "39.500 kg" in a.uitleg and "2.430 kg te zwaar" in a.uitleg
    # Een 3-assig chassis lost het op
    ch3 = chassis(3450, assen=3, type="20ft", twistlock_20=True)
    assert regel_aslast(boek, DAG, trekker(aandrijving="4x2"), ch3, zwaar).niveau == OK


def test_aslast_2assige_trekker_met_3assig_chassis(boek):
    a = aslast_grens(boek, DAG, "4x2", 3)
    assert a.totaal_kg == 45500  # 10.000 + 11.500 + 24.000
    assert a.alternatief_kg == 48500  # met tridem 27.000 (Open)
    assert a.totaal_kg < 50000 and a.alternatief_kg < 50000  # dus geen 50 t


# ---------------------------------------------------------------- extra


def test_ontbrekende_tarra_geeft_geen_getal_maar_een_melding(boek):
    g = bereken_gewicht(boek, DAG, TrekkerInvoer("trekker x", "4x2", None, "aanname"), chassis(4540), [])
    assert g.lege_combinatie_kg is None and g.ontbreekt
    u = regel_gewicht(boek, DAG, TrekkerInvoer("trekker x", "4x2", None, "aanname"), chassis(4540), [], "NL")
    assert u.niveau == WAARSCHUWING and u.blokkeert_voorstel


def test_te_zwaar_is_waarschuwing_maar_hard_voor_voorstel(boek):
    zwaar = [ContainerInvoer("40", "HC", 28500 + 4150, 4150, False)]
    u = regel_gewicht(boek, DAG, trekker(), chassis(4540, twistlock_40=True), zwaar, "NL-intermodaal")
    assert u.niveau == WAARSCHUWING and u.hard_voor_voorstel and u.blokkeert_voorstel
    assert u.niveau != HARD


def test_regel_aanpassen_verandert_de_uitkomst(db):
    """Regels zijn data: pas de grens aan in de database en de berekening volgt."""
    from sqlalchemy import select

    from app.models import Regel

    regel = db.scalar(select(Regel).where(Regel.code == "gewicht.intermodaal.3as"))
    regel.waarde = 45000
    db.commit()
    g = bereken_gewicht(RegelBoek.laad(db), DAG, trekker(), chassis(4540), [], ["gewicht.intermodaal.3as"])
    assert g.per_grens[0].max_lading_kg == 45000 - 8000 - 4540


@given(t=st.integers(5000, 12000), c=st.integers(2000, 7000), tarra=st.integers(1800, 5000),
       lading=st.integers(0, 32000), limiet=st.sampled_from([40000, 42000, 44000, 50000]))
def test_formule_klopt_altijd(t, c, tarra, lading, limiet):
    """Eigenschap: past precies als de lading niet groter is dan de max lading."""
    leeg = lege_combinatie(t, c, [tarra])
    assert (leeg + lading <= limiet) == (lading <= max_lading(limiet, leeg))
