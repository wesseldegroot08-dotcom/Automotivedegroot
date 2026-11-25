"""Ritten maken en inplannen. Gebruikt door het planbord en door de solver."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.planner.context import DagContext
from app.statussen import zet_status

RIT_TYPE = {"import": "afhaal", "export": "aflever", "leeg": "leeg retour", "ITT": "ITT"}


def maak_rit_voor_order(db: Session, order: m.Order) -> m.Rit:
    """Eén rit per order: van ophaalplek naar afleverplek, met twee stops."""
    rit = m.Rit(order_id=order.id, container_id=order.containers[0].id if order.containers else None, volgnr=1,
                type=RIT_TYPE.get(order.type, "afhaal"), van_locatie_id=order.van_locatie_id,
                naar_locatie_id=order.naar_locatie_id, status="Concept", vastheid="open")
    db.add(rit)
    db.flush()
    db.add_all([
        m.Stop(rit_id=rit.id, volgnr=1, locatie_id=order.van_locatie_id,
               type="gate-out" if order.van_locatie.type == "terminal" else "laden"),
        m.Stop(rit_id=rit.id, volgnr=2, locatie_id=order.naar_locatie_id,
               type="gate-in" if order.naar_locatie.type == "terminal" else "lossen"),
    ])
    return rit


def orders_zonder_rit(db: Session, orders: list[m.Order]) -> list[m.Order]:
    met = set(db.scalars(select(m.Rit.order_id).where(m.Rit.order_id.in_([o.id for o in orders]))))
    return [o for o in orders if o.id not in met and o.status not in ("Geannuleerd",)]


def werk_stops_bij(ctx: DagContext, rit: m.Rit) -> None:
    """Zet de geplande tijden van de stops en het einde van de rit."""
    if rit.gepland_start is None:
        rit.gepland_eind = None
        for s in rit.stops:
            s.gepland_aankomst = s.gepland_vertrek = None
        return
    duur = ctx.rit_duur(rit)
    t0 = rit.gepland_start
    t1 = t0 + timedelta(minutes=duur.laden_min)
    t2 = t1 + timedelta(minutes=duur.reis.minuten)
    t3 = t2 + timedelta(minutes=duur.lossen_min)
    rit.gepland_eind = t3
    rit.geplande_km = duur.reis.km
    stops = sorted(rit.stops, key=lambda s: s.volgnr)
    if len(stops) >= 2:
        stops[0].gepland_aankomst, stops[0].gepland_vertrek = t0, t1
        stops[-1].gepland_aankomst, stops[-1].gepland_vertrek = t2, t3


def plan_rit(ctx: DagContext, rit: m.Rit, start: datetime | None, trekker_id: int | None, chassis_id: int | None,
             chauffeur_id: int | None) -> None:
    """Wijs middelen en tijd toe. Status gaat mee: compleet = Gepland, anders Concept."""
    if rit.vastheid == "gestart":
        raise ValueError("Deze rit is gestart en staat vast.")
    rit.gepland_start = start
    rit.trekker_id, rit.chassis_id, rit.chauffeur_id = trekker_id, chassis_id, chauffeur_id
    db = ctx.db
    rit.trekker = db.get(m.Trekker, trekker_id) if trekker_id else None
    rit.chassis = db.get(m.Chassis, chassis_id) if chassis_id else None
    rit.chauffeur = db.get(m.Chauffeur, chauffeur_id) if chauffeur_id else None
    werk_stops_bij(ctx, rit)
    compleet = all([start, trekker_id, chassis_id, chauffeur_id])
    if compleet and rit.status == "Concept":
        zet_status(rit, "rit", "Gepland")
        if rit.order and rit.order.status == "Nieuw":
            zet_status(rit.order, "order", "Gepland")
    elif not compleet and rit.status == "Gepland":
        zet_status(rit, "rit", "Concept")
        rit.gepubliceerd = False
        if rit.order and rit.order.status == "Gepland":
            zet_status(rit.order, "order", "Nieuw")
    if rit not in ctx.ritten:
        ctx.ritten.append(rit)
