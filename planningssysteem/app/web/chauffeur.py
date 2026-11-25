"""Chauffeurspagina voor de telefoon: grote knoppen, tijdstempels, geen GPS."""

from datetime import timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.planner.context import dag_grenzen
from app.ports.clock import NL, klok, vandaag_nl
from app.statussen import OngeldigeOvergang, mag, zet_status
from app.web.deps import csrf_controle, get_db, huidige_gebruiker
from app.web.sjablonen import templates

router = APIRouter(prefix="/chauffeur", dependencies=[Depends(csrf_controle)])

# actie -> (nieuwe ritstatus, knoptekst)
ACTIES = {
    "vertrek": ("Onderweg", "🚚 Vertrek / onderweg"),
    "aangekomen": ("Aangekomen", "📍 Aangekomen"),
    "bezig": ("In behandeling", "⏳ Laden of lossen begonnen"),
    "klaar": ("Klaar", "✔ Klaar hier"),
    "afronden": ("Afgerond", "🏁 Rit afgerond"),
}


def _volgende_stop(rit: m.Rit) -> m.Stop | None:
    return next((s for s in sorted(rit.stops, key=lambda s: s.volgnr) if s.werkelijk_vertrek is None), None)


def knoppen(rit: m.Rit) -> list[tuple[str, str]]:
    uit = []
    open_stops = [s for s in rit.stops if s.werkelijk_vertrek is None]
    for actie, (status, tekst) in ACTIES.items():
        if not mag("rit", rit.status, status):
            continue
        if actie == "vertrek" and rit.status == "Klaar" and not open_stops:
            continue  # alles gedaan: alleen afronden
        if actie == "afronden" and open_stops:
            continue
        uit.append((actie, tekst))
    return uit


def _mijn_rit(db: Session, gebruiker, rit_id: int) -> m.Rit:
    rit = db.get(m.Rit, rit_id)
    if not rit or not gebruiker.chauffeur_id or rit.chauffeur_id != gebruiker.chauffeur_id or not rit.gepubliceerd:
        raise HTTPException(403, "Dit is niet jouw rit, of de rit is nog niet gepubliceerd.")
    return rit


def _order_status(rit: m.Rit, naar: str) -> None:
    """De orderstatus loopt mee als dat een toegestane stap is. Anders blijft hij staan."""
    if rit.order:
        try:
            zet_status(rit.order, "order", naar)
        except OngeldigeOvergang:
            pass


@router.get("")
def start(request: Request, db: Session = Depends(get_db), gebruiker=Depends(huidige_gebruiker)):
    if gebruiker.rol != "chauffeur":
        return RedirectResponse("/planbord", status_code=303)
    ritten = []
    chauffeur = db.get(m.Chauffeur, gebruiker.chauffeur_id) if gebruiker.chauffeur_id else None
    if chauffeur:
        begin, _ = dag_grenzen(vandaag_nl())
        ritten = db.scalars(select(m.Rit).where(
            m.Rit.chauffeur_id == chauffeur.id, m.Rit.gepubliceerd.is_(True), m.Rit.gepland_start >= begin,
            m.Rit.gepland_start < begin + timedelta(days=2)).order_by(m.Rit.gepland_start)).all()
    slots = {}
    for r in ritten:
        slots[r.id] = db.scalars(select(m.Slot).where(m.Slot.rit_id == r.id,
                                                      m.Slot.status.in_(["Toegekend", "Gewijzigd"]))).all()
    return templates.TemplateResponse(request, "chauffeur/start.html", {
        "chauffeur": chauffeur, "ritten": ritten, "knoppen": {r.id: knoppen(r) for r in ritten}, "slots": slots,
        "melding": request.query_params.get("melding"), "fout": request.query_params.get("fout")})


@router.post("/rit/{rit_id}/{actie}")
def actie(rit_id: int, actie: str, db: Session = Depends(get_db), gebruiker=Depends(huidige_gebruiker)):
    if actie not in ACTIES:
        raise HTTPException(404, "Onbekende knop.")
    rit = _mijn_rit(db, gebruiker, rit_id)
    nu = klok().nu()
    stop = _volgende_stop(rit)
    try:
        zet_status(rit, "rit", ACTIES[actie][0])
    except OngeldigeOvergang as e:
        db.rollback()
        return RedirectResponse("/chauffeur?" + urlencode({"fout": str(e)}), status_code=303)
    if actie == "vertrek":
        rit.vastheid = "gestart"
        _order_status(rit, "Onderweg")
    elif actie == "aangekomen" and stop:
        stop.werkelijk_aankomst = nu
        _order_status(rit, "Op terminal" if stop.locatie.type == "terminal" else "Bij klant")
    elif actie == "klaar" and stop:
        stop.werkelijk_vertrek = nu
        if stop.werkelijk_aankomst:
            stop.wachttijd_min = int((nu - stop.werkelijk_aankomst).total_seconds() // 60)
    elif actie == "afronden":
        _order_status(rit, "Geleverd")
    db.commit()
    tekst = f"{ACTIES[actie][1][2:]} om {nu.astimezone(NL):%H:%M}"
    return RedirectResponse("/chauffeur?" + urlencode({"melding": tekst}), status_code=303)
