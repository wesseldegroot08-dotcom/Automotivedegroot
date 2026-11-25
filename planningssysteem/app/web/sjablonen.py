"""Jinja2-sjablonen en kleine hulpjes om getallen netjes te tonen."""

from datetime import date, datetime, time

from fastapi.templating import Jinja2Templates

from app.config import BASIS_MAP
from app.ports.clock import NL

templates = Jinja2Templates(directory=str(BASIS_MAP / "app" / "templates"))


def kg(waarde: int | None) -> str:
    """12345 -> '12.345 kg'"""
    if waarde is None:
        return "onbekend"
    return f"{waarde:,} kg".replace(",", ".")


def geld(cent: int | None) -> str:
    """12345 -> '€ 123,45'"""
    if cent is None:
        return "onbekend"
    teken = "-" if cent < 0 else ""
    cent = abs(cent)
    euro, rest = divmod(cent, 100)
    return f"{teken}€ {euro:,}".replace(",", ".") + f",{rest:02d}"


def tijd_nl(waarde) -> str:
    """Toon een UTC-tijd in Nederlandse tijd."""
    if waarde is None:
        return ""
    if isinstance(waarde, datetime):
        return waarde.astimezone(NL).strftime("%d-%m-%Y %H:%M")
    if isinstance(waarde, date):
        return waarde.strftime("%d-%m-%Y")
    if isinstance(waarde, time):
        return waarde.strftime("%H:%M")
    return str(waarde)


def uur_nl(waarde) -> str:
    if waarde is None:
        return ""
    return waarde.astimezone(NL).strftime("%H:%M")


def minuten(m: int | None) -> str:
    """135 -> '2 u 15 min'"""
    if m is None:
        return "onbekend"
    teken = "-" if m < 0 else ""
    u, r = divmod(abs(int(m)), 60)
    return f"{teken}{u} u {r:02d} min" if u else f"{teken}{r} min"


DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober",
           "november", "december"]


def dag_nl(d) -> str:
    """date -> 'donderdag 26 november'"""
    return f"{DAGEN[d.weekday()]} {d.day} {MAANDEN[d.month - 1]}"


def dag_titel(d) -> str:
    """'Morgen', 'Vandaag' of de dag zelf."""
    from app.ports.clock import morgen_nl, vandaag_nl

    if d == morgen_nl():
        return f"Morgen · {dag_nl(d)}"
    if d == vandaag_nl():
        return f"Vandaag · {dag_nl(d)}"
    return dag_nl(d).capitalize()


def _woorden(t):
    from app.eenvoudig import woorden

    return woorden(t)


templates.env.filters.update(kg=kg, geld=geld, tijd_nl=tijd_nl, uur_nl=uur_nl, minuten=minuten, dag_nl=dag_nl,
                             dag_titel=dag_titel, woorden=_woorden)
