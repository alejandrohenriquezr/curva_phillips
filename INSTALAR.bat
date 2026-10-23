@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_entorno.ps1"
if errorlevel 1 (
  echo La instalacion no se completo. Revisa el error anterior.
  pause
  exit /b 1
)
pause
