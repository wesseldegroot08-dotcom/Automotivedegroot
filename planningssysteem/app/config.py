"""Instellingen uit het .env-bestand.

Geheimen (sleutels, wachtwoorden) staan nooit in de code, maar in .env.
"""

import os
from functools import lru_cache
from pathlib import Path

BASIS_MAP = Path(__file__).resolve().parent.parent


def _lees_env_bestand() -> None:
    """Lees .env en zet de waarden in os.environ (zonder extra pakket)."""
    pad = BASIS_MAP / ".env"
    if not pad.exists():
        return
    for regel in pad.read_text(encoding="utf-8").splitlines():
        regel = regel.strip()
        if not regel or regel.startswith("#") or "=" not in regel:
            continue
        sleutel, waarde = regel.split("=", 1)
        os.environ.setdefault(sleutel.strip(), waarde.strip())


class Instellingen:
    def __init__(self) -> None:
        _lees_env_bestand()
        self.geheime_sleutel = os.environ.get("GEHEIME_SLEUTEL", "")
        url = os.environ.get("DATABASE_URL", "sqlite:///data/planning.db")
        # Een relatief SQLite-pad rekenen we vanaf de projectmap.
        if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
            rel = url.removeprefix("sqlite:///")
            if rel and rel != ":memory:" and not Path(rel).is_absolute():
                pad = BASIS_MAP / rel
                pad.parent.mkdir(parents=True, exist_ok=True)
                url = f"sqlite:///{pad.as_posix()}"
        self.database_url = url
        self.demo_wachtwoord = os.environ.get("DEMO_WACHTWOORD", "demo1234")
        self.cookie_secure = os.environ.get("COOKIE_SECURE", "0") == "1"
        self.bedrijfsnaam = os.environ.get("BEDRIJFSNAAM", "Degroot Transport")


@lru_cache
def instellingen() -> Instellingen:
    return Instellingen()
