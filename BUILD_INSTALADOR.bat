@echo off
setlocal
cd /d "%~dp0.."
echo === 1/3 PyInstaller ===
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% -m pip install --upgrade pyinstaller || goto erro
%PY% -m PyInstaller --noconfirm --clean installer\PolvoNegroLive.spec || goto erro
if not exist dist\PolvoNegroLive\PolvoNegroLive.exe goto erro
echo.
echo === 2/3 Inno Setup ===
set ISCC=
for %%P in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe") do if exist %%P set ISCC=%%P
if "%ISCC%"=="" (
  echo Inno Setup 6 nao encontrado. O programa ja esta em dist\PolvoNegroLive\PolvoNegroLive.exe ^(modo portatil: crie um arquivo vazio portable.flag ao lado dele^).
  echo Para gerar o Setup.exe instale o Inno Setup 6 ^(jrsoftware.org^) e rode este arquivo de novo.
  goto fim
)
%ISCC% installer\PolvoNegroLive.iss || goto erro
echo.
echo === 3/3 PRONTO ===
echo Instalador: installer\Output\PolvoNegroLive_Setup_8.0.0.exe
goto fim
:erro
echo.
echo *** FALHOU. Veja a mensagem acima. ***
:fim
pause
