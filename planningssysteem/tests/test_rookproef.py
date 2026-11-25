"""Rookproef: elke hoofdpagina geeft een normale pagina."""

from tests.conftest import inloggen

PAGINAS = ["/", "/stamdata", "/voertuigen", "/voertuigen/combinatie", "/voertuigen/import",
           "/voertuigen/trekker/nieuw", "/voertuigen/chassis/nieuw", "/voertuigen/trekker/1",
           "/voertuigen/chassis/1", "/logboek", "/instellingen", "/planbord", "/planbord?per=chauffeur",
           "/planbord?rit=1", "/planbord?rit=4", "/planbord/terminals", "/planbord?datum=2026-11-27", "/voorstellen",
           "/orders/inlezen", "/facturen", "/export/rooster"]


def test_alle_hoofdpaginas_openen(client):
    from app.web.entiteiten import ENTITEITEN

    inloggen(client, "admin")
    urls = PAGINAS + [f"/stamdata/{e.slug}" for e in ENTITEITEN] + [f"/stamdata/{e.slug}/nieuw" for e in ENTITEITEN]
    for url in urls:
        r = client.get(url)
        assert r.status_code == 200, f"{url} gaf {r.status_code}"
        assert "Er ging iets mis" not in r.text, url


def test_bewerkpagina_van_eerste_rij_opent(client):
    from app.web.entiteiten import ENTITEITEN

    inloggen(client)
    for e in ENTITEITEN:
        r = client.get(f"/stamdata/{e.slug}/1")
        assert r.status_code in (200, 404), e.slug


def test_end_to_end_voorstel_goedkeuren_en_exporteren(client, db):
    """Testplan 19: inloggen, voorstel maken, goedkeuren, rooster exporteren."""
    from sqlalchemy import select

    from app import models as m
    from tests.conftest import csrf_van

    db.get(m.Instelling, "solver_tijdlimiet_sec").waarde = "5"
    db.commit()
    assert inloggen(client).status_code == 303
    token = csrf_van(client, "/planbord")
    r = client.post("/voorstellen/maken", data={"datum": "2026-11-26", "csrf": token})
    assert r.status_code == 200 and "Kan niet gepland worden" in r.text
    v = db.scalar(select(m.Voorstel))
    r = client.post(f"/voorstellen/{v.id}/goedkeuren", data={"csrf": token})
    assert r.status_code == 200 and "Voorstel goedgekeurd" in r.text and "Er ging iets mis" not in r.text
    r = client.get("/export/rooster.csv?datum=2026-11-26")
    assert r.status_code == 200 and r.text.count("\n") > 3
