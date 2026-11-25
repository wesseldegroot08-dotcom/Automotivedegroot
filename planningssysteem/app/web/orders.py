"""Order inlezen: tekst plakken, concept controleren, goedkeuren."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.keuzes import CONTAINER_MATEN, CONTAINER_TYPES, ORDER_TYPES
from app.orders_inlezen import VERPLICHT, bewaar, keur_af, keur_goed, lees_in
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(prefix="/orders", dependencies=[Depends(csrf_controle)])
VELDEN = list(VERPLICHT) + ["boeking_bl"]

VOORBEELD = """Goedemiddag,

Graag ophalen bij ECT Euromax: container CSQU3054383 (40ft HC), VGM 21.500 kg.
Onze ref: ALFA-7781. B/L nummer MAEU12345678.
Leveren bij Alfa DC Waalwijk op 27-11-2026 tussen 09:00 - 13:00.

Groet, Alfa Logistiek (demo)"""


@router.get("/inlezen")
def inlezen(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    concepten = db.scalars(select(m.OrderConcept).order_by(m.OrderConcept.id.desc()).limit(20)).all()
    return templates.TemplateResponse(request, "orders/inlezen.html", {"concepten": concepten,
                                                                      "voorbeeld": VOORBEELD})


@router.post("/inlezen")
async def inlezen_post(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    tekst = str(form.get("tekst", "")).strip()
    if len(tekst) < 10:
        return RedirectResponse("/orders/inlezen", status_code=303)
    c = lees_in(db, tekst[:20000], gebruiker.gebruikersnaam)
    db.commit()
    return RedirectResponse(f"/orders/concept/{c.id}", status_code=303)


def _keuzes(db: Session) -> dict:
    return {
        "klanten": db.scalars(select(m.Klant).where(m.Klant.actief.is_(True)).order_by(m.Klant.naam)).all(),
        "terminals": db.scalars(select(m.Locatie).where(m.Locatie.type.in_(["terminal", "depot"]))
                                .order_by(m.Locatie.naam)).all(),
        "klantlocaties": db.scalars(select(m.Locatie).where(m.Locatie.type == "klant").order_by(m.Locatie.naam)).all(),
        "rederijen": db.scalars(select(m.Rederij).order_by(m.Rederij.naam)).all(),
        "maten": CONTAINER_MATEN, "types": CONTAINER_TYPES, "ordertypes": ORDER_TYPES,
    }


@router.get("/concept/{cid}")
def concept(cid: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    c = db.get(m.OrderConcept, cid)
    if not c:
        raise HTTPException(404, "Concept niet gevonden.")
    return templates.TemplateResponse(request, "orders/concept.html", {
        "c": c, "v": json.loads(c.velden), "meldingen": json.loads(c.meldingen), **_keuzes(db),
        "fout": request.query_params.get("fout")})


@router.post("/concept/{cid}")
async def concept_post(cid: int, request: Request, db: Session = Depends(get_db),
                       gebruiker=Depends(planner_of_admin)):
    c = db.get(m.OrderConcept, cid)
    if not c:
        raise HTTPException(404, "Concept niet gevonden.")
    if c.status in ("Goedgekeurd", "Afgekeurd"):
        return RedirectResponse(f"/orders/concept/{cid}", status_code=303)
    form = await request.form()
    velden = {k: str(form.get(k, "")).strip() for k in VELDEN}
    actie = str(form.get("actie", "opslaan"))
    if actie == "afkeuren":
        keur_af(db, c)
        db.commit()
        return RedirectResponse("/orders/inlezen", status_code=303)
    if actie == "goedkeuren":
        try:
            o = keur_goed(db, c, velden, gebruiker.gebruikersnaam)
        except ValueError as e:
            db.commit()  # de ingevulde velden en meldingen bewaren
            from urllib.parse import urlencode

            return RedirectResponse(f"/orders/concept/{cid}?" + urlencode({"fout": str(e)}), status_code=303)
        db.commit()
        d = o.venster_van.date().isoformat()
        return RedirectResponse(f"/planbord?datum={d}&melding=Order+{o.klantreferentie}+aangemaakt", status_code=303)
    bewaar(db, c, velden)
    db.commit()
    return RedirectResponse(f"/orders/concept/{cid}", status_code=303)
