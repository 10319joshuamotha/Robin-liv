@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Robin is not installed yet.
  echo Run install_windows.ps1 first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" main.py
endlocal
