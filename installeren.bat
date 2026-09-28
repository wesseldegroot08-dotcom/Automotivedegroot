@echo off
rem Dubbelklik op dit bestand om Occasion Scanner te installeren (eenmalig).
cd /d "%~dp0"
echo.
echo === Occasion Scanner installeren ===
echo.
set "PY="
set "CHECK=import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"

rem 1. De py-launcher (komt mee met de installer van python.org)
where py >nul 2>nul
if errorlevel 1 goto probeer_python
py -3 -c "%CHECK%" >nul 2>nul
if errorlevel 1 goto probeer_python
set "PY=py -3"
goto gevonden

:probeer_python
rem 2. python via PATH (werkt als het vinkje "Add to PATH" aan stond)
python -c "%CHECK%" >nul 2>nul
if errorlevel 1 goto probeer_mappen
set "PY=python"
goto gevonden

:probeer_mappen
rem 3. De standaard installatiemappen (werkt ook zonder het PATH-vinkje)
for /d %%D in ("%LocalAppData%\Programs\Python\Python3*" "%ProgramFiles%\Python3*") do call :test_map "%%~D"
if defined PY goto gevonden
goto niet_gevonden

:test_map
if defined PY exit /b 0
if not exist "%~1\python.exe" exit /b 0
"%~1\python.exe" -c "%CHECK%" >nul 2>nul
if errorlevel 1 exit /b 0
set PY="%~1\python.exe"
exit /b 0

:niet_gevonden
echo Python 3.11 of nieuwer is NIET gevonden.
echo.
echo Dit heeft de computer wel gevonden:
where python 2>nul
where py 2>nul
python --version 2>nul
py --version 2>nul
echo.
echo - Staat hierboven niets? Dan is Python nog niet geinstalleerd.
echo - Staat er een pad met "WindowsApps"? Dat is alleen een snelkoppeling
echo   naar de Microsoft Store, geen echte Python.
echo - Staat er een versie lager dan 3.11? Dan is die te oud.
echo.
echo OPLOSSING: installeer Python via python.org/downloads
echo en zet een vinkje bij "Add python.exe to PATH".
echo Sluit daarna dit venster en dubbelklik opnieuw op installeren.bat.
echo.
echo Maak een foto van dit scherm als je er niet uitkomt.
pause
exit /b 1

:gevonden
echo Python gevonden:
%PY% --version
echo.
echo Onderdelen installeren, even geduld (kan een minuut duren)...
%PY% -m venv .venv
if errorlevel 1 goto fout_venv
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto fout_pip
echo.
echo Klaar! Dubbelklik nu op demo.bat of start.bat.
pause
exit /b 0

:fout_venv
echo Er ging iets mis bij het maken van de .venv-map.
echo Maak een foto van dit scherm en stuur hem op.
pause
exit /b 1

:fout_pip
echo Er ging iets mis bij het installeren van de onderdelen. Heb je internet?
echo Maak een foto van dit scherm en stuur hem op.
pause
exit /b 1
