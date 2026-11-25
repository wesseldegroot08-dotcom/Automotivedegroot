"""Inloggen: wachtwoorden hashen, rem op inlogpogingen en CSRF-bescherming.

- Hashen: een wachtwoord slaan we nooit zelf op, alleen een 'hash' (een onomkeerbare code).
  We gebruiken argon2, de huidige aanbeveling.
- Rem: na 5 mislukte pogingen in 15 minuten kun je even niet inloggen.
- CSRF: elk formulier stuurt een geheim token mee. Zo kan een andere website
  niet stiekem namens jou op een knop drukken.
"""

import secrets
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Gebruiker, InlogPoging
from app.ports.clock import klok

_hasher = PasswordHasher()

MAX_MISLUKT = 5
REM_PERIODE = timedelta(minutes=15)


def hash_wachtwoord(wachtwoord: str) -> str:
    return _hasher.hash(wachtwoord)


def controleer_wachtwoord(hash_: str, wachtwoord: str) -> bool:
    try:
        return _hasher.verify(hash_, wachtwoord)
    except (VerifyMismatchError, InvalidHashError):
        return False


def is_geremd(db: Session, gebruikersnaam: str, ip: str) -> bool:
    sinds = klok().nu() - REM_PERIODE
    aantal = db.scalar(
        select(func.count()).select_from(InlogPoging).where(
            InlogPoging.gelukt.is_(False),
            InlogPoging.tijd >= sinds,
            (InlogPoging.gebruikersnaam == gebruikersnaam) | (InlogPoging.ip == ip),
        )
    )
    return (aantal or 0) >= MAX_MISLUKT


def probeer_inloggen(db: Session, gebruikersnaam: str, wachtwoord: str, ip: str) -> Gebruiker | None:
    """Geeft de gebruiker terug als het klopt. Anders None. Elke poging wordt bewaard."""
    gebruiker = db.scalar(select(Gebruiker).where(Gebruiker.gebruikersnaam == gebruikersnaam))
    gelukt = bool(gebruiker and gebruiker.actief and controleer_wachtwoord(gebruiker.wachtwoord_hash, wachtwoord))
    db.add(InlogPoging(gebruikersnaam=gebruikersnaam, ip=ip, gelukt=gelukt, tijd=klok().nu()))
    db.commit()
    return gebruiker if gelukt else None


def nieuw_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def tokens_gelijk(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return secrets.compare_digest(a, b)
