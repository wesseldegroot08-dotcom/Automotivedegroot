"""Startscherm 'Morgen': hoeveel is gepland, wat moet jij doen, en één knop Akkoord."""

import uuid
from datetime import date, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.jobs import plaats_job, voer_uit
from app.planner.automatisch import akkoord, laatste_voorstel, stand_van_de_dag, zorg_voor_plan
from app.planner.voorstel import VoorstelFout, noodstop_aan
from app.ports.clock import morgen_nl
from app.web.deps import csrf_controle, get_db, huidige_gebruiker, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(dependencies=[Depends(csrf_controle)])


def _datum(tekst: str | None) -> date:
    try:
        return date.fromisoformat(tekst) if tekst else morgen_nl()
    except ValueError:
        return morgen_nl()


def _context(request: Request, db: Session, d: date, achtergrond: BackgroundTasks, gebruiker) -> dict:
    job = zorg_voor_plan(db, d, gebruiker.gebruikersnaam)
    if job and job.status == "wachtend":
        achtergrond.add_task(voer_uit, job.id)
    stand = stand_van_de_dag(db, d, job)
    return {"s": stand, "datum": d, "vorige": d - timedelta(days=1), "volgende": d + timedelta(days=1),
            "melding": request.query_params.get("melding"), "fout": request.query_params.get("fout")}


@router.get("/")
def morgen(request: Request, achtergrond: BackgroundTasks, datum: str = "", db: Session = Depends(get_db),
           gebruiker=Depends(huidige_gebruiker)):
    if gebruiker.rol == "chauffeur":
        return RedirectResponse("/chauffeur", status_code=303)
    d = _datum(datum)
    return templates.TemplateResponse(request, "morgen.html", _context(request, db, d, achtergrond, gebruiker))


@router.get("/morgen/stand")
def stand(request: Request, achtergrond: BackgroundTasks, datum: str = "", db: Session = Depends(get_db),
          gebruiker=Depends(planner_of_admin)):
    """Voor het verversen terwijl het plan wordt gemaakt."""
    d = _datum(datum)
    return templates.TemplateResponse(request, "_morgen_stand.html", _context(request, db, d, achtergrond, gebruiker))


def _terug(d: date, melding: str = "", fout: str = "") -> RedirectResponse:
    q = {"datum": d.isoformat()}
    if melding:
        q["melding"] = melding
    if fout:
        q["fout"] = fout
    return RedirectResponse("/?" + urlencode(q), status_code=303)


@router.post("/morgen/akkoord")
async def akkoord_route(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    v = laatste_voorstel(db, d)
    if noodstop_aan(db):
        return _terug(d, fout="De noodstop staat aan. Plan en verstuur met de hand via het planbord.")
    if not v:
        return _terug(d, fout="Er is nog geen plan voor deze dag.")
    try:
        uit = akkoord(db, v, gebruiker.gebruikersnaam)
    except VoorstelFout as e:
        db.rollback()
        return _terug(d, fout=str(e))
    tekst = f"Klaar. {uit.verstuurd} rit(ten) verstuurd naar de chauffeurs."
    if uit.aangemeld:
        tekst += f" {uit.aangemeld} aangemeld bij de terminal (simulator)."
    if uit.wacht:
        tekst += f" {uit.wacht} rit(ten) wachten nog op jou: zie de lijst hieronder."
    return _terug(d, melding=tekst, fout=" ".join(uit.meldingen[:4]))


@router.post("/morgen/opnieuw")
async def opnieuw(request: Request, achtergrond: BackgroundTasks, db: Session = Depends(get_db),
                  gebruiker=Depends(planner_of_admin)):
    """Plan opnieuw maken. Vastgezette en gestarte ritten blijven staan."""
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    if noodstop_aan(db):
        return _terug(d, fout="De noodstop staat aan. Automatisch plannen staat uit.")
    job = plaats_job(db, "voorstel", {"datum": d.isoformat(), "gebruiker": gebruiker.gebruikersnaam},
                     f"voorstel:{d}:opnieuw:{uuid.uuid4().hex[:10]}")
    db.commit()
    achtergrond.add_task(voer_uit, job.id)
    return _terug(d)
