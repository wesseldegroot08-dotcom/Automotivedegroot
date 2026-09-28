@echo off
rem Dubbelklik: zoekt elke 30 minuten en opent het dashboard. Stoppen: sluit dit venster.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo De tool is nog niet geinstalleerd. Dubbelklik eerst op installeren.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py start
pause
