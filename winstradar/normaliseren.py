"""Haalt nette gegevens uit rommelige advertentietekst.

Mensen schrijven "1.2 TSI", "1,2tsi" of "1.2 benzine". Deze functies
maken daar iets van waar de tool mee kan rekenen.
"""

import re

from .generaties import bepaal_generatie

# Woorden die op een turbomotor wijzen. "1.2 TSI" en "1.2 TCe" zijn totaal
# andere motoren dan "1.2 16V", ook al is de inhoud hetzelfde.
TURBO_WOORDEN = ["tsi", "tfsi", "tce", "ecoboost", "turbo", "gti", "gt line"]
DIESEL_WOORDEN = ["diesel", "tdi", "dci", "tdci", "cdti", "d-4d", "d4d", "crdi", "hdi"]
HYBRIDE_WOORDEN = ["hybrid", "hybride"]
MOTOR_WOORDEN = set(TURBO_WOORDEN + DIESEL_WOORDEN + HYBRIDE_WOORDEN +
                    ["vvt-i", "vvti", "16v", "12v", "mpi", "sce", "ecotec", "sidi", "fsi", "tfsi"])
AUTOMAAT_WOORDEN = ["automaat", "automatic", "dsg", "cvt", "edc", "powershift",
                    "easytronic", "multidrive", "aut.", "tiptronic"]


def lees_getal(tekst):
    """'142.000 km' -> 142000. Geen getal? Dan None."""
    if tekst is None:
        return None
    if isinstance(tekst, (int, float)):
        return int(tekst)
    cijfers = re.sub(r"[^\d]", "", str(tekst))
    return int(cijfers) if cijfers else None


