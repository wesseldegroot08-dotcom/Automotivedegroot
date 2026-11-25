"""Test 9 uit het testplan: verbodsdag Duitsland, plus regel 21."""

from datetime import date, datetime

import pytest

from app.ports.clock import NL
from app.rules.basis import HARD, OK, WAARSCHUWING, RegelBoek
from app.rules.verbodsdag import regel_de_intermodaal, regel_verbodsdag

ZONDAG = date(2026, 11, 29)


@pytest.fixture
def boek(db):
    return RegelBoek.laad(db)


def t(d, uur):
    return datetime(d.year, d.month, d.day, uur, tzinfo=NL)


def test_zondag_naar_duitsland_boven_75t_faalt(boek):
    u = regel_verbodsdag(boek, "DE", t(ZONDAG, 8), t(ZONDAG, 14), 40000, set())
    assert u.niveau == HARD and "zondag" in u.uitleg


def test_zondag_na_22_uur_mag(boek):
    assert regel_verbodsdag(boek, "DE", t(ZONDAG, 22), t(ZONDAG, 23), 40000, set()).niveau == OK


def test_lichter_dan_75t_mag(boek):
    assert regel_verbodsdag(boek, "DE", t(ZONDAG, 8), t(ZONDAG, 14), 7000, set()).niveau == OK


def test_gecombineerd_vervoer_uitzondering(boek):
    ok = regel_verbodsdag(boek, "DE", t(ZONDAG, 8), t(ZONDAG, 14), 40000, set(), True, km_weg=120)
    assert ok.niveau == OK and "Uitzondering" in ok.uitleg
    te_ver = regel_verbodsdag(boek, "DE", t(ZONDAG, 8), t(ZONDAG, 14), 40000, set(), True, km_weg=220)
    assert te_ver.niveau == HARD


def test_feestdag_telt_als_verbodsdag(boek):
    kerst = date(2026, 12, 25)  # een vrijdag
    assert regel_verbodsdag(boek, "DE", t(kerst, 9), t(kerst, 12), 40000, {kerst}).niveau == HARD


def test_nederland_heeft_geen_verbodsdag(boek):
    assert regel_verbodsdag(boek, "NL", t(ZONDAG, 8), t(ZONDAG, 14), 40000, set()) is None


def test_duitsland_intermodaal_220km_geeft_waarschuwing(boek):
    assert regel_de_intermodaal(boek, ZONDAG, "DE-intermodaal", 220).niveau == WAARSCHUWING
    assert regel_de_intermodaal(boek, ZONDAG, "DE-intermodaal", 120).niveau == OK
