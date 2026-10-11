; Inno Setup 6.3+ . Gera installer\Output\PolvoNegroLive_Setup_8.0.0.exe a partir de dist\PolvoNegroLive (criado pelo PyInstaller).
; Instala POR USUARIO (sem administrador). Atualizar = rodar o Setup novo por cima: %APPDATA%\PolvoNegroLive (configuracoes) NUNCA e tocado.
#define AppName "Polvo Negro Live"
#define AppVersion "8.0.0"
#define AppPublisher "Diêgo Botelho Pereira"
#define AppExe "PolvoNegroLive.exe"

[Setup]
AppId={{B7C1E2A4-5D3F-4A6B-9C8E-2F1D0A7B4C93}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\PolvoNegroLive
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=Output
OutputBaseFilename=PolvoNegroLive_Setup_{#AppVersion}
SetupIconFile=..\assets\logo\polvonegro.ico
UninstallDisplayIcon={app}\{#AppExe}
WizardImageFile=..\assets\logo\wizard_large.bmp
WizardSmallImageFile=..\assets\logo\wizard_small.bmp
WizardStyle=modern
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "..\dist\PolvoNegroLive\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Abrir o {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
function FFmpegAchado(): Boolean;
begin
  Result := FileSearch('ffmpeg.exe', GetEnv('PATH')) <> '';
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and (not FFmpegAchado()) then
    WizardForm.FinishedLabel.Caption := WizardForm.FinishedLabel.Caption + #13#10#13#10 +
      'ATENÇÃO: não encontrei o FFmpeg (ffmpeg.exe) no PATH do Windows. Instale o FFmpeg de 64 bits (ou coloque ffmpeg.exe na pasta ffmpeg\bin do programa). O Polvo Negro Live avisa na abertura.';
end;
