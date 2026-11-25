"""Rookproef: elke hoofdpagina geeft een normale pagina."""

from tests.conftest import inloggen

PAGINAS = ["/", "/stamdata", "/voertuigen", "/logboek", "/instellingen"]


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
