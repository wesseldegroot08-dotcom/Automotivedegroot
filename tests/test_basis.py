"""Tests. Draaien met: python -m pytest"""

import json
from datetime import date

import pytest

from winstradar import analyse, database, rdw, rode_vlaggen
from winstradar.advertentie import Advertentie
from winstradar.generaties import bepaal_generatie
from winstradar.instellingen import laad_instellingen
from winstradar.normaliseren import herken_motor, herken_transmissie, toon_kenteken, vul_aan, zoek_kenteken
from winstradar.sites.basis import json_uit_html
from winstradar.sites.marktplaats import hoort_bij_model, listing_naar_advertentie


@pytest.fixture
def inst():
    return laad_instellingen()


@pytest.fixture
def conn(tmp_path):
    return database.verbind(tmp_path / "test.db")


# ---------- herkennen ----------

def test_motor_herkennen():
    assert herken_motor("Volkswagen Polo 1.2 TSI Comfortline") == ("1.2 TSI", "1.2 turbo")
    assert herken_motor("Polo 1.2 12V Trendline")[1] == "1.2"          # geen turbo: andere motor
    assert herken_motor("Toyota Yaris 1.33 VVT-i")[1] == "1.3"
    assert herken_motor("Clio 0,9 TCe Expression")[1] == "0.9 turbo"
    assert herken_motor("Yaris Hybrid Aspiration", brandstof="hybride")[1] == "hybride"
    assert herken_motor("Golf Trendline")[1] is None


def test_transmissie():
    assert herken_transmissie("Automaat", "") == "automaat"
    assert herken_transmissie(None, "Golf 1.4 TSI DSG Highline") == "automaat"
    assert herken_transmissie("Handgeschakeld", "") == "handgeschakeld"
    assert herken_transmissie(None, "Golf 1.4 TSI Highline") is None


def test_generatie_en_wisseljaar():
    assert bepaal_generatie("Volkswagen", "Polo", 2014) == "6R/6C"
    assert bepaal_generatie("Volkswagen", "Golf", 2012) is None             # VI of VII: onzeker
    assert bepaal_generatie("Volkswagen", "Golf", 2012, "Golf 7 1.2 TSI") == "VII"


def test_kenteken():
    assert zoek_kenteken("Mooie auto, kenteken KX-218-T, apk tot juni") == "KX218T"
    assert zoek_kenteken("Kenteken: 19rvb4") == "19RVB4"
    assert zoek_kenteken("Geleverd op 12-05-2014") is None
    assert toon_kenteken("KX218T") == "KX-218-T"
    assert toon_kenteken("19RVB4") == "19-RVB-4"


# ---------- rekenen ----------

def maak_auto(i, prijs, jaar=2014, km=140000, titel="Volkswagen Polo 1.2 TSI Comfortline", tekst="Nette auto"):
    adv = Advertentie(site="test", advertentie_id=str(i), link="", titel=titel, beschrijving=tekst,
                      transmissie="Handgeschakeld", brandstof="Benzine", bouwjaar=jaar,
                      kilometerstand=km, vraagprijs=prijs)
    return vul_aan(adv, "Volkswagen", "Polo")


def test_winstberekening_met_melding(conn, inst):
    for i, p in enumerate([4950, 4600, 4750, 5100, 4400, 4850, 4700]):
        database.sla_op(conn, maak_auto(100 + i, p, km=140000 + i * 1000))
    # Deze telt niet mee: andere motor
    database.sla_op(conn, maak_auto(200, 3000, titel="Volkswagen Polo 1.4 16V"))
    # Deze telt niet mee: meer dan 25.000 km verschil
    database.sla_op(conn, maak_auto(201, 3000, km=170000))
    # Deze telt niet mee: bouwjaar 2 jaar verschil
    database.sla_op(conn, maak_auto(202, 3000, jaar=2012))
    # Deze wordt uitgesloten: rode-vlag-woord drukt de prijs
    database.sla_op(conn, maak_auto(203, 2500, km=139000, tekst="motor defect"))

    pk, _ = database.sla_op(conn, maak_auto(1, 3100, km=142500))
    r = analyse.analyseer(conn, database.haal_auto(conn, pk), inst)

    assert len(r.vergelijkbaar) == 7
    assert len(r.uitgesloten) == 1
    assert r.mediaan == 4750
    assert r.verkoopprijs == pytest.approx(4512.50)
    assert r.marge == pytest.approx(1412.50)
    assert r.kosten_totaal == 475
    assert r.winst == pytest.approx(937.50)
    assert r.status == "melding"


