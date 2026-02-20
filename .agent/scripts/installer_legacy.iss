; Script de Instalação Inno Setup para LiveCaptionArchiver
; Compile este arquivo usando Inno Setup Compiler (gratuito)
; Download: https://jrsoftware.org/isdl.php

#define AppName "LiveCaptionArchiver"
#define AppVersion "1.0.0"
#define AppPublisher "Legendary Legend"
#define AppURL "https://github.com/legendary-legend"
#define AppExeName "LiveCaptionArchiver.exe"
#define OutputDir "dist"
#define SourceDir "."

[Setup]
; Informações básicas
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir={#OutputDir}
OutputBaseFilename={#AppName}-Setup-v{#AppVersion}
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Arquivos da aplicação
Source: "src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Cria diretórios necessários
[Dirs]
Name: "{app}\captions"; Flags: uninsneveruninstall
Name: "{app}\logs"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Executa script de instalação Python após instalação dos arquivos
Filename: "{app}\install_dependencies.bat"; Description: "Instalar dependências Python agora"; Flags: runascurrentuser waituntilterminated; StatusMsg: "Instalando dependências Python... Isso pode levar alguns minutos."
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  PythonPath: string;
  PythonFound: Boolean;

function InitializeSetup(): Boolean;
begin
  // Verifica se Python está instalado
  PythonFound := RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath);
  if not PythonFound then
    PythonFound := RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath);
  if not PythonFound then
    PythonFound := RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.9\InstallPath', '', PythonPath);
  if not PythonFound then
    PythonFound := RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.8\InstallPath', '', PythonPath);
  
  if not PythonFound then
  begin
    if MsgBox('Python não foi detectado no sistema.' + #13#10 + 
              'O LiveCaptionArchiver requer Python 3.8 ou superior.' + #13#10 + #13#10 +
              'Deseja continuar mesmo assim? (Você precisará instalar Python manualmente)',
              mbConfirmation, MB_YESNO) = IDNO then
      Result := False
    else
      Result := True;
  end
  else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InstallScript: string;
  PythonExe: string;
  ScriptContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Determina o executável Python
    if PythonPath <> '' then
      PythonExe := PythonPath + 'python.exe'
    else
      PythonExe := 'python'; // Usa PATH se não encontrar no registro
    
    // Cria script de instalação de dependências
    InstallScript := ExpandConstant('{app}\install_dependencies.bat');
    ScriptContent := 
      '@echo off' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo  Instalando dependencias do LiveCaptionArchiver' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo.' + #13#10 +
      'cd /d "' + ExpandConstant('{app}') + '"' + #13#10 +
      'echo [1/3] Atualizando pip...' + #13#10 +
      '"' + PythonExe + '" -m pip install --upgrade pip --quiet' + #13#10 +
      'echo [2/3] Instalando dependencias do requirements.txt...' + #13#10 +
      '"' + PythonExe + '" -m pip install -r requirements.txt' + #13#10 +
      'echo [3/3] Verificando instalacao...' + #13#10 +
      '"' + PythonExe + '" -c "import PyQt6; import easyocr; import mss; import cv2; import numpy; print(''Todas as dependencias foram instaladas com sucesso!'')"' + #13#10 +
      'if errorlevel 1 (' + #13#10 +
      '    echo.' + #13#10 +
      '    echo ERRO: Algumas dependencias nao foram instaladas corretamente.' + #13#10 +
      '    echo Verifique sua conexao com a internet e tente novamente.' + #13#10 +
      '    pause' + #13#10 +
      '    exit /b 1' + #13#10 +
      ')' + #13#10 +
      'echo.' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo  Instalacao concluida com sucesso!' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo.' + #13#10 +
      'pause';
    
    SaveStringToFile(InstallScript, ScriptContent, False);
  end;
end;
