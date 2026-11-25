"""Statussen met vaste stappen (state machines).

Elke soort heeft een lijst van toegestane overgangen. Een andere overgang geeft een
duidelijke foutmelding en wordt NIET opgeslagen.
"""

OVERGANGEN: dict[str, dict[str, set[str]]] = {
    "order": {
        "Nieuw": {"Gepland", "Geannuleerd", "Geblokkeerd", "Probleem"},
        "Gepland": {"Onderweg", "Nieuw", "Geannuleerd", "Geblokkeerd", "Probleem"},
        "Onderweg": {"Op terminal", "Bij klant", "Probleem"},
        "Op terminal": {"Onderweg", "Bij klant", "Geleverd", "Probleem"},
        "Bij klant": {"Onderweg", "Op terminal", "Geleverd", "Probleem"},
        "Geleverd": {"Leeg retour", "Afgerond"},
        "Leeg retour": {"Afgerond"},
        "Afgerond": {"Gefactureerd"},
        "Gefactureerd": set(),
        "Geannuleerd": set(),
        "Geblokkeerd": {"Nieuw", "Geannuleerd"},
        "Probleem": {"Nieuw", "Gepland", "Geannuleerd"},
    },
    "order_concept": {
        "Ontvangen": {"Gelezen"},
        "Gelezen": {"Te controleren", "Goedgekeurd"},
        "Te controleren": {"Goedgekeurd", "Afgekeurd"},
        "Goedgekeurd": set(),
        "Afgekeurd": set(),
    },
    "rit": {
        "Concept": {"Gepland"},
        "Gepland": {"Geaccepteerd", "Concept", "Onderweg"},
        "Geaccepteerd": {"Onderweg", "Gepland"},
        "Onderweg": {"Aangekomen", "Slot gemist"},
        "Aangekomen": {"In behandeling", "Geweigerd door terminal"},
        "In behandeling": {"Klaar"},
        "Klaar": {"Afgerond", "Onderweg"},
        "Afgerond": set(),
        "Geweigerd door terminal": {"Concept", "Gepland"},
        "Slot gemist": {"Concept", "Gepland"},
    },
    "container": {
        "Aangekondigd": {"Gelost", "Vrij"},
        "Gelost": {"Vrij"},
        "Vrij": {"Opgehaald"},
        "Opgehaald": {"Geleverd"},
        "Geleverd": {"Geladen of geleegd"},
        "Geladen of geleegd": {"Leeg retour afgemeld"},
        "Leeg retour afgemeld": set(),
    },
    "slot": {
        "Aangevraagd": {"Toegekend", "Geweigerd", "Geannuleerd"},
        "Toegekend": {"Gebruikt", "Gewijzigd", "Geannuleerd", "No-show"},
        "Gewijzigd": {"Toegekend", "Geannuleerd", "Gebruikt", "No-show"},
        "Gebruikt": set(),
        "Geweigerd": set(),
        "Geannuleerd": set(),
        "No-show": set(),
    },
    "release": {
        "Onbekend": {"Verwacht", "Vrij", "Geblokkeerd"},
        "Verwacht": {"Vrij", "Geblokkeerd"},
        "Vrij": {"Geblokkeerd"},
        "Geblokkeerd": {"Verwacht", "Vrij"},
    },
    "voorstel": {
        "Berekend": {"Voorgesteld"},
        "Voorgesteld": {"Goedgekeurd", "Afgekeurd"},
        "Goedgekeurd": {"Gepubliceerd"},
        "Afgekeurd": set(),
        "Gepubliceerd": set(),
    },
}

NAMEN = {"order": "order", "order_concept": "order-concept", "rit": "rit", "container": "container",
         "slot": "slot", "release": "release", "voorstel": "voorstel"}


class OngeldigeOvergang(ValueError):
    pass


def mag(soort: str, van: str, naar: str) -> bool:
    return naar in OVERGANGEN[soort].get(van, set())


def volgende(soort: str, van: str) -> list[str]:
    return sorted(OVERGANGEN[soort].get(van, set()))


def controleer_overgang(soort: str, van: str, naar: str) -> None:
    if soort not in OVERGANGEN:
        raise OngeldigeOvergang(f"Onbekende soort: {soort}.")
    if naar not in OVERGANGEN[soort]:
        raise OngeldigeOvergang(f"'{naar}' is geen bestaande status voor een {NAMEN[soort]}.")
    if not mag(soort, van, naar):
        toegestaan = ", ".join(volgende(soort, van)) or "geen (eindstatus)"
        raise OngeldigeOvergang(f"Een {NAMEN[soort]} kan niet van '{van}' naar '{naar}'. "
                                f"Toegestaan vanaf '{van}': {toegestaan}.")


def zet_status(obj, soort: str, naar: str, veld: str = "status") -> None:
    """Wijzig de status alleen als de overgang mag. Anders een fout, en er verandert niets."""
    van = getattr(obj, veld)
    controleer_overgang(soort, van, naar)
    setattr(obj, veld, naar)
