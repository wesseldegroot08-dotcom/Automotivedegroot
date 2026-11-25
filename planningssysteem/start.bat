@echo off
REM Start de testversie op Windows.  Gebruik: dubbelklik, of "start.bat --reset" voor verse demodata.
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 of nieuwer is niet gevonden.
  echo Installeer het via https://www.python.org/downloads/ en vink "Add python.exe to PATH" aan.
  pause
  exit /b 1
)

if not exist .venv (
  echo Stap 1: virtuele omgeving maken ^(.venv^)...
  %PY% -m venv .venv
  if errorlevel 1 goto fout
)
call .venv\Scripts\activate.bat

echo Stap 2: pakketten installeren ^(de eerste keer duurt dit een paar minuten^)...
python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto fout

echo Stap 3: instellingen en database klaarzetten...
python -m app.setup_env
alembic upgrade head
if errorlevel 1 goto fout
if "%~1"=="--reset" (python -m app.seed --reset) else (python -m app.seed)
if errorlevel 1 goto fout

echo.
echo Klaar! Open in je browser:  http://localhost:8000
echo Inloggen: planner / admin / chauffeur. Het wachtwoord staat in .env ^(DEMO_WACHTWOORD^).
echo Stoppen: druk op Ctrl+C.
echo.
uvicorn app.main:app --host 127.0.0.1 --port 8000
goto einde

:fout
echo.
echo Er ging iets mis. Lees de melding hierboven.
pause
exit /b 1

:einde
endlocal
