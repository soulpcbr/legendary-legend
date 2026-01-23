@echo off
REM Template para instalação de dependências
REM Este arquivo será modificado pelo instalador Inno Setup

echo ========================================
echo  Instalando dependencias do LiveCaptionArchiver
echo ========================================
echo.

cd /d "{app}"

REM Atualiza pip
echo [1/3] Atualizando pip...
python -m pip install --upgrade pip --quiet

REM Instala dependências
echo [2/3] Instalando dependencias do requirements.txt...
python -m pip install -r requirements.txt

echo [3/3] Verificando instalacao...
python -c "import PyQt6; import easyocr; import mss; import cv2; import numpy; print('Todas as dependencias foram instaladas com sucesso!')"

if errorlevel 1 (
    echo.
    echo ERRO: Algumas dependencias nao foram instaladas corretamente.
    echo Verifique sua conexao com a internet e tente novamente.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Instalacao concluida com sucesso!
echo ========================================
echo.
pause
