"""Containernummer controleren volgens ISO 6346 (Bevestigd).

Opbouw: 3 letters eigenaar + 1 letter categorie (U, J of Z) + 6 cijfers + 1 controlecijfer.
Rekenregel: geef elke letter een waarde (A=10, B=12, ... 11, 22 en 33 slaan we over).
Vermenigvuldig de waarde op positie i (0 t/m 9) met 2 tot de macht i. Tel alles op.
Neem de rest na delen door 11, en daarvan de rest na delen door 10. Dat is het controlecijfer.
"""

import re
from dataclasses import dataclass

LETTERWAARDEN = {
    "A": 10, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17, "H": 18, "I": 19,
    "J": 20, "K": 21, "L": 23, "M": 24, "N": 25, "O": 26, "P": 27, "Q": 28, "R": 29,
    "S": 30, "T": 31, "U": 32, "V": 34, "W": 35, "X": 36, "Y": 37, "Z": 38,
}

_PATROON = re.compile(r"^[A-Z]{3}[UJZ][0-9]{7}$")


@dataclass
class Uitslag:
    geldig: bool
    melding: str
    genormaliseerd: str = ""


def bereken_controlecijfer(eerste_tien: str) -> int:
    totaal = 0
    for i, teken in enumerate(eerste_tien):
        waarde = LETTERWAARDEN[teken] if teken.isalpha() else int(teken)
        totaal += waarde * (2**i)
    return (totaal % 11) % 10


def controleer_containernummer(nummer: str) -> Uitslag:
    schoon = re.sub(r"[\s\-]", "", (nummer or "")).upper()
    if len(schoon) != 11:
        return Uitslag(False, f"Een containernummer heeft 11 tekens. Dit nummer heeft er {len(schoon)}.")
    if not _PATROON.match(schoon):
        return Uitslag(False, "Verkeerde opbouw. Het moet zijn: 3 letters, dan U, J of Z, dan 7 cijfers. "
                              "Voorbeeld: CSQU3054383.")
    verwacht = bereken_controlecijfer(schoon[:10])
    if int(schoon[10]) != verwacht:
        return Uitslag(False, f"Controlecijfer klopt niet: het laatste cijfer moet {verwacht} zijn, "
                              f"niet {schoon[10]}. Controleer het nummer.")
    return Uitslag(True, "Geldig containernummer.", schoon)
