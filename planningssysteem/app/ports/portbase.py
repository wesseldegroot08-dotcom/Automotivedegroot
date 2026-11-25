"""PortbaseGateway: pre-notificatie naar de terminal. In de testversie is dit een SIMULATOR.

Gedrag zoals bij ECT (stand 23 november 2026):
- Geen aparte slotboeking. Het slot volgt uit de ETA in de pre-notificatie. TAR en slot zijn alleen-lezen.
- Antwoordcodes: COR (correct, slot toegekend), CDM (containergegevens kloppen niet), BLT (geblokkeerd,
  bijvoorbeeld release niet vrij).
- Een ETA wijzigen kan alleen door annuleren en opnieuw sturen met hetzelfde label.
Een echte koppeling moet dezelfde interface krijgen (stuur_prenotificatie en annuleer).
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Protocol

from app.ports.clock import NL
from app.rules.iso6346 import controleer_containernummer


@dataclass
class PreNotificatie:
    label: str
    terminalcode: str
    handlingtype: str  # ophalen / brengen
    containernummers: list[str]
    eta: datetime
    release_vrij: bool
    slotlengte_min: int
    capaciteit_per_slot: int | None
    bezette_slots: dict[datetime, int]  # slot-begin -> aantal al toegekend


@dataclass
class Antwoord:
    code: str  # COR, CDM, BLT
    toegekend: bool
    tekst: str
    tar: str | None = None
    slot_van: datetime | None = None
    slot_tot: datetime | None = None


class PortbaseGateway(Protocol):
    def stuur_prenotificatie(self, pn: PreNotificatie) -> Antwoord: ...

    def annuleer(self, label: str) -> Antwoord: ...


class PortbaseSimulator:
    """Nep-Portbase. Geeft altijd hetzelfde antwoord op dezelfde vraag (geen toeval)."""

    naam = "simulator"

    def stuur_prenotificatie(self, pn: PreNotificatie) -> Antwoord:
        for nr in pn.containernummers:
            if not controleer_containernummer(nr).geldig:
                return Antwoord("CDM", False, f"Container {nr}: nummer klopt niet (ISO 6346).")
        if not pn.containernummers:
            return Antwoord("CDM", False, "Geen containernummer in de pre-notificatie.")
        if pn.handlingtype == "ophalen" and not pn.release_vrij:
            return Antwoord("BLT", False, "Container is geblokkeerd: release, douane of terminal niet vrij.")
        lengte = pn.slotlengte_min or 120
        lokaal = pn.eta.astimezone(NL)
        middernacht = datetime.combine(lokaal.date(), time()).replace(tzinfo=NL)
        minuten = int((lokaal - middernacht).total_seconds() // 60)
        begin = middernacht + timedelta(minutes=(minuten // lengte) * lengte)
        verschoven = False
        if pn.capaciteit_per_slot:
            while pn.bezette_slots.get(begin, 0) >= pn.capaciteit_per_slot:
                begin += timedelta(minutes=lengte)
                verschoven = True
        tar = "TAR-SIM-" + hashlib.sha1(f"{pn.label}|{begin.isoformat()}".encode()).hexdigest()[:8].upper()
        tekst = "Pre-notificatie correct. Slot toegekend op basis van de ETA."
        if verschoven:
            tekst += " Het slot van de ETA was vol: het volgende vrije slot is gegeven."
        return Antwoord("COR", True, tekst, tar, begin, begin + timedelta(minutes=lengte))

    def annuleer(self, label: str) -> Antwoord:
        return Antwoord("COR", True, f"Pre-notificatie {label} geannuleerd.")


_gateway: PortbaseGateway = PortbaseSimulator()


def gateway() -> PortbaseGateway:
    return _gateway


def zet_gateway(g: PortbaseGateway) -> None:
    global _gateway
    _gateway = g
