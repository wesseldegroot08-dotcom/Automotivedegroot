"""Klok (poort). Tests kunnen zo zelf bepalen hoe laat het is."""

from datetime import UTC, date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

NL = ZoneInfo("Europe/Amsterdam")


class Clock(Protocol):
    def nu(self) -> datetime: ...


class SysteemKlok:
    def nu(self) -> datetime:
        return datetime.now(UTC)


class VasteKlok:
    """Een klok die stilstaat. Handig in tests."""

    def __init__(self, moment: datetime):
        self.moment = moment

    def nu(self) -> datetime:
        return self.moment


_klok: Clock = SysteemKlok()


def klok() -> Clock:
    return _klok


def zet_klok(nieuwe: Clock) -> None:
    global _klok
    _klok = nieuwe


def vandaag_nl() -> date:
    return klok().nu().astimezone(NL).date()


def morgen_nl() -> date:
    return vandaag_nl() + timedelta(days=1)


def nl_tijd(d: date, uur: int, minuut: int = 0) -> datetime:
    """Maak een tijd in Nederlandse tijd en zet hem om naar UTC."""
    return datetime(d.year, d.month, d.day, uur, minuut, tzinfo=NL).astimezone(UTC)
