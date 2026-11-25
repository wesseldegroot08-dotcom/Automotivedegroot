"""Logboek (audit log).

Elke wijziging in de database komt vanzelf in het logboek: wie, wat, voor, na en wanneer.
Dat gebeurt met een 'luisteraar' op de database-sessie. Zo kan geen enkel scherm het vergeten.

Het logboek zelf kan via de app niet gewijzigd of verwijderd worden.
"""

import json
from datetime import date, datetime, time

from sqlalchemy import event, insert, inspect
from sqlalchemy.orm import Session

from app.db import nu_utc
from app.models import AuditLog, InlogPoging

# Wie doet de wijziging? Dat staat in session.info["gebruiker"] (zie app/web/deps.py).


def wie(session: Session) -> str:
    return session.info.get("gebruiker", "systeem")

# Tabellen die we niet loggen: het logboek zelf en de inlogpogingen (die hebben eigen rijen).
NIET_LOGGEN = {AuditLog.__tablename__, InlogPoging.__tablename__, "job"}
# Velden die nooit in het logboek mogen.
GEHEIM = {"wachtwoord_hash"}


class LogboekNietWijzigbaar(Exception):
    pass


def _naar_tekst(waarde):
    if isinstance(waarde, (datetime, date, time)):
        return waarde.isoformat()
    return waarde


def _velden(obj, alleen: set[str] | None = None) -> dict:
    mapper = inspect(obj).mapper
    uit = {}
    for kolom in mapper.column_attrs:
        if kolom.key in GEHEIM:
            continue
        if alleen is not None and kolom.key not in alleen:
            continue
        uit[kolom.key] = _naar_tekst(getattr(obj, kolom.key))
    return uit


def _json(d: dict | None) -> str | None:
    if d is None:
        return None
    return json.dumps(d, ensure_ascii=False, sort_keys=True, default=str)


def _record_id(obj) -> str:
    ident = inspect(obj).identity
    return ",".join(str(i) for i in ident) if ident else ""


@event.listens_for(Session, "after_flush")
def _log_wijzigingen(session: Session, _ctx) -> None:
    rijen = []
    gebruiker = wie(session)
    for obj in session.new:
        tabel = obj.__tablename__
        if tabel in NIET_LOGGEN:
            continue
        rijen.append(dict(actie="aanmaken", tabel=tabel, record_id=_record_id(obj), voor=None,
                          na=_json(_velden(obj))))
    for obj in session.dirty:
        tabel = obj.__tablename__
        if tabel in NIET_LOGGEN or not session.is_modified(obj, include_collections=False):
            continue
        staat = inspect(obj)
        voor, na = {}, {}
        for attr in staat.mapper.column_attrs:
            if attr.key in GEHEIM:
                continue
            hist = staat.attrs[attr.key].history
            if hist.has_changes():
                voor[attr.key] = _naar_tekst(hist.deleted[0]) if hist.deleted else None
                na[attr.key] = _naar_tekst(hist.added[0]) if hist.added else None
        if na:
            rijen.append(dict(actie="wijzigen", tabel=tabel, record_id=_record_id(obj),
                              voor=_json(voor), na=_json(na)))
    for obj in session.deleted:
        tabel = obj.__tablename__
        if tabel in NIET_LOGGEN:
            continue
        rijen.append(dict(actie="verwijderen", tabel=tabel, record_id=_record_id(obj),
                          voor=_json(_velden(obj)), na=None))
    if rijen:
        nu = nu_utc()
        for r in rijen:
            r["gebruiker"] = gebruiker
            r["tijd"] = nu
        session.connection().execute(insert(AuditLog), rijen)


@event.listens_for(Session, "before_flush")
def _bescherm_logboek(session: Session, _ctx, _instances) -> None:
    for obj in list(session.dirty) + list(session.deleted):
        if isinstance(obj, AuditLog) and (obj in session.deleted or session.is_modified(obj)):
            raise LogboekNietWijzigbaar("Het logboek kan niet gewijzigd of verwijderd worden.")


def log_actie(session: Session, actie: str, *, tabel: str = "", record_id: str = "",
              voor: dict | None = None, na: dict | None = None,
              reden_code: str | None = None, reden: str | None = None) -> None:
    """Schrijf een losse regel in het logboek, bijvoorbeeld bij inloggen of een override."""
    session.add(AuditLog(
        gebruiker=wie(session), actie=actie, tabel=tabel, record_id=str(record_id),
        voor=_json(voor), na=_json(na), reden_code=reden_code, reden=reden, tijd=nu_utc(),
    ))
