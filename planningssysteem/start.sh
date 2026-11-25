#!/usr/bin/env bash
# Start de testversie op Mac of Linux.  Gebruik:  ./start.sh   (of ./start.sh --reset voor verse demodata)
set -e
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3 is niet gevonden. Installeer Python 3.11 of nieuwer via https://www.python.org/downloads/"
  exit 1
fi
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' || {
  echo "Je Python is te oud. Je hebt Python 3.11 of nieuwer nodig."; exit 1; }

if [ ! -d .venv ]; then
  echo "Stap 1: virtuele omgeving maken (.venv)..."
  "$PY" -m venv .venv
fi
source .venv/bin/activate

echo "Stap 2: pakketten installeren (de eerste keer duurt dit een paar minuten)..."
pip install --disable-pip-version-check -q -r requirements.txt

echo "Stap 3: instellingen en database klaarzetten..."
python -m app.setup_env
alembic upgrade head
if [ "$1" = "--reset" ]; then python -m app.seed --reset; else python -m app.seed; fi

echo ""
echo "Klaar! Open in je browser:  http://localhost:8000"
echo "Inloggen: planner / admin / chauffeur. Het wachtwoord staat in .env (DEMO_WACHTWOORD)."
echo "Stoppen: druk op Ctrl+C."
echo ""
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
