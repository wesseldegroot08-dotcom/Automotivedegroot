"""Gedeelde test-instellingen.

Elke test krijgt een eigen, verse database met demodata.
De klok staat vast op woensdag 25 november 2026, 10:00 (Nederlandse tijd).
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

_map = Path(tempfile.mkdtemp(prefix="planning-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_map / 'test.db').as_posix()}"
os.environ["GEHEIME_SLEUTEL"] = "test-sleutel"
os.environ["DEMO_WACHTWOORD"] = "demo1234"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import db as dbmod  # noqa: E402
from app.ports.clock import NL, VasteKlok, zet_klok  # noqa: E402

TEST_MOMENT = datetime(2026, 11, 25, 10, 0, tzinfo=NL)


@pytest.fixture(autouse=True)
def vaste_klok():
    zet_klok(VasteKlok(TEST_MOMENT))
    yield
    from app.ports.clock import SysteemKlok

    zet_klok(SysteemKlok())


@pytest.fixture
def db():
    from app.seed import vul

    dbmod.Base.metadata.drop_all(dbmod.engine)
    dbmod.Base.metadata.create_all(dbmod.engine)
    sessie = dbmod.SessionLocal()
    vul(sessie)
    sessie.commit()
    sessie.info["gebruiker"] = "test"
    yield sessie
    sessie.close()


@pytest.fixture
def client(db):
    from app.main import app

    return TestClient(app)


def inloggen(client: TestClient, naam: str = "planner", wachtwoord: str = "demo1234"):
    pagina = client.get("/login")
    token = _csrf(pagina.text)
    return client.post("/login", data={"gebruikersnaam": naam, "wachtwoord": wachtwoord, "csrf": token},
                       follow_redirects=False)


def _csrf(html: str) -> str:
    import re

    gevonden = re.search(r'name="csrf" value="([^"]+)"', html)
    assert gevonden, "Geen CSRF-token in de pagina"
    return gevonden.group(1)


def csrf_van(client: TestClient, url: str = "/") -> str:
    return _csrf(client.get(url).text)
