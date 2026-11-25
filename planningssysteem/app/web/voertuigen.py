"""Voertuigen: trekkers en chassis. (Mijlpaal 2 breidt dit uit.)"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(prefix="/voertuigen", dependencies=[Depends(csrf_controle)])


@router.get("")
def overzicht(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    trekkers = db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                          .order_by(m.Trekker.intern_nummer)).all()
    chassis = db.scalars(select(m.Chassis).where(m.Chassis.gearchiveerd.is_(False)).order_by(m.Chassis.nummer)).all()
    return templates.TemplateResponse(request, "voertuigen/overzicht.html", {"trekkers": trekkers, "chassis": chassis})
