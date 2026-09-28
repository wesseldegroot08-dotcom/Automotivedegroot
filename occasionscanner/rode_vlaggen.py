"""Rode vlaggen: dingen waar je extra goed naar moet kijken voordat je koopt."""

import re


def gevonden_woorden(tekst, inst):
    """Welke rode-vlag-woorden staan in de tekst? Uitzonderingen (bv. 'schadevrij') tellen niet."""
    rv = inst["rode_vlaggen"]
    laag = (tekst or "").lower()
    for uitzondering in rv["uitzonderingen"]:
        laag = laag.replace(uitzondering.lower(), " ")
    gevonden = []
    for woord in rv["woorden"]:
        # Woord moet los staan: "schade" wel, "schadevrij" niet (die is hierboven al weggehaald)
        if re.search(rf"(?<![a-z]){re.escape(woord.lower())}(?![a-z])", laag):
            gevonden.append(woord)
    return gevonden


def controleer(auto, inst, mediaan=None):
    """Geeft een lijst met rode vlaggen (teksten) terug."""
    rv = inst["rode_vlaggen"]
    vlaggen = []

    if mediaan and auto["vraagprijs"]:
        onder = (1 - auto["vraagprijs"] / mediaan) * 100
        if onder > rv["verdacht_goedkoop_procent"]:
            vlaggen.append(f"Prijs {onder:.0f}% onder vergelijkbare auto's (oplichting of verborgen schade?)")

    for woord in gevonden_woorden(f"{auto['titel']} {auto['beschrijving']}", inst):
        vlaggen.append(f"Woord in advertentie: “{woord}”")

    if auto["kilometerstand"] is None:
        vlaggen.append("Geen kilometerstand vermeld")

    # Alleen beoordelen als we de volledige beschrijving hebben, niet het korte stukje uit de zoeklijst.
    if auto["beschrijving_volledig"]:
        aantal = len((auto["beschrijving"] or "").split())
        if aantal < rv["min_woorden_beschrijving"]:
            vlaggen.append(f"Vage beschrijving (maar {aantal} woorden)")

    return vlaggen
