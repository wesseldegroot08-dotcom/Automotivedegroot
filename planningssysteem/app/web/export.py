"""Export: rooster (CSV en printbaar) en factuurconcept (scherm en CSV). Terugvaloptie als het systeem uitvalt."""

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.planner.context import laad_dag
from app.ports.clock import NL, morgen_nl
from app.rules.factuur import maak_concept
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(dependencies=[Depends(csrf_controle)])


def _datum(tekst: str) -> date:
    try:
        return date.fromisoformat(tekst) if tekst else morgen_nl()
    except ValueError:
        return morgen_nl()


def _csv(rijen: list[list], naam: str) -> Response:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    for r in rijen:
        w.writerow(r)
    # BOM zodat Excel de euro's en accenten goed leest
    return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{naam}"'})


def rooster_rijen(db: Session, d: date) -> list[dict]:
    ctx = laad_dag(db, d)
    uit = []
    for r in ctx.ritten:
        if not (r.gepland_start and r.trekker_id and r.chauffeur_id):
            continue
        slots = db.scalars(select(m.Slot).where(m.Slot.rit_id == r.id, m.Slot.status.in_(["Toegekend",
                                                                                           "Gewijzigd"]))).all()
        uit.append({
            "chauffeur": r.chauffeur.pseudoniem, "start": r.gepland_start.astimezone(NL).strftime("%H:%M"),
            "eind": (ctx.bereken_eind(r) or r.gepland_start).astimezone(NL).strftime("%H:%M"),
            "trekker": r.trekker.intern_nummer, "chassis": r.chassis.nummer if r.chassis else "",
            "order": r.order.klantreferentie, "klant": r.order.klant.naam, "van": r.van_locatie.naam,
            "naar": r.naar_locatie.naam, "containers": ", ".join(c.nummer for c in r.order.containers),
            "slot": ", ".join(f"{s.terminal.naam} {s.slot_van.astimezone(NL):%H:%M}-{s.slot_tot.astimezone(NL):%H:%M}"
                              for s in slots if s.slot_van),
            "tar": ", ".join(s.tar for s in slots if s.tar), "status": r.status,
            "gepubliceerd": "ja" if r.gepubliceerd else "nee", "vastheid": r.vastheid})
    uit.sort(key=lambda x: (x["chauffeur"], x["start"]))
    return uit


KOLOMMEN = ["chauffeur", "start", "eind", "trekker", "chassis", "order", "klant", "van", "naar", "containers", "slot",
            "tar", "status", "gepubliceerd", "vastheid"]


@router.get("/export/rooster")
def rooster(request: Request, datum: str = "", db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    rijen = rooster_rijen(db, d)
    per_chauffeur: dict[str, list[dict]] = {}
    for r in rijen:
        per_chauffeur.setdefault(r["chauffeur"], []).append(r)
    return templates.TemplateResponse(request, "export/rooster.html", {"datum": d, "per_chauffeur": per_chauffeur,
                                                                       "aantal": len(rijen)})


@router.get("/export/rooster.csv")
def rooster_csv(datum: str = "", db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    rijen = rooster_rijen(db, d)
    log_actie(db, "export rooster", tabel="planning", record_id=d.isoformat(), na={"ritten": len(rijen)})
    db.commit()
    return _csv([["datum"] + KOLOMMEN] + [[d.isoformat()] + [r[k] for k in KOLOMMEN] for r in rijen],
                f"rooster-{d.isoformat()}.csv")


def concepten(db: Session, d: date):
    ctx = laad_dag(db, d)
    tarieven = list(db.scalars(select(m.Tariefregel)))
    per_order: dict[int, list[m.Rit]] = {}
    for r in ctx.ritten:
        if r.gepland_start and r.order.status != "Geannuleerd":
            per_order.setdefault(r.order_id, []).append(r)
    return [maak_concept(ritten[0].order, ritten, tarieven, d) for ritten in per_order.values()]


@router.get("/facturen")
def facturen(request: Request, datum: str = "", db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    lijst = concepten(db, d)
    return templates.TemplateResponse(request, "export/facturen.html", {
        "datum": d, "concepten": lijst, "totaal": sum(f.totaal_cent for f in lijst)})


@router.get("/facturen.csv")
def facturen_csv(datum: str = "", db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    rijen = [["datum", "order", "klant", "omschrijving", "bedrag_euro"]]
    for f in concepten(db, d):
        for r in f.regels:
            rijen.append([d.isoformat(), f.order.klantreferentie, f.order.klant.naam, r.omschrijving,
                          f"{r.bedrag_cent / 100:.2f}".replace(".", ",")])
    return _csv(rijen, f"factuurconcept-{d.isoformat()}.csv")
