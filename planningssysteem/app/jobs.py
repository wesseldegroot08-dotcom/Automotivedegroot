"""Eenvoudige job-wachtrij in de database.

- plaats_job: maakt een taak. Bestaat de sleutel al, dan krijg je de bestaande taak terug (idempotent).
- voer_uit: voert één taak uit in een eigen databasesessie. Fouten worden opgeslagen, nooit verzwegen.
- verwerk_wachtende: pakt alle wachtende taken op (bijvoorbeeld na een herstart).
"""

import json
import traceback
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import db as dbmod
from app import models as m
from app.db import nu_utc

HANDLERS: dict[str, Callable[[Session, dict, m.Job], dict]] = {}


def handler(soort: str):
    def registreer(f):
        HANDLERS[soort] = f
        return f

    return registreer


def plaats_job(db: Session, soort: str, payload: dict, sleutel: str) -> m.Job:
    bestaand = db.scalar(select(m.Job).where(m.Job.sleutel == sleutel))
    if bestaand:
        return bestaand
    job = m.Job(soort=soort, sleutel=sleutel, payload=json.dumps(payload, ensure_ascii=False))
    db.add(job)
    try:
        db.flush()
    except IntegrityError:  # tegelijk aangemaakt: neem de bestaande
        db.rollback()
        return db.scalar(select(m.Job).where(m.Job.sleutel == sleutel))
    return job


def voer_uit(job_id: int) -> None:
    import app.berichten  # noqa: F401  (registreert de handlers)
    import app.planner.voorstel  # noqa: F401

    with dbmod.SessionLocal() as db:
        job = db.get(m.Job, job_id)
        if not job or job.status in ("bezig", "klaar"):
            return
        payload = json.loads(job.payload or "{}")
        db.info["gebruiker"] = payload.get("gebruiker", "systeem")
        job.status, job.gestart, job.pogingen = "bezig", nu_utc(), job.pogingen + 1
        db.commit()
        try:
            resultaat = HANDLERS[job.soort](db, payload, job)
            job.status, job.resultaat, job.klaar = "klaar", json.dumps(resultaat, ensure_ascii=False), nu_utc()
            db.commit()
        except Exception as e:
            db.rollback()
            job = db.get(m.Job, job_id)
            job.status, job.klaar = "fout", nu_utc()
            job.fout = f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}"
            db.commit()


def verwerk_wachtende() -> int:
    with dbmod.SessionLocal() as db:
        ids = list(db.scalars(select(m.Job.id).where(m.Job.status == "wachtend").order_by(m.Job.id)))
    for i in ids:
        voer_uit(i)
    return len(ids)
