@echo off
color 0A
mode con: cols=80 lines=25

echo ==============================================================================
echo                 LiveCaptionArchiver - Gerador de Instalador
echo ==============================================================================
echo.
echo  Este script automatiza todo o processo de criacao do instalador (LL.exe)
echo  para seus usuarios finais.
echo.
echo  O que ele vai fazer:
echo  1. Criar um ambiente virtual isolado (build_env)
echo  2. Instalar todas as dependencias necessarias (PyQt6, OCR, MSS, etc.)
echo  3. Compilar o codigo fonte Python para um executavel Windows
echo  4. Chamar o Inno Setup para empacotar tudo no arquivo final "LL.exe"
echo.
echo  REQUISITOS:
echo  - Instalar o Inno Setup 6 (https://jrsoftware.org/isdl.php)
echo  - Ter o Python instalado
echo.
echo  Pressione qualquer tecla para iniciar o processo de build...
pause > nul

cls
echo ==============================================================================
echo                       Iniciando Processo de Build...
echo ==============================================================================
echo.
call .agent\scripts\build_installer.bat

echo.
echo ==============================================================================
echo                       Processo Finalizado!
echo ==============================================================================
echo.
echo  Se tudo ocorreu bem, o instalador esta na pasta:
echo  dist\LL.exe
echo.
echo  Envie apenas o arquivo "LL.exe" para os usuarios finais.
echo.
pause
