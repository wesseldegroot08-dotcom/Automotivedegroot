"""Leest instellingen.toml en geheimen.toml in."""

import tomllib
from pathlib import Path

MAP = Path(__file__).resolve().parent.parent
INSTELLINGEN_BESTAND = MAP / "instellingen.toml"
GEHEIMEN_BESTAND = MAP / "geheimen.toml"
DATA_MAP = MAP / "data"
LOG_MAP = MAP / "logs"


def laad_instellingen(pad=INSTELLINGEN_BESTAND):
    """Geeft de instellingen terug als een dictionary."""
    with open(pad, "rb") as f:
        inst = tomllib.load(f)
    # Maak lijsten klein geschreven, zodat vergelijken makkelijk is.
    inst["zoeken"]["brandstof"] = [b.lower() for b in inst["zoeken"]["brandstof"]]
    inst["zoeken"]["transmissie"] = [t.lower() for t in inst["zoeken"]["transmissie"]]
    return inst


def laad_geheimen(pad=GEHEIMEN_BESTAND):
    """Geeft de geheimen terug. Bestaat het bestand niet? Dan een lege dictionary."""
    if not Path(pad).exists():
        return {}
    with open(pad, "rb") as f:
        return tomllib.load(f)


def totale_kosten(inst):
    return sum(inst["kosten"].values())
