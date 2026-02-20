@echo off
REM ============================================================================
REM  LiveCaptionArchiver - Build Installer Script
REM ============================================================================
REM  Este script:
REM    1. Cria um ambiente virtual limpo para build
REM    2. Instala dependencias e PyInstaller
REM    3. Compila o app com PyInstaller (--onedir)
REM    4. Gera o instalador LL.exe com Inno Setup
REM
REM  Modo de uso: Execute este .bat na raiz do projeto ou de qualquer lugar.
REM  O script detecta automaticamente a raiz do projeto.
REM
REM  Pre-requisitos:
REM    - Python 3.8+ instalado e no PATH
REM    - Inno Setup 6 instalado (https://jrsoftware.org/isdl.php)
REM
REM  Saida: dist\LL.exe (instalador auto-suficiente)
REM ============================================================================
setlocal EnableDelayedExpansion

REM === Determinar diretorio raiz do projeto ===
set "SCRIPT_DIR=%~dp0"
REM O script esta em .agent\scripts\, entao a raiz eh 2 niveis acima
pushd "%SCRIPT_DIR%..\.."
set "PROJECT_ROOT=%CD%"
popd

echo.
echo  ============================================================
echo   LiveCaptionArchiver - Build System v2.0
echo  ============================================================
echo   Projeto: %PROJECT_ROOT%
echo   Data:    %DATE% %TIME%
echo  ============================================================
echo.

REM === Passo 0: Verificar Python ===
echo [0/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERRO FATAL: Python nao encontrado no PATH!
    echo  Instale Python 3.8+ de https://www.python.org/downloads/
    echo  Marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo   OK - Python %PYTHON_VERSION% detectado
echo.

REM === Passo 1: Criar/Usar ambiente virtual de build ===
echo [1/6] Configurando ambiente virtual de build...
set "BUILD_VENV=%PROJECT_ROOT%\build_env"

if exist "%BUILD_VENV%\Scripts\python.exe" (
    echo   Ambiente virtual existente encontrado. Reutilizando...
) else (
    echo   Criando novo ambiente virtual em %BUILD_VENV%...
    python -m venv "%BUILD_VENV%"
    if errorlevel 1 (
        echo   ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)

REM Ativa o venv
call "%BUILD_VENV%\Scripts\activate.bat"
echo   OK - Ambiente virtual ativado
echo.

REM === Passo 2: Instalar dependencias ===
echo [2/6] Instalando dependencias...
echo   Atualizando pip...
python -m pip install --upgrade pip --quiet 2>nul

echo   Instalando requirements.txt...
pip install -r "%PROJECT_ROOT%\requirements.txt" --quiet 2>nul
if errorlevel 1 (
    echo   AVISO: Algumas dependencias podem nao ter sido instaladas.
    echo   Tentando instalar individualmente...
    pip install PyQt6 easyocr mss opencv-python numpy --quiet 2>nul
)

echo   Instalando PyInstaller...
pip install pyinstaller --quiet 2>nul

echo   OK - Dependencias instaladas
echo.

REM === Passo 3: Limpar builds anteriores ===
echo [3/6] Limpando builds anteriores...
if exist "%PROJECT_ROOT%\build" (
    rmdir /s /q "%PROJECT_ROOT%\build" 2>nul
    echo   Pasta build/ removida
)
if exist "%PROJECT_ROOT%\dist\LiveCaptionArchiver" (
    rmdir /s /q "%PROJECT_ROOT%\dist\LiveCaptionArchiver" 2>nul
    echo   Pasta dist/LiveCaptionArchiver/ removida
)
if exist "%PROJECT_ROOT%\dist\LiveCaptionArchiver.exe" (
    del /q "%PROJECT_ROOT%\dist\LiveCaptionArchiver.exe" 2>nul
    echo   Arquivo dist/LiveCaptionArchiver.exe removido
)
if exist "%PROJECT_ROOT%\dist\LL.exe" (
    del /q "%PROJECT_ROOT%\dist\LL.exe" 2>nul
    echo   Arquivo dist/LL.exe antigo removido
)
echo   OK - Limpeza concluida
echo.

REM === Passo 4: Compilar com PyInstaller ===
echo [4/6] Compilando com PyInstaller (isso pode levar alguns minutos)...
echo.

cd /d "%PROJECT_ROOT%"

python -m PyInstaller ^
    --name=LiveCaptionArchiver ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --log-level=WARN ^
    --add-data "src;src" ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=easyocr ^
    --hidden-import=mss ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --collect-all=easyocr ^
    --collect-all=PyQt6 ^
    --collect-all=mss ^
    src\main.py

if errorlevel 1 (
    echo.
    echo  ERRO: Falha ao compilar com PyInstaller!
    echo  Verifique os erros acima e tente novamente.
    echo.
    pause
    exit /b 1
)

REM Verificar se o executavel foi criado
if not exist "%PROJECT_ROOT%\dist\LiveCaptionArchiver\LiveCaptionArchiver.exe" (
    echo.
    echo  ERRO: Executavel nao foi gerado!
    echo  O PyInstaller pode ter falhado silenciosamente.
    echo.
    pause
    exit /b 1
)

echo.
echo   OK - Executavel compilado com sucesso
echo   Localizado em: dist\LiveCaptionArchiver\LiveCaptionArchiver.exe
echo.

REM === Passo 5: Criar instalador com Inno Setup ===
echo [5/6] Gerando instalador com Inno Setup...

REM Procurar Inno Setup em locais comuns
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

REM Procurar via PATH
if "!ISCC!"=="" (
    where ISCC.exe >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=*" %%p in ('where ISCC.exe') do set "ISCC=%%p"
    )
)

if "!ISCC!"=="" (
    echo.
    echo  ============================================================
    echo   AVISO: Inno Setup Compiler (ISCC.exe) nao encontrado!
    echo  ============================================================
    echo.
    echo   O executavel foi compilado com sucesso em:
    echo     dist\LiveCaptionArchiver\LiveCaptionArchiver.exe
    echo.
    echo   Para gerar o instalador LL.exe, voce precisa:
    echo     1. Baixar Inno Setup 6: https://jrsoftware.org/isdl.php
    echo     2. Instalar o Inno Setup
    echo     3. Executar este script novamente
    echo.
    echo   Ou manualmente:
    echo     "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .agent\scripts\installer.iss
    echo.
    pause
    exit /b 0
)

echo   Inno Setup encontrado: !ISCC!
echo   Compilando instalador...
echo.

"!ISCC!" "%PROJECT_ROOT%\.agent\scripts\installer.iss"

if errorlevel 1 (
    echo.
    echo  ERRO: Falha ao gerar o instalador!
    echo  Verifique os erros acima.
    echo.
    pause
    exit /b 1
)

REM Verificar se LL.exe foi criado
if not exist "%PROJECT_ROOT%\dist\LL.exe" (
    echo.
    echo  ERRO: O instalador LL.exe nao foi encontrado em dist\
    echo.
    pause
    exit /b 1
)

echo.
echo   OK - Instalador gerado com sucesso!
echo.

REM === Passo 6: Resumo ===
echo [6/6] Build concluido!
echo.
echo  ============================================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo  ============================================================
echo.
echo   Arquivos gerados:
echo.
echo     Executavel:   dist\LiveCaptionArchiver\LiveCaptionArchiver.exe
echo     Instalador:   dist\LL.exe
echo.
echo   Distribua apenas o arquivo LL.exe para os usuarios finais.
echo   Ele contem tudo necessario para instalar o programa.
echo.
echo   O instalador permite:
echo     - Escolher pasta de instalacao
echo     - Criar atalho no Desktop
echo     - Criar atalho no Menu Iniciar
echo     - Instalar / Reparar / Atualizar
echo.
echo  ============================================================
echo.

REM Desativa venv
call deactivate 2>nul

pause
exit /b 0
