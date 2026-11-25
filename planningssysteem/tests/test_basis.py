"""Mijlpaal 1: login, rollen, CSRF, logboek, regels als data en demodata."""

import pytest
from sqlalchemy import func, select

from app import models as m
from app.audit import LogboekNietWijzigbaar
from app.rules.iso6346 import controleer_containernummer
from tests.conftest import csrf_van, inloggen

# ------------------------------------------------------------------ demodata


def test_demodata_heeft_de_gevraagde_aantallen(db):
    def tel(model, *where):
        return db.scalar(select(func.count()).select_from(model).where(*where))

    assert tel(m.Trekker) == 6
    assert tel(m.Chassis) == 8
    assert tel(m.Chauffeur) == 8
    assert tel(m.Locatie, m.Locatie.type == "terminal") == 4
    assert tel(m.Locatie, m.Locatie.type == "depot") == 3
    assert tel(m.Klant) == 5
    assert tel(m.Rederij) == 2
    assert tel(m.Order) == 25
    # 2 chauffeurs met geldig ADR, waarvan 1 met tank (Hamza's ADR is verlopen)
    from app.ports.clock import vandaag_nl
    vandaag = vandaag_nl()
    assert tel(m.Chauffeur, m.Chauffeur.adr_basis_tot >= vandaag) == 2
    assert tel(m.Chauffeur, m.Chauffeur.adr_tank_tot >= vandaag) == 1


def test_alle_demo_containernummers_zijn_geldig(db):
    for c in db.scalars(select(m.Container)):
        assert controleer_containernummer(c.nummer).geldig, c.nummer


def test_elke_regel_heeft_bron_en_status(db):
    for r in db.scalars(select(m.Regel)):
        assert r.bron and r.status in ("bevestigd", "schatting", "open"), r.code


# ------------------------------------------------------------------ inloggen en rollen


