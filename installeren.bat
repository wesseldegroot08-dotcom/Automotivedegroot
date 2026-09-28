@echo off
rem Dubbelklik op dit bestand om Occasion Winstradar te installeren (eenmalig).
cd /d "%~dp0"
echo.
echo === Occasion Winstradar installeren ===
echo.
set "PY=python"
where py >nul 2>nul && set "PY=py"
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 of nieuwer is niet gevonden.
  echo Installeer Python via python.org/downloads en zet een vinkje bij
  echo "Add python.exe to PATH". Dubbelklik daarna opnieuw op dit bestand.
  pause
  exit /b 1
)
echo Python gevonden. Onderdelen installeren, even geduld...
%PY% -m venv .venv
if errorlevel 1 (
  echo Er ging iets mis bij het maken van de .venv-map.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
  echo Er ging iets mis bij het installeren. Heb je internet?
  pause
  exit /b 1
)
echo.
echo Klaar! Dubbelklik nu op demo.bat of start.bat.
pause
