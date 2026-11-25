"""Maak een back-up van de database.

Gebruik:  python scripts/backup.py            (maakt backups/planning-JJJJMMDD-UUMM.db)
          python scripts/backup.py --houd 30  (bewaar de laatste 30 back-ups, standaard 14)

Werkt met SQLite. De back-up wordt gemaakt met de backup-functie van SQLite, dus ook als de app draait.
Terugzetten: stop de app, kopieer de back-up naar data/planning.db, start de app. Zie docs/NOODPROCEDURE.md.
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))


def database_pad() -> Path:
    from app.config import instellingen

    url = instellingen().database_url
    if not url.startswith("sqlite:///"):
        raise SystemExit("Alleen SQLite wordt ondersteund door dit script.")
    return Path(url.removeprefix("sqlite:///"))


def maak_backup(bron: Path, map_: Path, houd: int = 14) -> Path:
    if not bron.exists():
        raise SystemExit(f"Database niet gevonden: {bron}")
    map_.mkdir(parents=True, exist_ok=True)
    doel = map_ / f"planning-{datetime.now():%Y%m%d-%H%M%S}.db"
    with sqlite3.connect(bron) as b, sqlite3.connect(doel) as d:
        b.backup(d)
    with sqlite3.connect(doel) as d:  # controle: is de kopie leesbaar?
        if d.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise SystemExit("De back-up is beschadigd. Probeer het opnieuw.")
    oud = sorted(map_.glob("planning-*.db"))[:-houd] if houd > 0 else []
    for f in oud:
        f.unlink()
    return doel


def main() -> None:
    p = argparse.ArgumentParser(description="Back-up van de planningsdatabase")
    p.add_argument("--houd", type=int, default=14, help="aantal back-ups dat bewaard blijft")
    p.add_argument("--map", default=str(BASIS / "backups"), help="map voor de back-ups")
    args = p.parse_args()
    doel = maak_backup(database_pad(), Path(args.map), args.houd)
    print(f"Back-up gemaakt: {doel}")


if __name__ == "__main__":
    main()
