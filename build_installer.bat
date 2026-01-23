@echo off
REM Script para construir o instalador do LiveCaptionArchiver
REM Requer: PyInstaller e Inno Setup Compiler

echo ========================================
echo  LiveCaptionArchiver - Build Installer
echo ========================================
echo.

REM Verifica se PyInstaller está instalado
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/4] Instalando PyInstaller...
    python -m pip install pyinstaller
) else (
    echo [1/4] PyInstaller ja esta instalado
)

REM Limpa builds anteriores
echo [2/4] Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist\LiveCaptionArchiver" rmdir /s /q "dist\LiveCaptionArchiver"
if exist "dist\LiveCaptionArchiver.exe" del /q "dist\LiveCaptionArchiver.exe"

REM Cria o executável com PyInstaller
echo [3/4] Criando executavel com PyInstaller...
python -m PyInstaller ^
    --name=LiveCaptionArchiver ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data "src;src" ^
    --hidden-import=PyQt6 ^
    --hidden-import=easyocr ^
    --hidden-import=mss ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --collect-all=easyocr ^
    --collect-all=PyQt6 ^
    src/main.py

if errorlevel 1 (
    echo ERRO: Falha ao criar executavel!
    pause
    exit /b 1
)

REM Verifica se Inno Setup está instalado
set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_SETUP% (
    set INNO_SETUP="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist %INNO_SETUP% (
    echo.
    echo [4/4] AVISO: Inno Setup Compiler nao encontrado!
    echo.
    echo Para criar o instalador, voce precisa:
    echo 1. Baixar Inno Setup: https://jrsoftware.org/isdl.php
    echo 2. Instalar o Inno Setup
    echo 3. Executar manualmente: ISCC installer.iss
    echo.
    echo O executavel foi criado em: dist\LiveCaptionArchiver.exe
    echo.
    pause
    exit /b 0
)

REM Compila o instalador
echo [4/4] Criando instalador com Inno Setup...
%INNO_SETUP% installer.iss

if errorlevel 1 (
    echo ERRO: Falha ao criar instalador!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build concluido com sucesso!
echo ========================================
echo.
echo Arquivos gerados:
echo   - Executavel: dist\LiveCaptionArchiver.exe
echo   - Instalador: dist\LiveCaptionArchiver-Setup-v1.0.0.exe
echo.
pause
