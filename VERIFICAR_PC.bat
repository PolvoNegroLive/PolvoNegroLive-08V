@echo off
cd /d "%~dp0"
echo ==========================================
echo  POLVO NEGRO LIVE 8.0.0 - VERIFICACAO
echo ==========================================
echo.
echo [Python]
where py >nul 2>nul && (py -3 --version) || (where python >nul 2>nul && python --version || echo NAO ENCONTRADO)
echo.
echo [Tkinter - necessario para o painel]
where py >nul 2>nul && (py -3 -c "import tkinter; print('OK')" 2>nul || echo FALTANDO) || (python -c "import tkinter; print('OK')" 2>nul || echo FALTANDO)
echo.
echo [FFmpeg]
where ffmpeg >nul 2>nul && (where ffmpeg & ffmpeg -version | findstr /B "ffmpeg version") || echo Nao esta no PATH
if exist "ffmpeg\bin\ffmpeg.exe" echo Local: ffmpeg\bin\ffmpeg.exe
echo.
echo Nada foi instalado. Este arquivo apenas verifica.
pause
