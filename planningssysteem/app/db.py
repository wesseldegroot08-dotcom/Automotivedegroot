"""Database-verbinding.

We gebruiken SQLAlchemy 2. Geen SQLite-trucs, zodat PostgreSQL later ook werkt.
Tijden slaan we op in UTC (zie UTCDatumTijd).
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.config import instellingen


class Base(DeclarativeBase):
    pass


class UTCDatumTijd(TypeDecorator):
    """Slaat een tijd op als UTC en geeft altijd een tijd mét tijdzone terug."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Tijd zonder tijdzone. Gebruik een tijd met tijdzone.")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


def maak_engine(url: str | None = None):
    url = url or instellingen().database_url
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=args)
    if url.startswith("sqlite"):
        # Foreign keys aanzetten in SQLite (PostgreSQL doet dit altijd).
        @event.listens_for(engine, "connect")
        def _fk_aan(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()

    return engine


engine = maak_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def nu_utc() -> datetime:
    return datetime.now(UTC)
