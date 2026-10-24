@echo off
cd /d "%~dp0.."
set "PHILLIPS_PYTHON=%~dp0..\venv\Scripts\python.exe"
if not exist "%PHILLIPS_PYTHON%" (
 echo Ejecuta lanzadores\00_instalar.bat primero.
 exit /b 1
)
"%PHILLIPS_PYTHON%" -X utf8 scripts\05_ejecutar_todo.py %*
if errorlevel 1 pause
