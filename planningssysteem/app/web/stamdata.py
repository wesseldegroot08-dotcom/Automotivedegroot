"""Eén set pagina's voor alle stamdata: lijst, nieuw, bewerken, archiveren.

Echt verwijderen kan niet. Zo blijft de geschiedenis bewaard.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import String, Text, or_, select
from sqlalchemy.orm import Session

from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.entiteiten import ENTITEITEN, PER_SLUG, Entiteit
from app.web.sjablonen import templates
from app.web.velden import controleer

router = APIRouter(prefix="/stamdata", dependencies=[Depends(csrf_controle)])


def _entiteit(slug: str) -> Entiteit:
    if slug not in PER_SLUG:
        raise HTTPException(404, "Deze pagina bestaat niet.")
    return PER_SLUG[slug]


def _keuzes_fk(db: Session, e: Entiteit) -> dict[str, list[tuple[int, str]]]:
    uit = {}
    for v in e.velden:
        if v.soort == "fk":
            rijen = db.scalars(select(v.fk_model).order_by(v.fk_model.id)).all()
            uit[v.naam] = [(r.id, v.fk_label(r)) for r in rijen]
    return uit


def _toon(db: Session, e: Entiteit, obj, veld) -> str:
    waarde = getattr(obj, veld.naam)
    if waarde is None:
        return ""
    if veld.soort == "fk":
        ander = db.get(veld.fk_model, waarde)
        return veld.fk_label(ander) if ander else str(waarde)
    if veld.soort == "bool":
        return "Ja" if waarde else "Nee"
    from app.web.sjablonen import tijd_nl

    if veld.soort in ("datum", "datumtijd", "tijd"):
        return tijd_nl(waarde)
    return str(waarde)


@router.get("")
def overzicht(request: Request, gebruiker=Depends(planner_of_admin)):
    groepen: dict[str, list[Entiteit]] = {}
    for e in ENTITEITEN:
        groepen.setdefault(e.groep, []).append(e)
    return templates.TemplateResponse(request, "stamdata/overzicht.html", {"groepen": groepen})


@router.get("/{slug}")
def lijst(slug: str, request: Request, q: str = "", archief: int = 0,
          db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    e = _entiteit(slug)
    stmt = select(e.model)
    if e.archief_veld and not archief:
        kolom = getattr(e.model, e.archief_veld)
        stmt = stmt.where(kolom.is_(True) if e.archief_veld == "actief" else kolom.is_(False))
    if q:
        tekstkolommen = [getattr(e.model, v.naam) for v in e.velden
                         if isinstance(getattr(e.model, v.naam).type, (String, Text))]
        if tekstkolommen:
            stmt = stmt.where(or_(*[c.ilike(f"%{q}%") for c in tekstkolommen]))
    stmt = stmt.order_by(getattr(e.model, e.sorteer), e.model.id).limit(500)
    rijen = db.scalars(stmt).all()
    kolommen = [v for v in e.velden if v.in_lijst]
    tabel = [(r, [_toon(db, e, r, v) for v in kolommen]) for r in rijen]
    return templates.TemplateResponse(request, "stamdata/lijst.html", {
        "e": e, "kolommen": kolommen, "tabel": tabel, "q": q, "archief": archief,
    })


def _formulier(request, db, e, obj, waarden, fouten, status=200):
    return templates.TemplateResponse(request, "stamdata/formulier.html", {
        "e": e, "obj": obj, "waarden": waarden, "fouten": fouten, "fk_keuzes": _keuzes_fk(db, e),
    }, status_code=status)


def _waarden_uit(obj, e: Entiteit) -> dict:
    from app.ports.clock import NL

    uit = {}
    for v in e.velden:
        w = getattr(obj, v.naam, None) if obj is not None else None
        if w is None:
            uit[v.naam] = ""
        elif v.soort == "datumtijd":
            uit[v.naam] = w.astimezone(NL).strftime("%Y-%m-%dT%H:%M")
        elif v.soort == "tijd":
            uit[v.naam] = w.strftime("%H:%M")
        else:
            uit[v.naam] = w
    return uit


@router.get("/{slug}/nieuw")
def nieuw(slug: str, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    e = _entiteit(slug)
    return _formulier(request, db, e, None, _waarden_uit(None, e), {})


@router.get("/{slug}/{obj_id}")
def bewerk(slug: str, obj_id: int, request: Request, db: Session = Depends(get_db),
           gebruiker=Depends(planner_of_admin)):
    e = _entiteit(slug)
    obj = db.get(e.model, obj_id)
    if not obj:
        raise HTTPException(404, "Niet gevonden.")
    return _formulier(request, db, e, obj, _waarden_uit(obj, e), {})


async def _opslaan(slug, request, db, obj_id=None):
    e = _entiteit(slug)
    form = dict(await request.form())
    uitkomst = controleer(e.velden, form)
    extra_fouten = extra_controle(e, uitkomst.data) if uitkomst.ok else {}
    if not uitkomst.ok or extra_fouten:
        obj = db.get(e.model, obj_id) if obj_id else None
        return _formulier(request, db, e, obj, form, uitkomst.fouten or extra_fouten, status=422)
    if obj_id:
        obj = db.get(e.model, obj_id)
        if not obj:
            raise HTTPException(404, "Niet gevonden.")
    else:
        obj = e.model()
        db.add(obj)
    for naam, waarde in uitkomst.data.items():
        setattr(obj, naam, waarde)
    db.commit()
    return RedirectResponse(f"/stamdata/{slug}?opgeslagen=1", status_code=303)


def extra_controle(e: Entiteit, data: dict) -> dict[str, str]:
    """Controles die verder gaan dan 'is het een getal'."""
    fouten = {}
    if e.slug == "containers":
        from app.rules.iso6346 import controleer_containernummer

        res = controleer_containernummer(data["nummer"])
        if not res.geldig:
            fouten["nummer"] = res.melding
        else:
            data["nummer"] = res.genormaliseerd
    if "geldig_van" in data and data.get("geldig_tot") and data["geldig_tot"] < data["geldig_van"]:
        fouten["geldig_tot"] = "'Geldig tot' ligt voor 'geldig van'."
    if e.slug == "orders" and data["venster_tot"] <= data["venster_van"]:
        fouten["venster_tot"] = "Het einde van het tijdvenster moet na het begin liggen."
    return fouten


@router.post("/{slug}/nieuw")
async def maak(slug: str, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    return await _opslaan(slug, request, db)


@router.post("/{slug}/{obj_id}")
async def wijzig(slug: str, obj_id: int, request: Request, db: Session = Depends(get_db),
                 gebruiker=Depends(planner_of_admin)):
    return await _opslaan(slug, request, db, obj_id)


@router.post("/{slug}/{obj_id}/archiveren")
def archiveer(slug: str, obj_id: int, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    e = _entiteit(slug)
    if not e.archief_veld:
        raise HTTPException(400, "Dit kun je niet archiveren.")
    obj = db.get(e.model, obj_id)
    if not obj:
        raise HTTPException(404, "Niet gevonden.")
    huidig = getattr(obj, e.archief_veld)
    setattr(obj, e.archief_veld, not huidig)
    db.commit()
    return RedirectResponse(f"/stamdata/{slug}", status_code=303)
