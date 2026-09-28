"""Controle via de gratis RDW Open Data API.

Dataset "Gekentekende voertuigen": https://opendata.rdw.nl/resource/m9d7-ebf2.json
Je hebt geen account of sleutel nodig.
"""

from datetime import date

from .normaliseren import toon_kenteken

RDW_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"


def haal_op(ophaler, kenteken):
    """Geeft de RDW-gegevens (dictionary) terug, of {} als het kenteken niet bestaat."""
    # RDW is een open API, bedoeld om zo te gebruiken. Wel dezelfde wachttijd.
    data = ophaler.haal(RDW_URL, params={"kenteken": kenteken}, controleer_robots=False, json_verwacht=True)
    return data[0] if data else {}


def _datum(waarde):
    """'20140314' -> date(2014, 3, 14)."""
    if not waarde:
        return None
    w = str(waarde)[:10].replace("-", "")
    try:
        return date(int(w[:4]), int(w[4:6]), int(w[6:8]))
    except ValueError:
        return None


def _maanden_tussen(van, tot):
    return (tot.year - van.year) * 12 + (tot.month - van.month) - (tot.day < van.day)


def controleer(auto, gegevens, inst, vandaag=None):
    """Vergelijkt RDW met de advertentie. Geeft een lijst met (in_orde, tekst) terug."""
    vandaag = vandaag or date.today()
    kenteken = toon_kenteken(auto["kenteken"])
    if not gegevens:
        return [(False, f"Kenteken {kenteken} niet gevonden bij de RDW. Klopt het kenteken wel?")]

    uit = []
    merk_rdw = (gegevens.get("merk") or "").lower()
    if auto["merk"] and merk_rdw and auto["merk"].lower() not in merk_rdw:
        uit.append((False, f"Merk klopt niet: advertentie zegt {auto['merk']}, RDW zegt {gegevens.get('merk')}"))
    else:
        uit.append((True, f"Merk klopt ({gegevens.get('merk', '?')} {gegevens.get('handelsbenaming', '')})".strip()))

    toelating = _datum(gegevens.get("datum_eerste_toelating"))
    if toelating and auto["bouwjaar"]:
        if toelating.year == auto["bouwjaar"]:
            uit.append((True, f"Datum eerste toelating ({toelating:%d-%m-%Y}) klopt met bouwjaar {auto['bouwjaar']}"))
        else:
            uit.append((False, f"Advertentie zegt bouwjaar {auto['bouwjaar']}, "
                               f"RDW zegt eerste toelating {toelating:%d-%m-%Y}"))

    apk = _datum(gegevens.get("vervaldatum_apk"))
    grens = inst["rdw"]["apk_waarschuwing_maanden"]
    if apk is None:
        uit.append((False, "Geen APK-datum bekend bij de RDW"))
    elif apk < vandaag:
        uit.append((False, f"APK is VERLOPEN sinds {apk:%d-%m-%Y}"))
    elif _maanden_tussen(vandaag, apk) < grens:
        uit.append((False, f"APK verloopt op {apk:%d-%m-%Y}, binnen {grens} maanden"))
    else:
        uit.append((True, f"APK geldig tot {apk:%d-%m-%Y}"))

    oordeel = gegevens.get("tellerstandoordeel")
    if oordeel:
        if "onlogisch" in oordeel.lower():
            uit.append((False, f"Tellerstand-oordeel RDW: {oordeel} (mogelijk teruggedraaide km-teller!)"))
        elif "logisch" in oordeel.lower():
            uit.append((True, f"Tellerstand-oordeel RDW: {oordeel}"))

    if str(gegevens.get("openstaande_terugroepactie_indicator", "")).lower() == "ja":
        uit.append((False, "Er staat een terugroepactie open bij de RDW"))

    if str(gegevens.get("export_indicator", "")).lower() == "ja":
        uit.append((False, "RDW: auto staat gemeld voor export"))

    return uit
