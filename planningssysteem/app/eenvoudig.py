"""Gewone woorden voor het scherm. De regels zelf blijven precies; hier maken we er korte, duidelijke zinnen van."""

import re

REGEL_NAAM = {
    1: "Dubbel ingepland",
    2: "Past op de trailer",
    3: "Gewicht",
    4: "Gewicht per as",
    5: "Hoogte",
    7: "Rijtijd chauffeur",
    8: "Werktijd en pauze",
    9: "Tijdslot terminal",
    10: "Aangemeld bij terminal",
    11: "Container vrijgegeven",
    12: "Laatste gratis dag",
    13: "Op tijd bij de klant",
    14: "Gevaarlijke stoffen (ADR)",
    15: "Koelcontainer",
    16: "Pasjes chauffeur",
    17: "Rijverbod Duitsland",
    18: "Lege container terug",
    20: "Tol",
    21: "Duitsland: lange weg",
}

NIVEAU = {"ok": ("✔", "In orde"), "waarschuwing": ("⚠", "Let op"), "hard": ("⛔", "Mag niet")}

_VERVANG = [
    (re.compile(r"\bchassis\b", re.I), "trailer"),
    (re.compile(r"\bChassis\b"), "Trailer"),
    (re.compile(r"\beenheid \(trekker \+ chassis\)", re.I), "trekker met trailer"),
    (re.compile(r"pre-notificatie", re.I), "aanmelding bij de terminal"),
    (re.compile(r"\bLFD\b"), "laatste gratis dag"),
    (re.compile(r"\brelease\b", re.I), "vrijgave"),
]


def woorden(tekst: str | None) -> str:
    """Vervang vakwoorden door gewone woorden."""
    if not tekst:
        return ""
    for patroon, nieuw in _VERVANG:
        tekst = patroon.sub(nieuw, tekst)
    return tekst


def kort_reden(reden: str | None) -> str:
    """Eén korte zin: waarom kan deze rit niet gepland worden?"""
    r = reden or ""
    laag = r.lower()
    if "geen eenheid" in laag:
        if "20ft" in laag or "twistlock" in laag:
            return "Past op geen enkele trailer (geen trailer voor deze container vrij)."
        if "zwaar" in laag or "gewicht" in laag:
            return "Te zwaar voor de trekkers en trailers die er zijn."
        return "Past op geen enkele trekker met trailer."
    if "release" in laag and "niet groen" in laag:
        return "Container is nog niet vrijgegeven (douane, rederij of terminal)."
    if "geen geschikte chauffeur" in laag:
        if "adr" in laag:
            return "Geen chauffeur met een geldig ADR-diploma vrij."
        if "ect" in laag or "cargocard" in laag:
            return "Geen chauffeur met de juiste pasjes voor deze terminal vrij."
        return "Geen geschikte chauffeur vrij."
    if "eigen trekker" in laag:
        return "De chauffeurs die het mogen, hebben niet de juiste trekker of trailer. Geef iemand een andere trekker."
    if "tijden passen niet samen" in laag:
        return "Tijdslot van de terminal en de tijd van de klant passen niet samen."
    if "gesloten" in laag:
        return "Het adres is dan gesloten."
    if "geen ruimte" in laag:
        return "Alle geschikte chauffeurs zijn al bezet in de tijd van de klant."
    if "exacte controle" in laag:
        if "regel 7" in laag:
            return "Past niet binnen de rijtijd van een chauffeur."
        return "Haalt de controle niet (bijvoorbeeld gewicht of rijtijd)."
    if "vaste" in laag and "passen niet samen" in laag:
        return "De vastgezette ritten passen niet samen. Kijk op het planbord."
    eerste = re.split(r"(?<=[.!?])\s", woorden(r), maxsplit=1)[0]
    return eerste[:160]


def regel_zin(nr: int, uitleg: str) -> str:
    """Korte zin voor één regel, voor in de lijst 'Moet jij naar kijken'."""
    u = woorden(uitleg).replace("Niet toegestaan: ", "")
    if nr == 9 and "geen slot" in uitleg.lower():
        return "Nog geen tijdslot bij de terminal. Wordt aangevraagd als je akkoord geeft."
    if nr == 10:
        return "Nog niet aangemeld bij de terminal."
    if nr == 12:
        return u
    return f"{REGEL_NAAM.get(nr, f'Regel {nr}')}: {u}"