def test_bijna_als_winst_te_laag(conn, inst):
    for i, p in enumerate([4900, 5200, 4650, 4800, 5000]):
        database.sla_op(conn, maak_auto(100 + i, p, km=130000 + i * 1000))
    pk, _ = database.sla_op(conn, maak_auto(1, 3450))
    r = analyse.analyseer(conn, database.haal_auto(conn, pk), inst)
    assert r.marge == pytest.approx(1205)       # 4900 * 0.95 - 3450
    assert r.winst == pytest.approx(730)
    assert r.status == "bijna"


def test_te_weinig_data(conn, inst):
    for i, p in enumerate([4200, 4450, 3990]):
        database.sla_op(conn, maak_auto(100 + i, p, km=130000 + i * 1000))
    pk, _ = database.sla_op(conn, maak_auto(1, 3300))
    r = analyse.analyseer(conn, database.haal_auto(conn, pk), inst)
    assert r.status == "te_weinig_data"
    assert r.winst is None


def test_prijswijziging_en_duplicaat(conn):
    pk, status = database.sla_op(conn, maak_auto(1, 3750))
    assert status == "nieuw"
    _, status = database.sla_op(conn, maak_auto(1, 3450))
    assert status == "prijs_gewijzigd"
    geschiedenis = database.prijsgeschiedenis(conn, pk)
    assert (geschiedenis[0]["oude_prijs"], geschiedenis[0]["nieuwe_prijs"]) == (3750, 3450)
    # Zelfde auto opnieuw geplaatst (nieuw nummer, zelfde km): duplicaat
    pk2, _ = database.sla_op(conn, maak_auto(2, 3400))
    assert database.haal_auto(conn, pk2)["duplicaat_van"] == pk


# ---------- rode vlaggen en RDW ----------

def test_rode_vlaggen(inst):
    auto = {"titel": "Clio opknapper", "beschrijving": "Schadevrij maar motorstoring", "kilometerstand": None,
            "vraagprijs": 2400, "beschrijving_volledig": 1}
    vlaggen = rode_vlaggen.controleer(auto, inst, mediaan=4125)
    tekst = " ".join(vlaggen)
    assert "onder vergelijkbare" in tekst
    assert "opknapper" in tekst and "motorstoring" in tekst
    assert "schade”" not in tekst          # 'schadevrij' is geen rode vlag
    assert "Geen kilometerstand" in tekst
    assert "Vage beschrijving" in tekst


def test_rdw_controle(inst):
    auto = {"kenteken": "KX218T", "merk": "Volkswagen", "bouwjaar": 2014}
    gegevens = {"merk": "VOLKSWAGEN", "handelsbenaming": "POLO", "datum_eerste_toelating": "20130314",
                "vervaldatum_apk": "20261119", "tellerstandoordeel": "Onlogisch"}
    uit = rdw.controleer(auto, gegevens, inst, vandaag=date(2026, 9, 28))
    fouten = [t for ok, t in uit if not ok]
    assert any("eerste toelating 14-03-2013" in t for t in fouten)
    assert any("APK verloopt" in t for t in fouten)
    assert any("Onlogisch" in t for t in fouten)


# ---------- Marktplaats uitlezen ----------
# Let op: dit voorbeeld is nagebouwd. De echte opbouw van Marktplaats kan anders zijn.

VOORBEELD_LISTING = {
    "itemId": "m2123456789",
    "title": "Volkswagen Polo 1.2 TSI Comfortline | Airco | Cruise",
    "description": "Nette Polo met onderhoudshistorie.",
    "priceInfo": {"priceCents": 310000, "priceType": "FIXED"},
    "location": {"cityName": "Utrecht"},
    "vipUrl": "/v/auto-s/volkswagen/m2123456789-volkswagen-polo-1-2-tsi",
    "attributes": [{"key": "constructionYear", "value": "2014"}, {"key": "mileage", "value": "142.000 km"},
                   {"key": "fuel", "value": "Benzine"}, {"key": "transmission", "value": "Handgeschakeld"}],
}


