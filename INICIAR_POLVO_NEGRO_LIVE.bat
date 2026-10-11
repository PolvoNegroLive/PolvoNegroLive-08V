@echo off
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (
  start "" pyw -3 POLVO_NEGRO_LIVE.py
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw POLVO_NEGRO_LIVE.py
  exit /b
)
echo Python 3 nao foi encontrado. Instale o Python 3 (com Tcl/Tk) em python.org e rode de novo.
pause