def test_niet_ingelogd_gaat_naar_inlogpagina(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_inloggen_werkt_en_fout_wachtwoord_niet(client):
    assert inloggen(client, "planner", "fout").status_code == 401
    r = inloggen(client)
    assert r.status_code == 303
    assert client.get("/").status_code == 200


def test_rem_op_inlogpogingen(client):
    for _ in range(5):
        assert inloggen(client, "planner", "fout").status_code == 401
    # Ook het goede wachtwoord wordt nu even geweigerd
    assert inloggen(client, "planner", "demo1234").status_code == 429


def test_wachtwoord_is_gehasht(db):
    g = db.scalar(select(m.Gebruiker).where(m.Gebruiker.gebruikersnaam == "planner"))
    assert g.wachtwoord_hash.startswith("$argon2")
    assert "demo1234" not in g.wachtwoord_hash


def test_chauffeur_mag_niet_in_stamdata(client):
    inloggen(client, "chauffeur")
    assert client.get("/stamdata/klanten").status_code == 403


def test_post_zonder_csrf_wordt_geweigerd(client):
    inloggen(client)
    r = client.post("/stamdata/klanten/nieuw", data={"naam": "X", "betaaltermijn_dagen": "30"})
    assert r.status_code == 403


# ------------------------------------------------------------------ logboek


def test_wijziging_via_app_komt_in_logboek(client, db):
    inloggen(client)
    token = csrf_van(client, "/stamdata/klanten/nieuw")
    r = client.post("/stamdata/klanten/nieuw", data={"csrf": token, "naam": "Nieuwe Klant (demo)",
                                                     "betaaltermijn_dagen": "14"}, follow_redirects=False)
    assert r.status_code == 303
    log = db.scalars(select(m.AuditLog).where(m.AuditLog.tabel == "klant", m.AuditLog.actie == "aanmaken",
                                              m.AuditLog.gebruiker == "planner")).all()
    assert len(log) == 1 and "Nieuwe Klant (demo)" in log[0].na


def test_wijzigen_logt_voor_en_na(db):
    klant = db.scalar(select(m.Klant).where(m.Klant.naam.like("Alfa%")))
    klant.betaaltermijn_dagen = 60
    db.commit()
    log = db.scalars(select(m.AuditLog).where(m.AuditLog.tabel == "klant", m.AuditLog.actie == "wijzigen")).one()
    assert '"betaaltermijn_dagen": 30' in log.voor and '"betaaltermijn_dagen": 60' in log.na
    assert log.gebruiker == "test"


def test_logboek_kan_niet_gewijzigd_of_verwijderd_worden(db):
    rij = db.scalars(select(m.AuditLog)).first()
    rij.reden = "stiekem aangepast"
    with pytest.raises(LogboekNietWijzigbaar):
        db.commit()
    db.rollback()
    rij = db.scalars(select(m.AuditLog)).first()
    db.delete(rij)
    with pytest.raises(LogboekNietWijzigbaar):
        db.commit()
    db.rollback()


def test_logboek_heeft_geen_wijzig_of_verwijder_pagina(client):
    inloggen(client)
    token = csrf_van(client)
    assert client.post("/logboek", data={"csrf": token}).status_code == 405
    assert client.post("/logboek/1", data={"csrf": token}).status_code in (404, 405)


# ------------------------------------------------------------------ regels als data


def test_regel_zonder_bron_wordt_niet_geaccepteerd(client, db):
    inloggen(client)
    voor = db.scalar(select(func.count()).select_from(m.Regel))
    token = csrf_van(client, "/stamdata/regels/nieuw")
    r = client.post("/stamdata/regels/nieuw", data={
        "csrf": token, "code": "kosten.test", "categorie": "kosten", "omschrijving": "Test",
        "waarde": "100", "eenheid": "cent", "geldig_van": "2026-01-01", "bron": "", "status": "",
    })
    assert r.status_code == 422
    assert "Dit veld is verplicht" in r.text
    assert db.scalar(select(func.count()).select_from(m.Regel)) == voor


def test_regel_aanpassen_komt_in_logboek(client, db):
    inloggen(client)
    regel = db.scalar(select(m.Regel).where(m.Regel.code == "gewicht.intermodaal.3as"))
    token = csrf_van(client, f"/stamdata/regels/{regel.id}")
    data = {"csrf": token, "code": regel.code, "categorie": regel.categorie, "omschrijving": regel.omschrijving,
            "waarde": "44500", "eenheid": "kg", "in_gebruik": "on", "geldig_van": "2026-01-01",
            "bron": "Test", "status": "schatting"}
    assert client.post(f"/stamdata/regels/{regel.id}", data=data, follow_redirects=False).status_code == 303
    db.expire_all()
    log = db.scalars(select(m.AuditLog).where(m.AuditLog.tabel == "regel", m.AuditLog.actie == "wijzigen",
                                              m.AuditLog.record_id == str(regel.id))).one()
    assert '"waarde": 44000' in log.voor and '"waarde": 44500' in log.na


def test_container_met_fout_nummer_wordt_geweigerd(client):
    inloggen(client)
    token = csrf_van(client, "/stamdata/containers/nieuw")
    r = client.post("/stamdata/containers/nieuw", data={
        "csrf": token, "nummer": "CSQU3054384", "rederij_id": "1", "maat": "40", "type": "HC",
        "vgm_kg": "20000", "status": "Aangekondigd"})
    assert r.status_code == 422 and "Controlecijfer klopt niet" in r.text


def test_archiveren_verwijdert_niets(client, db):
    inloggen(client)
    klant = db.scalar(select(m.Klant).where(m.Klant.naam.like("Echo%")))
    token = csrf_van(client, f"/stamdata/klanten/{klant.id}")
    client.post(f"/stamdata/klanten/{klant.id}/archiveren", data={"csrf": token})
    db.expire_all()
    assert db.get(m.Klant, klant.id) is not None and db.get(m.Klant, klant.id).actief is False
