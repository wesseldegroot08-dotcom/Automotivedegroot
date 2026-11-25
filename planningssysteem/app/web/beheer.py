"""Beheer: alles wat je niet elke dag nodig hebt, op één plek."""

from fastapi import APIRouter, Depends, Request

from app.planner.voorstel import noodstop_aan
from app.web.deps import get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter()

TEGELS = [
    ("/stamdata", "📚", "Stamdata en regels", "Klanten, adressen, regels, tarieven en feestdagen. Met bron en status."),
    ("/logboek", "📜", "Logboek", "Wie wat wanneer veranderde. Kan niet gewijzigd worden."),
    ("/instellingen", "⚙", "Instellingen en noodstop", "Rekentijd, ECT-datum, no-show en de noodstop."),
    ("/voorstellen", "🧮", "Eerdere plannen", "Alle automatische plannen met uitleg en vergelijking."),
    ("/facturen", "🧾", "Factuurconcept", "Concept per order op basis van de tarieven, met CSV."),
    ("/export/rooster", "🖨", "Rooster exporteren", "Print of CSV. Bewaar elke dag, voor als het systeem uitvalt."),
    ("/orders/inlezen", "✉", "Order inlezen", "E-mailtekst plakken en controleren."),
    ("/planbord/terminals", "⏱", "Wachttijden terminals", "Gemeten tijd per terminal en klant."),
    ("/voertuigen/combinatie", "⚖", "Gewicht doorrekenen", "Wat mag er op een trekker met trailer?"),
]


@router.get("/beheer")
def beheer(request: Request, db=Depends(get_db), gebruiker=Depends(planner_of_admin)):
    return templates.TemplateResponse(request, "beheer.html", {"tegels": TEGELS, "noodstop": noodstop_aan(db)})
