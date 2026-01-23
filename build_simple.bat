@echo off
REM Script simples para criar apenas o executável (sem instalador)
REM Útil para testes rápidos

echo ========================================
echo  LiveCaptionArchiver - Build Simples
echo ========================================
echo.

REM Verifica se PyInstaller está instalado
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

REM Limpa builds anteriores
echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist\LiveCaptionArchiver" rmdir /s /q "dist\LiveCaptionArchiver"
if exist "dist\LiveCaptionArchiver.exe" del /q "dist\LiveCaptionArchiver.exe"

REM Cria o executável
echo Criando executavel...
python -m PyInstaller ^
    --name=LiveCaptionArchiver ^
    --onefile ^
    --windowed ^
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

echo.
echo ========================================
echo  Build concluido!
echo ========================================
echo.
echo Executavel criado em: dist\LiveCaptionArchiver.exe
echo.
pause
