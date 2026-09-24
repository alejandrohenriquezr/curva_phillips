@echo off
cd /d "%~dp0"
set "PHILLIPS_PYTHON=%LOCALAPPDATA%\curva_phillips\venv\Scripts\python.exe"
if not exist "%PHILLIPS_PYTHON%" (
 echo Ejecuta INSTALAR.bat primero.
 exit /b 1
)
"%PHILLIPS_PYTHON%" -X utf8 orquestar.py %*
if errorlevel 1 pause
