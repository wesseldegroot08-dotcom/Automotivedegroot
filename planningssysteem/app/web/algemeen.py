"""Inloggen, startpagina, logboek en instellingen."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.auth import is_geremd, nieuw_csrf_token, probeer_inloggen
from app.ports.clock import NL
from app.web.deps import alleen_admin, csrf_controle, get_db, huidige_gebruiker, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(dependencies=[Depends(csrf_controle)])


def _ip(request: Request) -> str:
    return request.client.host if request.client else "onbekend"


@router.get("/login")
def login_pagina(request: Request):
    return templates.TemplateResponse(request, "login.html", {"fout": None})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    naam = str(form.get("gebruikersnaam", "")).strip()
    wachtwoord = str(form.get("wachtwoord", ""))
    if is_geremd(db, naam, _ip(request)):
        return templates.TemplateResponse(request, "login.html", {
            "fout": "Te veel mislukte pogingen. Wacht 15 minuten en probeer het opnieuw."}, status_code=429)
    gebruiker = probeer_inloggen(db, naam, wachtwoord, _ip(request))
    if not gebruiker:
        return templates.TemplateResponse(request, "login.html", {
            "fout": "Gebruikersnaam of wachtwoord klopt niet."}, status_code=401)
    request.session.clear()
    request.session.update(gebruiker_id=gebruiker.id, gebruikersnaam=gebruiker.gebruikersnaam,
                           rol=gebruiker.rol, csrf=nieuw_csrf_token())
    db.info["gebruiker"] = gebruiker.gebruikersnaam
    log_actie(db, "inloggen", tabel="gebruiker", record_id=gebruiker.id)
    db.commit()
    return RedirectResponse("/chauffeur" if gebruiker.rol == "chauffeur" else "/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/")
def start(request: Request, db: Session = Depends(get_db), gebruiker=Depends(huidige_gebruiker)):
    if gebruiker.rol == "chauffeur":
        return RedirectResponse("/chauffeur", status_code=303)
    tellers = {
        "Orders": db.scalar(select(func.count()).select_from(m.Order)),
        "Trekkers": db.scalar(select(func.count()).select_from(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))),
        "Chassis": db.scalar(select(func.count()).select_from(m.Chassis).where(m.Chassis.gearchiveerd.is_(False))),
        "Chauffeurs": db.scalar(select(func.count()).select_from(m.Chauffeur).where(m.Chauffeur.actief.is_(True))),
        "Regels": db.scalar(select(func.count()).select_from(m.Regel)),
    }
    open_regels = db.scalar(select(func.count()).select_from(m.Regel).where(m.Regel.status != "bevestigd"))
    return templates.TemplateResponse(request, "start.html", {"tellers": tellers, "open_regels": open_regels})


@router.get("/chauffeur")
def chauffeur_start(request: Request, gebruiker=Depends(huidige_gebruiker)):
    return templates.TemplateResponse(request, "chauffeur_leeg.html", {})


@router.get("/logboek")
def logboek(request: Request, q: str = "", actie: str = "", tabel: str = "", gebruiker_filter: str = "",
            van: str = "", tot: str = "", pagina: int = 1,
            db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    stmt = select(m.AuditLog)
    if q:
        stmt = stmt.where(or_(m.AuditLog.voor.ilike(f"%{q}%"), m.AuditLog.na.ilike(f"%{q}%"),
                              m.AuditLog.reden.ilike(f"%{q}%"), m.AuditLog.record_id == q))
    if actie:
        stmt = stmt.where(m.AuditLog.actie == actie)
    if tabel:
        stmt = stmt.where(m.AuditLog.tabel == tabel)
    if gebruiker_filter:
        stmt = stmt.where(m.AuditLog.gebruiker == gebruiker_filter)
    try:
        if van:
            stmt = stmt.where(m.AuditLog.tijd >= datetime.fromisoformat(van).replace(tzinfo=NL))
        if tot:
            stmt = stmt.where(m.AuditLog.tijd < datetime.fromisoformat(tot).replace(tzinfo=NL) + timedelta(days=1))
    except ValueError:
        pass
    per_pagina = 100
    rijen = db.scalars(stmt.order_by(m.AuditLog.id.desc()).offset((pagina - 1) * per_pagina)
                       .limit(per_pagina)).all()
    acties = db.scalars(select(m.AuditLog.actie).distinct().order_by(m.AuditLog.actie)).all()
    tabellen = db.scalars(select(m.AuditLog.tabel).distinct().order_by(m.AuditLog.tabel)).all()
    gebruikers = db.scalars(select(m.AuditLog.gebruiker).distinct().order_by(m.AuditLog.gebruiker)).all()
    return templates.TemplateResponse(request, "logboek.html", {
        "rijen": rijen, "q": q, "actie": actie, "tabel": tabel, "gebruiker_filter": gebruiker_filter,
        "van": van, "tot": tot, "pagina": pagina, "acties": acties, "tabellen": tabellen,
        "gebruikers": gebruikers, "meer": len(rijen) == per_pagina,
    })


@router.get("/instellingen")
def instellingen(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    rijen = db.scalars(select(m.Instelling).order_by(m.Instelling.sleutel)).all()
    return templates.TemplateResponse(request, "instellingen.html", {"rijen": rijen})


@router.post("/instellingen/{sleutel}")
async def instelling_opslaan(sleutel: str, request: Request, db: Session = Depends(get_db),
                             gebruiker=Depends(alleen_admin)):
    obj = db.get(m.Instelling, sleutel)
    if not obj:
        raise HTTPException(404, "Onbekende instelling.")
    form = await request.form()
    obj.waarde = str(form.get("waarde", "")).strip()
    db.commit()
    return RedirectResponse("/instellingen", status_code=303)
