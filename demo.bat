@echo off
rem Dubbelklik: bekijk het dashboard met verzonnen auto's.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo De tool is nog niet geinstalleerd. Dubbelklik eerst op installeren.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py demo
pause
