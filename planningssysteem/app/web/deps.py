"""Gedeelde stukjes voor alle pagina's: database, ingelogde gebruiker, rollen en CSRF."""

from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import db as dbmod
from app.auth import nieuw_csrf_token, tokens_gelijk
from app.models import Gebruiker


class NietIngelogd(Exception):
    """Wordt opgevangen in main.py: stuurt je naar de inlogpagina."""


def get_db(request: Request) -> Iterator[Session]:
    sessie = dbmod.SessionLocal()
    sessie.info["gebruiker"] = request.session.get("gebruikersnaam", "anoniem")
    try:
        yield sessie
    finally:
        sessie.close()


async def csrf_controle(request: Request) -> None:
    """Elke POST moet het juiste CSRF-token meesturen (formulierveld of HTMX-header)."""
    if request.method != "POST":
        return
    form = await request.form()
    token = form.get("csrf") or request.headers.get("X-CSRF-Token")
    if not tokens_gelijk(token, request.session.get("csrf")):
        raise HTTPException(status_code=403, detail="Formulier verlopen. Laad de pagina opnieuw.")


def csrf_token(request: Request) -> str:
    if "csrf" not in request.session:
        request.session["csrf"] = nieuw_csrf_token()
    return request.session["csrf"]


def huidige_gebruiker(request: Request, db: Session = Depends(get_db)) -> Gebruiker:
    gid = request.session.get("gebruiker_id")
    if not gid:
        raise NietIngelogd()
    gebruiker = db.get(Gebruiker, gid)
    if not gebruiker or not gebruiker.actief:
        request.session.clear()
        raise NietIngelogd()
    request.state.gebruiker = gebruiker
    return gebruiker


def vereist_rol(*rollen: str):
    def controle(gebruiker: Gebruiker = Depends(huidige_gebruiker)) -> Gebruiker:
        if gebruiker.rol not in rollen:
            raise HTTPException(status_code=403, detail="Je hebt geen toegang tot deze pagina.")
        return gebruiker

    return controle


planner_of_admin = vereist_rol("planner", "admin")
alleen_admin = vereist_rol("admin")
