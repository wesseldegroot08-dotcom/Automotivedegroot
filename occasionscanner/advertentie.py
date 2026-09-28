"""De gegevens van één advertentie."""

from dataclasses import dataclass, field


@dataclass
class Advertentie:
    site: str                      # bijvoorbeeld "marktplaats"
    advertentie_id: str            # het nummer van de advertentie op die site
    link: str
    titel: str
    beschrijving: str = ""
    beschrijving_volledig: bool = False   # False = alleen een stukje uit de zoeklijst
    merk: str | None = None
    model: str | None = None
    generatie: str | None = None
    uitvoering: str | None = None
    motor: str | None = None              # zoals in de advertentie, bv. "1.2 TSI"
    motor_sleutel: str | None = None      # om te vergelijken, bv. "1.2 turbo"
    brandstof: str | None = None          # "benzine", "hybride", ...
    transmissie: str | None = None        # "handgeschakeld" of "automaat"
    bouwjaar: int | None = None
    kilometerstand: int | None = None
    vraagprijs: int | None = None         # in hele euro's
    locatie: str | None = None
    kenteken: str | None = None           # zonder streepjes, hoofdletters
    extra: dict = field(default_factory=dict)  # ruwe gegevens van de site
