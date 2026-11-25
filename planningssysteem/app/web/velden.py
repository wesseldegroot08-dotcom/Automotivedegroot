"""Formuliervelden beschrijven en controleren met Pydantic.

We beschrijven per scherm welke velden er zijn. Daarmee maken we:
- het formulier (welke invoer, welke keuzelijst),
- de controle (met Pydantic, met foutmeldingen in simpel Nederlands),
- de lijst (welke kolommen).
Zo hoeven we niet 20 keer hetzelfde scherm te bouwen.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, ValidationError, create_model

from app.ports.clock import NL


@dataclass
class Veld:
    naam: str
    label: str
    soort: str = "tekst"  # tekst, lang, getal, kommagetal, datum, tijd, datumtijd, bool, keuze, fk
    verplicht: bool = False
    keuzes: list[str] | None = None
    fk_model: Any = None
    fk_label: Any = None  # functie: object -> tekst
    hulp: str = ""
    in_lijst: bool = False
    min: int | None = None
    max: int | None = None


def _leeg_naar_none(v):
    if isinstance(v, str) and v.strip() == "":
        return None
    return v.strip() if isinstance(v, str) else v


def _naar_bool(v):
    return v in (True, "on", "true", "1", "ja", 1)


def _datumtijd_nl(v):
    """Een tijd uit het formulier is Nederlandse tijd. Zet hem om naar een tijd met tijdzone."""
    v = _leeg_naar_none(v)
    if v is None or isinstance(v, datetime):
        return v
    dt = datetime.fromisoformat(v)
    return dt.replace(tzinfo=NL) if dt.tzinfo is None else dt


def _type_voor(veld: Veld):
    basis: Any
    if veld.soort in ("tekst", "lang"):
        basis = str
    elif veld.soort in ("getal", "fk"):
        basis = Annotated[int, Field(ge=veld.min, le=veld.max)]
    elif veld.soort == "kommagetal":
        basis = float
    elif veld.soort == "datum":
        basis = date
    elif veld.soort == "tijd":
        basis = time
    elif veld.soort == "datumtijd":
        basis = datetime
    elif veld.soort == "bool":
        return Annotated[bool, BeforeValidator(_naar_bool)], False
    elif veld.soort == "keuze":
        basis = Literal[tuple(veld.keuzes)]  # type: ignore[misc]
    else:
        raise ValueError(veld.soort)
    voorbewerking = _datumtijd_nl if veld.soort == "datumtijd" else _leeg_naar_none
    if veld.verplicht:
        return Annotated[basis, BeforeValidator(voorbewerking)], ...
    return Annotated[basis | None, BeforeValidator(voorbewerking)], None


FOUTEN = {
    "missing": "Dit veld is verplicht.",
    "string_type": "Dit veld is verplicht.",
    "int_parsing": "Vul een heel getal in (zonder punt of komma).",
    "int_from_float": "Vul een heel getal in (zonder punt of komma).",
    "int_type": "Dit veld is verplicht.",
    "float_parsing": "Vul een getal in.",
    "date_parsing": "Vul een geldige datum in.",
    "date_from_datetime_parsing": "Vul een geldige datum in.",
    "date_type": "Dit veld is verplicht.",
    "time_parsing": "Vul een geldige tijd in (uu:mm).",
    "time_type": "Dit veld is verplicht.",
    "datetime_parsing": "Vul een geldige datum en tijd in.",
    "datetime_from_date_parsing": "Vul een geldige datum en tijd in.",
    "datetime_type": "Dit veld is verplicht.",
    "value_error": "Deze waarde klopt niet.",
    "literal_error": "Kies een waarde uit de lijst.",
    "greater_than_equal": "Deze waarde is te laag.",
    "less_than_equal": "Deze waarde is te hoog.",
}


@dataclass
class Uitkomst:
    data: dict = field(default_factory=dict)
    fouten: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.fouten


def controleer(velden: list[Veld], invoer: dict) -> Uitkomst:
    """Controleer formulierinvoer. Geeft nette waarden of Nederlandse foutmeldingen."""
    definities = {v.naam: _type_voor(v) for v in velden}
    Model = create_model("Formulier", **definities)  # noqa: N806
    ruw = {v.naam: invoer.get(v.naam) for v in velden}
    for v in velden:
        if v.soort == "bool":
            ruw[v.naam] = invoer.get(v.naam, False)
    try:
        obj = Model(**ruw)
    except ValidationError as e:
        fouten = {}
        for fout in e.errors():
            naam = str(fout["loc"][0]) if fout["loc"] else ""
            fouten.setdefault(naam, FOUTEN.get(fout["type"], "Deze waarde klopt niet."))
        # Een leeg verplicht veld krijgt altijd dezelfde, duidelijke melding.
        for v in velden:
            if v.verplicht and v.soort != "bool" and (ruw.get(v.naam) is None or str(ruw[v.naam]).strip() == ""):
                fouten[v.naam] = FOUTEN["missing"]
        return Uitkomst(fouten=fouten)
    return Uitkomst(data=obj.model_dump())


def regel_velden() -> list[Veld]:
    """Velden die elke regel heeft (regels zijn data)."""
    from app.keuzes import STATUS_REGEL

    return [
        Veld("geldig_van", "Geldig van", "datum", verplicht=True, in_lijst=True),
        Veld("geldig_tot", "Geldig tot (leeg = geen einde)", "datum"),
        Veld("bron", "Bron (waar komt dit vandaan?)", "lang", verplicht=True),
        Veld("status", "Status", "keuze", verplicht=True, keuzes=STATUS_REGEL, in_lijst=True),
    ]
