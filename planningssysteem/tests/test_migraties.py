"""De migraties maken precies dezelfde tabellen als de code beschrijft."""

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory  # noqa: F401
from sqlalchemy import create_engine

from app.config import BASIS_MAP


def test_migraties_draaien_en_kloppen_met_de_code(tmp_path):
    url = f"sqlite:///{(tmp_path / 'm.db').as_posix()}"
    cfg = Config(str(BASIS_MAP / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASIS_MAP / "migrations"))
    cfg.attributes["url"] = url
    command.upgrade(cfg, "head")
    # 'check' faalt als de code tabellen of kolommen heeft die niet in een migratie staan
    command.check(cfg)
    create_engine(url).dispose()
