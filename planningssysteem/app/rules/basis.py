"""Bouwstenen van de regelmotor.

Elke regel geeft een Uitslag terug:
- niveau: 'ok', 'waarschuwing' of 'hard'
- uitleg: korte zin in simpel Nederlands
- bron en status van de regel (bevestigd / schatting / open)
- hard_voor_voorstel: True als een automatisch voorstel deze waarschuwing nooit mag hebben

De waarden (limieten, tarieven) komen uit de database via het RegelBoek. Niet uit de code.
"""

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Regel

OK, WAARSCHUWING, HARD = "ok", "waarschuwing", "hard"
_ERNST = {OK: 0, WAARSCHUWING: 1, HARD: 2}


@dataclass
class Uitslag:
    nr: int
    naam: str
    niveau: str
    uitleg: str
    bron: str = ""
    status: str = "bevestigd"
    hard_voor_voorstel: bool = False
    bedrag_cent: int | None = None
    onzeker: list[str] = field(default_factory=list)  # welke invoer een aanname is

    @property
    def blokkeert_voorstel(self) -> bool:
        return self.niveau == HARD or (self.niveau == WAARSCHUWING and self.hard_voor_voorstel)


def ergste(uitslagen: list[Uitslag]) -> str:
    if not uitslagen:
        return OK
    return max((u.niveau for u in uitslagen), key=lambda n: _ERNST[n])


@dataclass(frozen=True)
class RegelWaarde:
    code: str
    waarde: int
    eenheid: str
    status: str
    bron: str
    omschrijving: str


class RegelBoek:
    """Leest alle regels één keer uit de database en zoekt de geldige waarde op een datum."""

    def __init__(self, regels: list[Regel]):
        self._per_code: dict[str, list[Regel]] = {}
        for r in regels:
            self._per_code.setdefault(r.code, []).append(r)

    @classmethod
    def laad(cls, db: Session) -> "RegelBoek":
        return cls(list(db.scalars(select(Regel))))

    def get(self, code: str, datum: date) -> RegelWaarde | None:
        kandidaten = [
            r for r in self._per_code.get(code, [])
            if r.in_gebruik and r.waarde is not None and r.geldig_van <= datum
            and (r.geldig_tot is None or datum <= r.geldig_tot)
        ]
        if not kandidaten:
            return None
        r = max(kandidaten, key=lambda x: x.geldig_van)  # de nieuwste geldige regel
        return RegelWaarde(r.code, r.waarde, r.eenheid, r.status, r.bron, r.omschrijving)

    def waarde(self, code: str, datum: date, standaard: int | None = None) -> int | None:
        rw = self.get(code, datum)
        return rw.waarde if rw else standaard


def kg_tekst(kg: int) -> str:
    return f"{kg:,} kg".replace(",", ".")


def ton_tekst(kg: int) -> str:
    return f"{kg / 1000:.1f} t".replace(".", ",")
