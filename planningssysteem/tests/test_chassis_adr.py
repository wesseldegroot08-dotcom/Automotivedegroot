"""Tests 6 en 7 uit het testplan: chassis past, reefer en ADR."""

from datetime import date, timedelta
from types import SimpleNamespace

from app.rules.basis import HARD, OK
from app.rules.voertuig import (
    ChassisInvoer,
    ContainerInvoer,
    TrekkerInvoer,
    regel_adr,
    regel_chassis_past,
    regel_reefer,
)

DAG = date(2026, 11, 26)


def ch(type_="40ft", **kw):
    basis = dict(twistlock_20=False, twistlock_40=False, twistlock_45=False, geschikt_voor="dry,HC")
    basis.update(kw)
    return ChassisInvoer("chassis C-1", type_, 3, 4540, "fabrikant", **basis)


def test_45ft_op_40ft_chassis_is_hard():
    u = regel_chassis_past(ch("40ft", twistlock_40=True), [ContainerInvoer("45", "HC", 20000, 4800)])
    assert u.niveau == HARD and "45ft past niet" in u.uitleg


def test_40ft_hc_op_40ft_chassis_is_ok():
    assert regel_chassis_past(ch("40ft", twistlock_40=True), [ContainerInvoer("40", "HC", 20000, 4150)]).niveau == OK


def test_tank_op_gewoon_chassis_is_hard():
    u = regel_chassis_past(ch("20ft", twistlock_20=True), [ContainerInvoer("20", "tank", 24000, 3600)])
    assert u.niveau == HARD and "niet geschikt voor tank" in u.uitleg


def test_tank_op_tankchassis_is_ok():
    tank = ch("tank", twistlock_20=True, geschikt_voor="tank", adr_tank=True)
    assert regel_chassis_past(tank, [ContainerInvoer("20", "tank", 24000, 3600)]).niveau == OK


def test_reefer_zonder_stroom_of_genset_is_hard():
    reefer = [ContainerInvoer("40", "reefer", 24000, 4500)]
    assert regel_reefer(ch("40ft", twistlock_40=True, genset="niet"), reefer).niveau == HARD
    assert regel_reefer(ch("40ft", twistlock_40=True, genset="clip-on"), reefer).niveau == OK


def test_twee_20ft_alleen_op_multi_chassis():
    twee = [ContainerInvoer("20", "DC", 10000, 2250), ContainerInvoer("20", "DC", 10000, 2250)]
    assert regel_chassis_past(ch("20ft", twistlock_20=True), twee).niveau == HARD
    assert regel_chassis_past(ch("multi", twistlock_20=True, twistlock_40=True), twee).niveau == OK


def test_kiepen_zonder_kiepfunctie_is_hard():
    c = [ContainerInvoer("20", "DC", 20000, 2250)]
    assert regel_chassis_past(ch("20ft", twistlock_20=True), c, ["kiepen"]).niveau == HARD


# ---------------------------------------------------------------- ADR


def chauffeur(basis=None, tank=None, naam="Test"):
    return SimpleNamespace(pseudoniem=naam, adr_basis_tot=basis, adr_tank_tot=tank)


ADR_TANK = [ContainerInvoer("20", "tank", 24000, 3600, imo_klasse="3")]
TANKWAGEN = TrekkerInvoer("trekker 12", "4x2", 7650, "gewogen", adr_uitvoering="tank")
TANKCHASSIS = ChassisInvoer("chassis C-208", "tank", 3, 4800, "aanname", twistlock_20=True, geschikt_voor="tank",
                            adr_tank=True)
GELDIG = DAG + timedelta(days=100)


def test_adr_zonder_geldig_certificaat_is_hard():
    u = regel_adr(DAG, ADR_TANK, TANKWAGEN, TANKCHASSIS, chauffeur())
    assert u.niveau == HARD and "geen geldig ADR" in u.uitleg


def test_adr_met_verlopen_datum_is_hard():
    u = regel_adr(DAG, ADR_TANK, TANKWAGEN, TANKCHASSIS, chauffeur(basis=DAG - timedelta(days=1), tank=GELDIG))
    assert u.niveau == HARD and "verlopen" in u.uitleg


def test_adr_tank_vraagt_ook_tank_certificaat():
    u = regel_adr(DAG, ADR_TANK, TANKWAGEN, TANKCHASSIS, chauffeur(basis=GELDIG))
    assert u.niveau == HARD and "ADR-tank-certificaat" in u.uitleg


def test_trekker_zonder_adr_uitvoering_is_hard():
    gewone = TrekkerInvoer("trekker 11", "4x2", 8000, "aanname", adr_uitvoering="geen")
    u = regel_adr(DAG, ADR_TANK, gewone, TANKCHASSIS, chauffeur(basis=GELDIG, tank=GELDIG))
    assert u.niveau == HARD and "trekker 11 heeft geen ADR" in u.uitleg


def test_alles_in_orde_is_ok():
    assert regel_adr(DAG, ADR_TANK, TANKWAGEN, TANKCHASSIS, chauffeur(basis=GELDIG, tank=GELDIG)).niveau == OK


def test_geen_adr_lading_geeft_geen_adr_regel():
    assert regel_adr(DAG, [ContainerInvoer("40", "HC", 20000, 4150)], TANKWAGEN, TANKCHASSIS, chauffeur()) is None
