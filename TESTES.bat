@echo off
cd /d "%~dp0.."
where py >nul 2>nul && (py -3 -m unittest discover -s tests -v) || (python -m unittest discover -s tests -v)
pause
