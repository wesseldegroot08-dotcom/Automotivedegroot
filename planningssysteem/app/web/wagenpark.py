"""Wagenpark: chauffeur, eigen trekker en trailer aan elkaar koppelen. Plus een andere trekker voor één dag."""

from datetime import date
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.ports.clock import morgen_nl, vandaag_nl
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(prefix="/wagenpark", dependencies=[Depends(csrf_controle)])


def _int(v) -> int | None:
    try:
        return int(v) if v not in (None, "") else None
    except ValueError:
        return None


def _terug(melding: str = "", fout: str = "") -> RedirectResponse:
    q = {k: v for k, v in (("melding", melding), ("fout", fout)) if v}
    return RedirectResponse("/wagenpark/koppelen" + ("?" + urlencode(q) if q else ""), status_code=303)


@router.get("")
def wagenpark():
    return RedirectResponse("/wagenpark/koppelen", status_code=303)


@router.get("/koppelen")
def koppelen(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    chauffeurs = db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True))
                            .order_by(m.Chauffeur.pseudoniem)).all()
    trekkers = db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                          .order_by(m.Trekker.intern_nummer)).all()
    trailers = db.scalars(select(m.Chassis).where(m.Chassis.gearchiveerd.is_(False)).order_by(m.Chassis.nummer)).all()
    inzet = db.scalars(select(m.Inzet).where(m.Inzet.datum >= vandaag_nl()).order_by(m.Inzet.datum)).all()
    per_trekker = {t.id: t for t in trekkers}
    eigenaar = {c.voorkeur_trekker_id: c for c in chauffeurs if c.voorkeur_trekker_id}
    los_trekkers = [t for t in trekkers if t.id not in eigenaar]
    gekoppeld = {t.vaste_chassis_id for t in trekkers if t.vaste_chassis_id}
    los_trailers = [c for c in trailers if c.id not in gekoppeld]
    return templates.TemplateResponse(request, "wagenpark/koppelen.html", {
        "chauffeurs": chauffeurs, "trekkers": trekkers, "trailers": trailers, "per_trekker": per_trekker,
        "los_trekkers": los_trekkers, "los_trailers": los_trailers, "inzet": inzet, "morgen": morgen_nl(),
        "melding": request.query_params.get("melding"), "fout": request.query_params.get("fout")})


@router.post("/koppelen/{chauffeur_id}")
async def koppel(chauffeur_id: int, request: Request, db: Session = Depends(get_db),
                 gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    c = db.get(m.Chauffeur, chauffeur_id)
    trekker_id, trailer_id = _int(form.get("trekker_id")), _int(form.get("trailer_id"))
    if not c:
        return _terug(fout="Chauffeur niet gevonden.")
    if trekker_id:
        ander = db.scalar(select(m.Chauffeur).where(m.Chauffeur.voorkeur_trekker_id == trekker_id,
                                                    m.Chauffeur.id != c.id, m.Chauffeur.actief.is_(True)))
        if ander:
            t = db.get(m.Trekker, trekker_id)
            return _terug(fout=f"Trekker {t.intern_nummer} is al van {ander.pseudoniem}. Maak hem daar eerst los.")
    c.voorkeur_trekker_id = trekker_id
    tekst = f"{c.pseudoniem}: "
    if trekker_id:
        t = db.get(m.Trekker, trekker_id)
        if trailer_id:
            vorige = db.scalar(select(m.Trekker).where(m.Trekker.vaste_chassis_id == trailer_id,
                                                       m.Trekker.id != t.id))
            if vorige:
                vorige.vaste_chassis_id = None
            t.vaste_chassis_id = trailer_id
            trailer = db.get(m.Chassis, trailer_id)
            tekst += f"trekker {t.intern_nummer} met trailer {trailer.nummer}."
            if vorige:
                tekst += f" Trailer is losgemaakt van trekker {vorige.intern_nummer}."
        else:
            t.vaste_chassis_id = None
            tekst += f"trekker {t.intern_nummer}, zonder trailer. Zonder trailer komen er geen ritten."
    else:
        tekst += "geen eigen trekker meer. Er komen geen ritten tot je een trekker koppelt."
    log_actie(db, "koppelen", tabel="chauffeur", record_id=c.id, na={"trekker_id": trekker_id,
                                                                     "trailer_id": trailer_id})
    db.commit()
    return _terug(melding=tekst)


@router.post("/inzet")
async def inzet(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    c_id, t_id = _int(form.get("chauffeur_id")), _int(form.get("trekker_id"))
    try:
        d = date.fromisoformat(str(form.get("datum", "")))
    except ValueError:
        return _terug(fout="Kies een datum.")
    if not c_id or not t_id:
        return _terug(fout="Kies een chauffeur en een trekker.")
    if d < vandaag_nl():
        return _terug(fout="Die datum is al voorbij.")
    bestaand = db.scalar(select(m.Inzet).where(m.Inzet.datum == d, m.Inzet.chauffeur_id == c_id))
    if bestaand:
        bestaand.trekker_id = t_id
    else:
        db.add(m.Inzet(datum=d, chauffeur_id=c_id, trekker_id=t_id, opmerking=str(form.get("opmerking", ""))[:200]))
    db.commit()
    c, t = db.get(m.Chauffeur, c_id), db.get(m.Trekker, t_id)
    return _terug(melding=f"{c.pseudoniem} rijdt op {d:%d-%m} trekker {t.intern_nummer}. "
                          "Daarna weer de eigen trekker.")


@router.post("/inzet/{inzet_id}/weg")
def inzet_weg(inzet_id: int, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    i = db.get(m.Inzet, inzet_id)
    if i:
        db.delete(i)
        db.commit()
    return _terug(melding="Uitzondering verwijderd. De chauffeur rijdt weer de eigen trekker.")
