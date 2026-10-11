@echo off
cd /d "%~dp0.."
set FF=ffmpeg
where ffmpeg >nul 2>nul || set FF=ffmpeg\bin\ffmpeg.exe
if not exist "%APPDATA%\PolvoNegroLive\logs" mkdir "%APPDATA%\PolvoNegroLive\logs"
set OUT=%APPDATA%\PolvoNegroLive\logs\diagnostico_usb.txt
echo === DISPOSITIVOS DIRECTSHOW === > "%OUT%"
"%FF%" -hide_banner -list_devices true -f dshow -i dummy >> "%OUT%" 2>&1
type "%OUT%"
echo.
set /p CAM=Digite o NOME EXATO da camera (como aparece acima) para listar os modos, ou Enter para sair: 
if "%CAM%"=="" goto fim
echo. >> "%OUT%"
echo === MODOS DE: %CAM% === >> "%OUT%"
"%FF%" -hide_banner -list_options true -f dshow -i video="%CAM%" >> "%OUT%" 2>&1
"%FF%" -hide_banner -list_options true -f dshow -i video="%CAM%" 2>&1 | findstr /I "pixel_format vcodec"
:fim
echo.
echo Resultado salvo em %OUT%
pause
