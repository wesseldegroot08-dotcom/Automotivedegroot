"""Reistijden (poort: TravelTimeProvider).

Nu: een tabel met vaste reistijden die de planner kan aanpassen.
Staat een paar niet in de tabel? Dan: afstand in rechte lijn x correctiefactor, bij een vaste snelheid.
Dat is een aanname en wordt ook zo getoond.

Later kan hier een zelf gehoste kaartdienst achter (OSRM of Valhalla), zonder de rest te veranderen.
"""

import math
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Instelling, Locatie, Reistijd


@dataclass(frozen=True)
class Reis:
    minuten: int
    km: int
    km_buitenland: int = 0
    land_buitenland: str | None = None
    is_aanname: bool = True
    bron: str = "aanname"


class TravelTimeProvider(Protocol):
    def reis(self, van: Locatie, naar: Locatie) -> Reis: ...


def hemelsbreed_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class TabelReistijden:
    """Leest de tabel één keer in. Snel genoeg voor een kleine vloot."""

    def __init__(self, db: Session):
        self._tabel = {(r.van_locatie_id, r.naar_locatie_id): r for r in db.scalars(select(Reistijd))}
        inst = {i.sleutel: i.waarde for i in db.scalars(select(Instelling))}
        self.factor = int(inst.get("reistijd_correctiefactor_procent", "130")) / 100
        self.snelheid = int(inst.get("gemiddelde_snelheid_kmu", "60"))

    def reis(self, van: Locatie, naar: Locatie) -> Reis:
        if van.id == naar.id:
            return Reis(0, 0, is_aanname=False, bron="zelfde plek")
        for sleutel in ((van.id, naar.id), (naar.id, van.id)):
            r = self._tabel.get(sleutel)
            if r:
                return Reis(r.minuten, r.km, r.km_buitenland, r.land_buitenland, r.is_aanname, r.bron)
        km = hemelsbreed_km(van.lat, van.lon, naar.lat, naar.lon) * self.factor
        minuten = max(5, round(km / self.snelheid * 60))
        buitenland = naar.land if naar.land != "NL" else (van.land if van.land != "NL" else None)
        return Reis(minuten, round(km), 0, buitenland, True,
                    f"rechte lijn x {self.factor:.2f} bij {self.snelheid} km/u (aanname)")
