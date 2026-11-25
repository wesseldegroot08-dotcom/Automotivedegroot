"""OrderExtractor: haalt ordergegevens uit geplakte e-mailtekst.

In de testversie een eenvoudige uitlezer met reguliere expressies. Later kan hier een taalmodel of
document-AI achter, met dezelfde interface (lees). De controles daarna (ISO 6346, terminallijst, ...)
doet altijd gewone code, en een mens keurt goed.
"""

import re
from dataclasses import dataclass, field
from datetime import date, time
from typing import Protocol


@dataclass
class Uitgelezen:
    velden: dict[str, str] = field(default_factory=dict)
    gevonden_containers: list[str] = field(default_factory=list)
    twijfel: list[str] = field(default_factory=list)  # wat de uitlezer niet zeker weet


class OrderExtractor(Protocol):
    naam: str

    def lees(self, tekst: str, terminals: dict[str, str], locaties: dict[str, str],
             klanten: dict[str, str]) -> Uitgelezen: ...


CONTAINER = re.compile(r"\b([A-Z]{3}[UJZ])\s?(\d{6})\s?(\d)\b")
REFERENTIE = re.compile(r"\b(?:onze\s+ref(?:erentie)?|uw\s+ref(?:erentie)?|referentie|ref\.?|order(?:nummer|nr)?)"
                        r"\s*[:#]?\s*([A-Z0-9][A-Z0-9\-/]{2,30})", re.I)
BOEKING = re.compile(r"(?:B/?L|bill of lading|booking|boeking)(?:\s*(?:nr|nummer|number|no))?\.?\s*[:#]?\s*"
                     r"([A-Z0-9]{6,20})", re.I)
DATUM = re.compile(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b")
VENSTER = re.compile(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\s*(?:-|tot|t/m|en)\s*([01]?\d|2[0-3])[:.]([0-5]\d)\b")
TIJD = re.compile(r"\b(?:om|vanaf|rond)\s+([01]?\d|2[0-3])[:.]([0-5]\d)\b", re.I)
MAAT_TYPE = re.compile(r"\b(20|40|45)\s?(?:ft|'|voet)?\s?(DC|DV|GP|HC|HQ|RF|reefer|tank|dry)\b", re.I)
ISO_TYPE = re.compile(r"\b(22|25|42|45|L5)(G1|R1|T1)\b")
GEWICHT = re.compile(r"\b(?:VGM|gewicht|bruto|weight)\s*[:]?\s*(\d{1,2}[.,]?\d{3})\s*kg\b", re.I)
GEWICHT_LOS = re.compile(r"\b(\d{1,2}[.,]\d{3})\s*kg\b", re.I)

TYPE_WOORDEN = {"dc": "DC", "dv": "DC", "gp": "DC", "dry": "DC", "hc": "HC", "hq": "HC", "rf": "reefer",
                "reefer": "reefer", "tank": "tank"}
# ISO-typecode -> (maat, type). Let op: 45G1 is een 40ft High Cube, geen 45ft.
ISO_CODES = {"22G1": ("20", "DC"), "42G1": ("40", "DC"), "45G1": ("40", "HC"), "L5G1": ("45", "HC"),
             "22R1": ("20", "reefer"), "45R1": ("40", "reefer"), "22T1": ("20", "tank")}


def _zoek_naam(tekst: str, namen: dict[str, str]) -> str | None:
    """namen: zoekwoord (kleine letters) -> id. Langste treffer wint."""
    laag = tekst.lower()
    treffers = [(len(k), v) for k, v in namen.items() if k and k in laag]
    return max(treffers)[1] if treffers else None


class RegexExtractor:
    naam = "regex"

    def lees(self, tekst: str, terminals: dict[str, str], locaties: dict[str, str],
             klanten: dict[str, str]) -> Uitgelezen:
        u = Uitgelezen()
        v = u.velden
        u.gevonden_containers = list(dict.fromkeys("".join(g) for g in CONTAINER.findall(tekst.upper())))
        if u.gevonden_containers:
            v["containernummer"] = u.gevonden_containers[0]
            if len(u.gevonden_containers) > 1:
                u.twijfel.append(f"Meer dan één containernummer gevonden: {', '.join(u.gevonden_containers)}. "
                                 "Alleen de eerste is ingevuld.")
        if (r := REFERENTIE.search(tekst)):
            v["klantreferentie"] = r.group(1).strip(".,")
        if (b := BOEKING.search(tekst)):
            v["boeking_bl"] = b.group(1)
        if (d := DATUM.search(tekst)):
            try:
                v["datum"] = date(int(d.group(3)), int(d.group(2)), int(d.group(1))).isoformat()
            except ValueError:
                u.twijfel.append(f"Datum '{d.group(0)}' bestaat niet.")
        if (w := VENSTER.search(tekst)):
            v["venster_van"] = time(int(w.group(1)), int(w.group(2))).strftime("%H:%M")
            v["venster_tot"] = time(int(w.group(3)), int(w.group(4))).strftime("%H:%M")
        elif (t := TIJD.search(tekst)):
            v["venster_van"] = time(int(t.group(1)), int(t.group(2))).strftime("%H:%M")
            u.twijfel.append("Alleen een begintijd gevonden, geen eindtijd.")
        if (iso := ISO_TYPE.search(tekst.upper())) and iso.group(0) in ISO_CODES:
            v["maat"], v["container_type"] = ISO_CODES[iso.group(0)]
        elif (mt := MAAT_TYPE.search(tekst)):
            v["maat"], v["container_type"] = mt.group(1), TYPE_WOORDEN[mt.group(2).lower()]
        if (g := GEWICHT.search(tekst) or GEWICHT_LOS.search(tekst)):
            v["vgm_kg"] = g.group(1).replace(".", "").replace(",", "")
        laag = tekst.lower()
        if "export" in laag or "lading brengen" in laag or "beladen" in laag:
            v["type"] = "export"
        elif "leeg" in laag and ("retour" in laag or "terug" in laag):
            v["type"] = "leeg"
        elif "import" in laag or "ophalen" in laag or "afhalen" in laag:
            v["type"] = "import"
        terminal = _zoek_naam(tekst, terminals)
        locatie = _zoek_naam(tekst, locaties)
        klant = _zoek_naam(tekst, klanten)
        if klant:
            v["klant_id"] = klant
        if terminal:
            v["terminal_id"] = terminal
        if locatie:
            v["klantlocatie_id"] = locatie
        if not terminal:
            u.twijfel.append("Geen bekende terminal gevonden in de tekst.")
        return u


def extractor() -> OrderExtractor:
    return RegexExtractor()
