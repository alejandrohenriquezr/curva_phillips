@echo off
cd /d "%~dp0.."
set "PHILLIPS_PYTHON=%~dp0..\venv\Scripts\python.exe"
if not exist "%PHILLIPS_PYTHON%" (
  echo Primero ejecuta lanzadores\00_instalar.bat
  pause
  exit /b 1
)
"%PHILLIPS_PYTHON%" -m notebook
if errorlevel 1 pause
