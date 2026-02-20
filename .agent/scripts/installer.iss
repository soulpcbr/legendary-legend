; ============================================================================
; LiveCaptionArchiver - Inno Setup Installer Script
; ============================================================================
; Gera o instalador LL.exe auto-suficiente.
; O PyInstaller já empacotou TUDO - o usuário final NÃO precisa de Python.
;
; Funcionalidades:
;   - Instalar / Reparar / Atualizar
;   - Escolha de pasta de instalação
;   - Atalho no Menu Iniciar (opcional)
;   - Atalho no Desktop (opcional)
;   - Desinstalador incluído
;   - Compressão LZMA máxima
;   - Suporte a Português BR e Inglês
;
; Autor: Victor Lacerda Azevedo
; Data: 2026-02-20
; ============================================================================

; === Definições ===
#define AppName "LiveCaptionArchiver"
#define AppShortName "LL"
; Versão - tenta ler do .exe compilado, usa fallback se não existir
#ifexist "..\..\dist\LiveCaptionArchiver\LiveCaptionArchiver.exe"
  #define AppVersion GetStringFileInfo("..\..\dist\LiveCaptionArchiver\LiveCaptionArchiver.exe", "ProductVersion")
#else
  #define AppVersion "1.0.0"
#endif
#define AppPublisher "Victor Lacerda Azevedo"
#define AppURL "https://github.com/soulpcbr/legendary-legend"
#define AppExeName "LiveCaptionArchiver.exe"
#define AppDescription "Arquiva legendas ao vivo usando OCR inteligente"

[Setup]
; ID único e estável para permitir updates/reparos
AppId={{E7A3B5C1-4D2F-48A0-9E67-1C3D5F8B2A94}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases

; Pasta de instalação padrão (Program Files ou AppData do usuário)
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}

; Permitir instalação sem admin se o usuário escolher outra pasta
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Permitir que o usuário desabilite ícones de grupo
AllowNoIcons=yes

; Licença
LicenseFile=..\..\LICENSE

; Saída
OutputDir=..\..\dist
OutputBaseFilename=LL

; Compressão máxima
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; Estilo moderno do wizard
WizardStyle=modern
WizardSizePercent=120,120

; Arquitetura
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Info de desinstalação
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}

; Permitir que usuário veja o que vai ser instalado
ShowComponentSizes=yes

; Informações extras de versão
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppDescription}
VersionInfoCopyright=Copyright (c) 2026 {#AppPublisher}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

; Comportamento de update
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Messages]
; Mensagens customizadas PT-BR
brazilianportuguese.WelcomeLabel2=Este assistente irá instalar o [name] no seu computador.%n%nÉ recomendável fechar todas as outras aplicações antes de continuar.
brazilianportuguese.FinishedLabel=A instalação do [name] foi concluída com sucesso.%n%nO aplicativo pode ser iniciado clicando nos atalhos criados.

[Types]
Name: "full"; Description: "Instalação Completa"
Name: "compact"; Description: "Instalação Mínima"
Name: "custom"; Description: "Instalação Personalizada"; Flags: iscustom

[Components]
Name: "main"; Description: "Aplicativo Principal"; Types: full compact custom; Flags: fixed
Name: "docs"; Description: "Documentação e README"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na &Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked
Name: "startmenuicon"; Description: "Criar atalho no &Menu Iniciar"; GroupDescription: "Atalhos:"; Flags: checked

[Dirs]
; Pastas de dados do usuário (não removidas na desinstalação)
Name: "{app}\captions"; Flags: uninsneveruninstall
Name: "{app}\logs"; Flags: uninsneveruninstall

[Files]
; === Aplicativo Principal (PyInstaller onedir output) ===
Source: "..\..\dist\LiveCaptionArchiver\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main

; === Documentação ===
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: docs
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion; Components: docs

[Icons]
; Menu Iniciar
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "{#AppDescription}"; Tasks: startmenuicon
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

; Desktop
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "{#AppDescription}"; Tasks: desktopicon

[Run]
; Executar após instalação (opcional)
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Fechar o app antes de desinstalar
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM {#AppExeName} 2>nul"; Flags: runhidden

[UninstallDelete]
; Limpar arquivos temporários e cache (preservar captions e logs)
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_internal\__pycache__"

[Code]
// ==========================================================================
// Código Pascal Script para lógica customizada do instalador
// ==========================================================================

var
  RepairPage: TInputOptionWizardPage;
  IsUpdate: Boolean;

// Detecta se já existe uma instalação anterior
function IsAppInstalled(): Boolean;
var
  UninstallKey: string;
begin
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{E7A3B5C1-4D2F-48A0-9E67-1C3D5F8B2A94}_is1';
  Result := RegKeyExists(HKEY_LOCAL_MACHINE, UninstallKey) or
            RegKeyExists(HKEY_CURRENT_USER, UninstallKey);
end;

// Obtém o caminho da instalação anterior
function GetPreviousInstallDir(): string;
var
  UninstallKey: string;
  InstallDir: string;
begin
  Result := '';
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{E7A3B5C1-4D2F-48A0-9E67-1C3D5F8B2A94}_is1';
  
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, UninstallKey, 'InstallLocation', InstallDir) then
    Result := InstallDir
  else if RegQueryStringValue(HKEY_CURRENT_USER, UninstallKey, 'InstallLocation', InstallDir) then
    Result := InstallDir;
end;

function InitializeSetup(): Boolean;
begin
  IsUpdate := IsAppInstalled();
  Result := True;
end;

procedure InitializeWizard();
begin
  if IsUpdate then
  begin
    // Modo update/reparo - customizar mensagem de boas-vindas
    WizardForm.WelcomeLabel2.Caption := 
      'O ' + '{#AppName}' + ' já está instalado no seu computador.' + #13#10 + #13#10 +
      'Este assistente irá atualizar ou reparar a instalação existente.' + #13#10 + #13#10 +
      'Clique em Avançar para continuar.';
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo,
  MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
begin
  Result := '';
  
  if IsUpdate then
    Result := Result + 'Modo: Atualização/Reparo' + NewLine + NewLine
  else
    Result := Result + 'Modo: Nova Instalação' + NewLine + NewLine;
  
  if MemoDirInfo <> '' then
    Result := Result + MemoDirInfo + NewLine + NewLine;
  
  if MemoComponentsInfo <> '' then
    Result := Result + MemoComponentsInfo + NewLine + NewLine;
  
  if MemoTasksInfo <> '' then
    Result := Result + MemoTasksInfo + NewLine + NewLine;
    
  if MemoGroupInfo <> '' then
    Result := Result + MemoGroupInfo + NewLine;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Criar pasta de captions se não existir
    ForceDirectories(ExpandConstant('{app}\captions'));
    ForceDirectories(ExpandConstant('{app}\logs'));
  end;
end;