def bevat_woord(tekst, woorden):
    tekst = tekst.lower()
    return any(re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", tekst) for w in woorden)


def herken_brandstof(waarde, tekst):
    """Eerst het veld van de site, anders zoeken in de tekst."""
    if waarde:
        w = waarde.lower()
        for naam in ["hybride", "benzine", "diesel", "lpg", "elektrisch"]:
            if naam[:5] in w:
                return naam
        if "hybrid" in w:
            return "hybride"
        if "electr" in w:
            return "elektrisch"
    if bevat_woord(tekst, HYBRIDE_WOORDEN):
        return "hybride"
    if bevat_woord(tekst, DIESEL_WOORDEN):
        return "diesel"
    if bevat_woord(tekst, ["lpg"]):
        return "lpg"
    if bevat_woord(tekst, ["benzine", "tsi", "tce", "ecoboost", "vvt-i", "vvti", "16v", "mpi"]):
        return "benzine"
    return None


def herken_transmissie(waarde, tekst):
    if waarde:
        w = waarde.lower()
        if "auto" in w:
            return "automaat"
        if "hand" in w or "manu" in w:
            return "handgeschakeld"
    if bevat_woord(tekst, AUTOMAAT_WOORDEN):
        return "automaat"
    if bevat_woord(tekst, ["handgeschakeld", "handbak", "manual", "5-bak", "6-bak", "5 bak", "6 bak"]):
        return "handgeschakeld"
    return None


def herken_motor(tekst, cilinderinhoud=None, brandstof=None):
    """Geeft (motor zoals geschreven, motor_sleutel) terug.

    motor_sleutel is waar de tool op vergelijkt, bv. "1.2 turbo".
    """
    laag = tekst.lower().replace(",", ".")
    inhoud = None
    geschreven = None
    m = re.search(r"(?<![\d.])([0-3]\.\d{1,2})(?![\d.])\s*([a-z][a-z0-9\-]*)?", laag)
    if m:
        inhoud = f"{float(m.group(1)):.1f}"
        # Voor de weergave: "1.2 TSI" als er een motorwoord achter staat, anders "1.2"
        if m.group(2) and m.group(2) in MOTOR_WOORDEN:
            geschreven = f"{m.group(1)} {m.group(2).upper()}"
        else:
            geschreven = m.group(1)
    elif cilinderinhoud:
        cc = lees_getal(cilinderinhoud)
        if cc and 500 < cc < 4000:
            inhoud = f"{cc / 1000:.1f}"
            geschreven = f"{inhoud} ({cc} cc)"

    if brandstof == "hybride" or bevat_woord(laag, HYBRIDE_WOORDEN):
        soort = "hybride"
    elif brandstof == "diesel" or bevat_woord(laag, DIESEL_WOORDEN):
        soort = "diesel"
    elif bevat_woord(laag, TURBO_WOORDEN):
        soort = "turbo"
    else:
        soort = ""

    if inhoud is None:
        # Een hybride Yaris schrijft vaak geen motorinhoud; die heeft er maar één.
        if soort == "hybride":
            return (geschreven or "Hybrid"), "hybride"
        return None, None
    sleutel = f"{inhoud} {soort}".strip()
    return geschreven, sleutel


KENTEKEN_STREEPJES = re.compile(r"(?<![A-Z0-9-])([A-Z0-9]{1,3})-([A-Z0-9]{1,3})-([A-Z0-9]{1,3})(?![A-Z0-9-])")
KENTEKEN_NA_WOORD = re.compile(r"kenteken\s*:?\s*([A-Z0-9]{1,3}-?[A-Z0-9]{1,3}-?[A-Z0-9]{1,3})", re.I)


def _is_geldig_kenteken(delen):
    samen = "".join(delen)
    if len(samen) != 6:
        return False
    # Elk deel is helemaal letters of helemaal cijfers
    if not all(d.isalpha() or d.isdigit() for d in delen):
        return False
    # Er moeten letters én cijfers in zitten
    return any(d.isalpha() for d in delen) and any(d.isdigit() for d in delen)


def zoek_kenteken(tekst):
    """Zoekt een Nederlands kenteken in tekst. Geeft bv. 'KX218T' terug of None."""
    if not tekst:
        return None
    m = KENTEKEN_NA_WOORD.search(tekst)
    if m:
        kandidaat = m.group(1).upper()
        delen = kandidaat.split("-") if "-" in kandidaat else None
        if delen and _is_geldig_kenteken(delen):
            return "".join(delen)
        if not delen and len(kandidaat) == 6 and not kandidaat.isdigit() and not kandidaat.isalpha():
            return kandidaat
    for m in KENTEKEN_STREEPJES.finditer(tekst.upper()):
        if _is_geldig_kenteken(m.groups()):
            return "".join(m.groups())
    return None


def maak_kenteken_netjes(kenteken):
    """'KX-218-t' -> 'KX218T'."""
    if not kenteken:
        return None
    k = re.sub(r"[^A-Za-z0-9]", "", kenteken).upper()
    return k if len(k) == 6 else None


def toon_kenteken(k):
    """'KX218T' -> 'KX-218-T' (streepjes waar letters en cijfers wisselen)."""
    if not k:
        return ""
    groepen = re.findall(r"[A-Z]+|\d+", k)
    if len(groepen) == 3:
        return "-".join(groepen)
    if len(groepen) == 2:  # bv. 'XXXX99' -> 'XX-XX-99'
        a, b = groepen
        if len(a) == 4:
            return f"{a[:2]}-{a[2:]}-{b}"
        if len(b) == 4:
            return f"{a}-{b[:2]}-{b[2:]}"
    return f"{k[:2]}-{k[2:4]}-{k[4:]}"


def herken_uitvoering(titel, merk, model, motor):
    rest = titel
    for deel in [merk, model, motor]:
        if deel:
            rest = re.sub(re.escape(deel), " ", rest, flags=re.I)
    rest = re.sub(r"\s+", " ", rest).strip(" -|,")
    return rest[:60] or None


def vul_aan(adv, merk, model):
    """Vult de ontbrekende velden van een Advertentie in."""
    tekst = f"{adv.titel} {adv.beschrijving}"
    adv.merk = merk
    adv.model = model
    adv.brandstof = herken_brandstof(adv.brandstof, tekst)
    adv.transmissie = herken_transmissie(adv.transmissie, tekst)
    if not adv.motor_sleutel:
        cc = adv.extra.get("cilinderinhoud")
        # Eerst in de titel zoeken; daar staat de motor meestal goed.
        motor, sleutel = herken_motor(adv.titel, cc, adv.brandstof)
        if sleutel is None:
            motor, sleutel = herken_motor(tekst, cc, adv.brandstof)
        adv.motor, adv.motor_sleutel = motor, sleutel
    adv.generatie = bepaal_generatie(merk, model, adv.bouwjaar, tekst)
    adv.uitvoering = herken_uitvoering(adv.titel, merk, model, adv.motor)
    adv.kenteken = maak_kenteken_netjes(adv.kenteken) or zoek_kenteken(tekst)
    return adv
