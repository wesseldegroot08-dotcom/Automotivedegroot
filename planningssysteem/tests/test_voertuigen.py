"""Test 17 uit het testplan: voertuigen toevoegen, combinatiepagina, archiveren en CSV."""

from sqlalchemy import select

from app import models as m
from tests.conftest import csrf_van, inloggen

BASIS_TREKKER = {"kenteken": "99-TST-9", "intern_nummer": "99", "aandrijving": "4x2", "tarra_kg": "8000",
                 "adr_uitvoering": "geen", "status": "actief"}


def test_trekker_zonder_tarra_bron_wordt_niet_opgeslagen(client, db):
    inloggen(client)
    token = csrf_van(client, "/voertuigen/trekker/nieuw")
    r = client.post("/voertuigen/trekker/nieuw", data={**BASIS_TREKKER, "csrf": token})
    assert r.status_code == 422
    assert "Dit veld is verplicht" in r.text
    assert db.scalar(select(m.Trekker).where(m.Trekker.kenteken == "99-TST-9")) is None


def test_tarra_met_bron_aanname_geeft_een_vlag(client, db):
    inloggen(client)
    token = csrf_van(client, "/voertuigen/trekker/nieuw")
    r = client.post("/voertuigen/trekker/nieuw", data={**BASIS_TREKKER, "tarra_bron": "aanname", "csrf": token})
    assert r.status_code == 200  # na opslaan door naar de detailpagina
    assert "⚑ Aanname" in r.text
    assert "Tarra is een aanname" in r.text  # in de lijst 'Dit ontbreekt nog'


def test_sjabloon_vult_aanname_uit_regeltabel(client):
    inloggen(client)
    r = client.get("/voertuigen/trekker/nieuw?sjabloon=4x2-aanname")
    assert 'value="8000"' in r.text and "⚑ Aanname" in r.text


def _combinatie(client, db, trekker_nr, chassis_nr, **params):
    t = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == trekker_nr))
    c = db.scalar(select(m.Chassis).where(m.Chassis.nummer == chassis_nr))
    return client.get("/voertuigen/combinatie", params={"trekker_id": t.id, "chassis_id": c.id, **params})


def test_combinatiepagina_geeft_de_getallen_van_voorbeeld_1(client, db):
    """Trekker 11 (8.000 kg, aanname) + chassis C-204 (4.540 kg) + 40ft HC met 26.330 kg lading."""
    inloggen(client)
    r = _combinatie(client, db, "11", "C-204", c1_maat="40", c1_type="HC", c1_gewicht="26330", c1_soort="lading",
                    c1_tarra="4150", route="NL-intermodaal")
    assert r.status_code == 200
    for getal in ("16.690 kg", "33.310 kg", "27.310 kg", "25.310 kg", "23.310 kg"):
        assert getal in r.text, getal
    assert "onzeker door aanname" in r.text


def test_combinatiepagina_voorbeeld_2_twee_20ft(client, db):
    inloggen(client)
    # Trekker 11 (8.000) + C-206 multi (5.300) + 2 lege 20ft (2.250)
    r = _combinatie(client, db, "11", "C-206", c1_maat="20", c1_type="DC", c1_gewicht="2250", c1_tarra="2250",
                    c2_maat="20", c2_type="DC", c2_gewicht="2250", c2_tarra="2250")
    assert "17.800 kg" in r.text and "26.200 kg" in r.text and "32.200 kg" in r.text


def test_combinatiepagina_voorbeeld_3_aslast(client, db):
    inloggen(client)
    # Trekker 11 (4x2, 8.000) + C-201 (20ft, 2 assen, 3.450) + zware 20ft 30.480 bruto
    r = _combinatie(client, db, "11", "C-201", c1_maat="20", c1_type="DC", c1_gewicht="30480", c1_tarra="2250")
    assert "39.500 kg" in r.text and "2.430 kg te zwaar" in r.text


def test_combinatiepagina_toont_harde_regel(client, db):
    inloggen(client)
    r = _combinatie(client, db, "11", "C-204", c1_maat="45", c1_type="HC", c1_gewicht="20000")
    assert "Hard: niet toegestaan" in r.text


def test_archiveren_verwijdert_geen_historie(client, db):
    inloggen(client)
    t = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == "15"))
    rit = m.Rit(order_id=1, type="afhaal", van_locatie_id=1, naar_locatie_id=2, trekker_id=t.id)
    db.add(rit)
    db.commit()
    token = csrf_van(client, f"/voertuigen/trekker/{t.id}")
    client.post(f"/voertuigen/trekker/{t.id}/archiveren", data={"csrf": token})
    db.expire_all()
    t2 = db.get(m.Trekker, t.id)
    assert t2 is not None and t2.gearchiveerd
    assert db.get(m.Rit, rit.id).trekker_id == t.id
    assert "05-DTB-5" not in client.get("/voertuigen").text
    assert "05-DTB-5" in client.get("/voertuigen?archief=1").text


def test_csv_import_weigert_foute_rijen_met_duidelijke_melding(client, db):
    inloggen(client)
    token = csrf_van(client, "/voertuigen/import")
    csv = ("kenteken;intern_nummer;aandrijving;tarra_kg;tarra_bron;adr_uitvoering;status\n"
           "77-CSV-1;71;4x2;8100;gewogen;geen;actief\n"
           "77-CSV-2;72;4x2;8100;;geen;actief\n"          # bron ontbreekt
           "77-CSV-3;73;8x8;achtduizend;gewogen;geen;actief\n")  # foute aandrijving en tarra
    r = client.post("/voertuigen/import", data={"csrf": token, "soort": "trekker"},
                    files={"bestand": ("t.csv", csv.encode(), "text/csv")})
    assert "1 rij(en) opgeslagen" in r.text
    assert "2 rij(en) geweigerd" in r.text
    assert "Rij 3: Bron van de tarra: Dit veld is verplicht." in r.text
    assert "Rij 4:" in r.text and "Vul een heel getal in" in r.text
    assert db.scalar(select(m.Trekker).where(m.Trekker.kenteken == "77-CSV-1")) is not None
    assert db.scalar(select(m.Trekker).where(m.Trekker.kenteken == "77-CSV-2")) is None


def test_csv_export_en_terug_importeren(client):
    inloggen(client)
    export = client.get("/voertuigen/export/chassis.csv")
    assert export.status_code == 200 and "C-204" in export.text
    token = csrf_van(client, "/voertuigen/import")
    r = client.post("/voertuigen/import", data={"csrf": token, "soort": "chassis"},
                    files={"bestand": ("c.csv", export.content, "text/csv")})
    assert "8 rij(en) opgeslagen" in r.text and "geweigerd" not in r.text


def test_voorkeur_gewicht_moet_0_tot_10_zijn(client, db):
    inloggen(client)
    t = db.scalar(select(m.Trekker).where(m.Trekker.intern_nummer == "11"))
    token = csrf_van(client, f"/voertuigen/trekker/{t.id}")
    r = client.post(f"/voertuigen/trekker/{t.id}/voorkeur",
                    data={"csrf": token, "soort": "taak", "waarde": "reefer", "gewicht": "11"})
    assert r.status_code == 422
    r = client.post(f"/voertuigen/trekker/{t.id}/voorkeur",
                    data={"csrf": token, "soort": "taak", "waarde": "reefer", "gewicht": "7"}, follow_redirects=False)
    assert r.status_code == 303
