"""Alembic: past de database aan als de tabellen veranderen (migraties)."""

from alembic import context

from app import models  # noqa: F401  (laadt alle tabellen)
from app.config import instellingen
from app.db import Base, maak_engine

doel = Base.metadata


def run_migrations_online() -> None:
    url = context.config.attributes.get("url") or instellingen().database_url
    engine = maak_engine(url)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=doel, render_as_batch=True, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