def test_marktplaats_listing():
    adv = listing_naar_advertentie(VOORBEELD_LISTING)
    vul_aan(adv, "Volkswagen", "Polo")
    assert adv.vraagprijs == 3100
    assert adv.bouwjaar == 2014
    assert adv.kilometerstand == 142000
    assert adv.motor_sleutel == "1.2 turbo"
    assert adv.transmissie == "handgeschakeld"
    assert adv.generatie == "6R/6C"
    assert adv.link.startswith("https://www.marktplaats.nl/v/")
    assert hoort_bij_model(adv, "Volkswagen", "Polo")


def test_ander_model_wordt_overgeslagen():
    d = dict(VOORBEELD_LISTING, title="Volkswagen Golf Plus 1.4 TSI",
             vipUrl="/v/auto-s/volkswagen/m1-golf-plus")
    assert not hoort_bij_model(listing_naar_advertentie(d), "Volkswagen", "Golf")


def test_json_uit_html():
    html = ('<script id="__NEXT_DATA__" type="application/json">'
            + json.dumps({"props": {"listings": [VOORBEELD_LISTING]}}) + "</script>")
    assert json_uit_html(html)[0]["props"]["listings"][0]["itemId"] == "m2123456789"


# ---------- dashboard ----------

def test_dashboard_met_demo(tmp_path, inst):
    from winstradar.dashboard.app import maak_app
    from winstradar.demo import vul_demo
    pad = tmp_path / "demo.db"
    vul_demo(pad)
    client = maak_app(inst, pad, demo=True).test_client()
    pagina = client.get("/").get_data(as_text=True)
    assert "Polo" in pagina and "Melding" in pagina
    assert "verzonnen auto's" in pagina                  # demo-balk zichtbaar
    assert client.get("/?alleen_deals=1").status_code == 200
    detail = client.get("/auto/1").get_data(as_text=True)
    assert "Mediaan vraagprijs" in detail
    assert 'href=""' not in detail                      # geen lege links in de demo
    echt = maak_app(inst, pad).test_client().get("/").get_data(as_text=True)
    assert "verzonnen auto's" not in echt               # geen demo-balk in de echte versie


# ---------- netjes ophalen (met een nep-website, zonder internet) ----------

class NepAntwoord:
    def __init__(self, status, tekst=""):
        self.status_code, self.text = status, tekst


def maak_nep_ophaler(monkeypatch, paginas):
    """paginas: {url: NepAntwoord of Exception}."""
    from winstradar import ophalen
    monkeypatch.setattr(ophalen.time, "sleep", lambda s: None)
    o = ophalen.NetteOphaler("TestBot/1.0")
    bezocht = []

    def get(url, timeout):
        bezocht.append(url)
        antwoord = paginas.get(url, NepAntwoord(404))
        if isinstance(antwoord, Exception):
            raise antwoord
        return antwoord
    monkeypatch.setattr(o.sessie, "get", get)
    return o, bezocht


def test_robots_verbod_wordt_gerespecteerd(monkeypatch):
    from winstradar.ophalen import NietToegestaan
    o, bezocht = maak_nep_ophaler(monkeypatch, {
        "https://site.nl/robots.txt": NepAntwoord(200, "User-agent: *\nDisallow: /geheim/"),
        "https://site.nl/open": NepAntwoord(200, "hallo"),
    })
    assert o.haal("https://site.nl/open") == "hallo"
    with pytest.raises(NietToegestaan):
        o.haal("https://site.nl/geheim/pagina")
    assert "https://site.nl/geheim/pagina" not in bezocht   # nooit opgevraagd


def test_geen_verbinding_is_geen_verbod(monkeypatch):
    import requests
    o, _ = maak_nep_ophaler(monkeypatch, {
        "https://site.nl/robots.txt": requests.ConnectionError("geen internet"),
    })
    with pytest.raises(ConnectionError, match="kon robots.txt"):
        o.haal("https://site.nl/open")


def test_blokkade_wordt_herkend(monkeypatch):
    from winstradar.ophalen import SiteGeblokkeerd
    o, _ = maak_nep_ophaler(monkeypatch, {
        "https://site.nl/robots.txt": NepAntwoord(404),
        "https://site.nl/a": NepAntwoord(429),
        "https://site.nl/b": NepAntwoord(200, "<html>Please solve this CAPTCHA</html>"),
    })
    with pytest.raises(SiteGeblokkeerd):
        o.haal("https://site.nl/a")
    with pytest.raises(SiteGeblokkeerd):
        o.haal("https://site.nl/b")


def test_wachttijd_minimaal_5_seconden():
    from winstradar.ophalen import NetteOphaler
    assert NetteOphaler("x", wachttijd=1).wachttijd == 5
