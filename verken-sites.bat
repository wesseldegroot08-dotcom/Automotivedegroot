@echo off
rem Dubbelklik: kijk per site of het zoeken werkt.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo De tool is nog niet geinstalleerd. Dubbelklik eerst op installeren.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py verken-sites
pause
