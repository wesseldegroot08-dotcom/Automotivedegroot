"""Voorstellen: maken (via de job-wachtrij), bekijken, vergelijken, goedkeuren of afkeuren."""

import json
import uuid
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.jobs import plaats_job, voer_uit
from app.planner.context import laad_dag
from app.planner.voorstel import (
    VoorstelFout,
    afkeuren,
    goedkeuren,
    huidige_hash,
    meet,
    noodstop_aan,
    regelversie,
)
from app.ports.clock import morgen_nl
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(prefix="/voorstellen", dependencies=[Depends(csrf_controle)])


def _datum(tekst: str | None) -> date:
    try:
        return date.fromisoformat(tekst) if tekst else morgen_nl()
    except ValueError:
        return morgen_nl()


def _terug(url: str, melding: str = "", fout: str = ""):
    from urllib.parse import urlencode

    q = {k: v for k, v in (("melding", melding), ("fout", fout)) if v}
    return RedirectResponse(url + ("&" if "?" in url else "?") + urlencode(q) if q else url, status_code=303)


def _voorstel_van_job(job: m.Job) -> int | None:
    if job and job.status == "klaar" and job.resultaat:
        return json.loads(job.resultaat).get("voorstel_id")
    return None


@router.get("")
def overzicht(request: Request, datum: str = "", db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    voorstellen = db.scalars(select(m.Voorstel).where(m.Voorstel.datum == d).order_by(m.Voorstel.id.desc())).all()
    jobs = db.scalars(select(m.Job).where(m.Job.soort == "voorstel", m.Job.status.in_(["wachtend", "bezig", "fout"]))
                      .order_by(m.Job.id.desc()).limit(5)).all()
    jobs = [j for j in jobs if json.loads(j.payload).get("datum") == d.isoformat()]
    return templates.TemplateResponse(request, "voorstellen/overzicht.html", {
        "datum": d, "voorstellen": voorstellen, "jobs": jobs, "noodstop": noodstop_aan(db),
        "melding": request.query_params.get("melding"), "fout": request.query_params.get("fout")})


@router.post("/maken")
async def maken(request: Request, achtergrond: BackgroundTasks, db: Session = Depends(get_db),
                gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    if noodstop_aan(db):
        return _terug(f"/voorstellen?datum={d}", fout="De noodstop staat aan. Voorstellen zijn uit.")
    herbereken = form.get("herbereken") == "ja"
    # Zelfde invoer en regels = zelfde taak (dubbel klikken maakt geen tweede voorstel).
    sleutel = f"voorstel:{d}:{huidige_hash(db, d)}:{regelversie(db)}"
    if herbereken:
        sleutel += f":{uuid.uuid4().hex[:8]}"
    job = plaats_job(db, "voorstel", {"datum": d.isoformat(), "gebruiker": gebruiker.gebruikersnaam}, sleutel)
    db.commit()
    if job.status == "klaar" and (vid := _voorstel_van_job(job)):
        return _terug(f"/voorstellen/{vid}", melding="Dit voorstel bestaat al voor precies deze invoer.")
    if job.status == "wachtend":
        achtergrond.add_task(voer_uit, job.id)
    return RedirectResponse(f"/voorstellen/job/{job.id}", status_code=303)


@router.get("/job/{job_id}")
def job_status(job_id: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    job = db.get(m.Job, job_id)
    if not job:
        raise HTTPException(404, "Taak niet gevonden.")
    vid = _voorstel_van_job(job)
    if vid and not request.headers.get("HX-Request"):
        return RedirectResponse(f"/voorstellen/{vid}", status_code=303)
    sjabloon = "voorstellen/_job.html" if request.headers.get("HX-Request") else "voorstellen/job.html"
    antwoord = templates.TemplateResponse(request, sjabloon, {"job": job, "voorstel_id": vid,
                                                              "datum": json.loads(job.payload).get("datum")})
    if vid and request.headers.get("HX-Request"):
        antwoord.headers["HX-Redirect"] = f"/voorstellen/{vid}"
    return antwoord


@router.get("/{voorstel_id}")
def detail(voorstel_id: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    v = db.get(m.Voorstel, voorstel_id)
    if not v:
        raise HTTPException(404, "Voorstel niet gevonden.")
    huidig = meet(laad_dag(db, v.datum))
    verouderd = v.status == "Voorgesteld" and huidige_hash(db, v.datum) != v.invoer_hash
    ingepland = sorted([r for r in v.regels if r.ingepland], key=lambda r: (r.trekker_id or 0, r.start))
    niet = [r for r in v.regels if not r.ingepland]
    return templates.TemplateResponse(request, "voorstellen/detail.html", {
        "v": v, "huidig": huidig, "ingepland": ingepland, "niet": niet, "verouderd": verouderd,
        "noodstop": noodstop_aan(db), "regelversie_nu": regelversie(db),
        "melding": request.query_params.get("melding"), "fout": request.query_params.get("fout")})


@router.post("/{voorstel_id}/goedkeuren")
def goedkeuren_route(voorstel_id: int, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    v = db.get(m.Voorstel, voorstel_id)
    if not v:
        raise HTTPException(404, "Voorstel niet gevonden.")
    try:
        aantal = goedkeuren(db, v, gebruiker.gebruikersnaam)
    except VoorstelFout as e:
        db.rollback()
        return _terug(f"/voorstellen/{voorstel_id}", fout=str(e))
    db.commit()
    return _terug(f"/planbord?datum={v.datum}", melding=f"Voorstel goedgekeurd: {aantal} rit(ten) op het planbord "
                  "gezet. Pas aan waar nodig, stuur de pre-notificaties en publiceer daarna.")


@router.post("/{voorstel_id}/afkeuren")
async def afkeuren_route(voorstel_id: int, request: Request, db: Session = Depends(get_db),
                         gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    v = db.get(m.Voorstel, voorstel_id)
    if not v:
        raise HTTPException(404, "Voorstel niet gevonden.")
    try:
        afkeuren(db, v, gebruiker.gebruikersnaam, str(form.get("reden", "")))
    except VoorstelFout as e:
        db.rollback()
        return _terug(f"/voorstellen/{voorstel_id}", fout=str(e))
    db.commit()
    return _terug(f"/voorstellen?datum={v.datum}", melding="Voorstel afgekeurd. Er is niets op het planbord veranderd.")
