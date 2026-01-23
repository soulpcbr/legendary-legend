#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalação do LiveCaptionArchiver
Cria pastas, instala dependências e configura o ambiente.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Informações da aplicação
APP_NAME = "LiveCaptionArchiver"
APP_VERSION = "1.0.0"
INSTALL_DIR = Path.home() / "LiveCaptionArchiver"
VENV_DIR = INSTALL_DIR / "venv"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

def print_header():
    """Imprime cabeçalho do instalador."""
    print("=" * 60)
    print(f"  {APP_NAME} v{APP_VERSION} - Instalador")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    if sys.version_info < (3, 8):
        print("ERRO: Python 3.8 ou superior é necessário!")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detectado")

def create_directories():
    """Cria as pastas necessárias."""
    print("\n[Criando pastas...]")
    directories = [
        INSTALL_DIR,
        INSTALL_DIR / "captions",
        INSTALL_DIR / "logs",
        INSTALL_DIR / "src"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")

def create_virtual_environment():
    """Cria ambiente virtual Python."""
    print("\n[Criando ambiente virtual...]")
    if VENV_DIR.exists():
        print(f"  ⚠ Ambiente virtual já existe em {VENV_DIR}")
        response = input("  Deseja recriar? (s/N): ").strip().lower()
        if response == 's':
            shutil.rmtree(VENV_DIR)
        else:
            print("  ✓ Usando ambiente virtual existente")
            return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print(f"  ✓ Ambiente virtual criado em {VENV_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Erro ao criar ambiente virtual: {e}")
        sys.exit(1)

def get_pip_executable():
    """Retorna o caminho do executável pip do ambiente virtual."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "pip.exe"
    else:
        return VENV_DIR / "bin" / "pip"

def get_python_executable():
    """Retorna o caminho do executável Python do ambiente virtual."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"

def install_dependencies():
    """Instala as dependências do requirements.txt."""
    print("\n[Instalando dependências...]")
    pip = get_pip_executable()
    
    if not pip.exists():
        print(f"  ✗ pip não encontrado em {pip}")
        sys.exit(1)
    
    # Atualiza pip primeiro
    print("  Atualizando pip...")
    try:
        subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True)
        print("  ✓ pip atualizado")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Aviso ao atualizar pip: {e}")
    
    # Instala dependências
    if REQUIREMENTS_FILE.exists():
        print(f"  Instalando de {REQUIREMENTS_FILE}...")
        try:
            subprocess.run([str(pip), "install", "-r", str(REQUIREMENTS_FILE)], check=True)
            print("  ✓ Dependências instaladas")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Erro ao instalar dependências: {e}")
            sys.exit(1)
    else:
        print(f"  ⚠ Arquivo requirements.txt não encontrado em {REQUIREMENTS_FILE}")
        print("  Instalando dependências básicas...")
        dependencies = ["PyQt6", "easyocr", "mss", "opencv-python", "numpy"]
        try:
            subprocess.run([str(pip), "install"] + dependencies, check=True)
            print("  ✓ Dependências básicas instaladas")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Erro ao instalar dependências: {e}")
            sys.exit(1)

def copy_source_files():
    """Copia os arquivos fonte para o diretório de instalação."""
    print("\n[Copiando arquivos...]")
    source_dir = Path(__file__).parent / "src"
    target_dir = INSTALL_DIR / "src"
    
    if source_dir.exists():
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        print(f"  ✓ Arquivos copiados para {target_dir}")
    else:
        print(f"  ⚠ Diretório src não encontrado em {source_dir}")

def create_start_script():
    """Cria script de inicialização."""
    print("\n[Criando script de inicialização...]")
    python_exe = get_python_executable()
    
    if sys.platform == "win32":
        script_path = INSTALL_DIR / "start.bat"
        script_content = f"""@echo off
cd /d "{INSTALL_DIR}"
"{python_exe}" -m src.main
pause
"""
    else:
        script_path = INSTALL_DIR / "start.sh"
        script_content = f"""#!/bin/bash
cd "{INSTALL_DIR}"
"{python_exe}" -m src.main
"""
    
    script_path.write_text(script_content, encoding="utf-8")
    
    if sys.platform != "win32":
        os.chmod(script_path, 0o755)
    
    print(f"  ✓ Script criado: {script_path}")

def create_start_menu_shortcut():
    """Cria atalho no menu iniciar (Windows)."""
    if sys.platform != "win32":
        print("\n[Pulando criação de atalho (não é Windows)]")
        return
    
    print("\n[Criando atalho no menu iniciar...]")
    try:
        import winshell
        from win32com.client import Dispatch
        
        start_menu = Path(winshell.folder("CSIDL_PROGRAMS"))
        app_folder = start_menu / APP_NAME
        app_folder.mkdir(exist_ok=True)
        
        python_exe = get_python_executable()
        script_path = INSTALL_DIR / "start.bat"
        
        shortcut_path = app_folder / f"{APP_NAME}.lnk"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(script_path)
        shortcut.WorkingDirectory = str(INSTALL_DIR)
        shortcut.IconLocation = str(python_exe)
        shortcut.Description = f"{APP_NAME} v{APP_VERSION}"
        shortcut.save()
        
        print(f"  ✓ Atalho criado: {shortcut_path}")
    except ImportError:
        print("  ⚠ Bibliotecas winshell/win32com não disponíveis")
        print("  Instale com: pip install winshell pywin32")
        print("  Atalho não criado, mas você pode usar start.bat")
    except Exception as e:
        print(f"  ⚠ Erro ao criar atalho: {e}")
        print("  Você pode usar start.bat para iniciar o aplicativo")

def main():
    """Função principal do instalador."""
    print_header()
    
    print(f"Diretório de instalação: {INSTALL_DIR}")
    response = input("\nDeseja continuar? (S/n): ").strip().lower()
    if response == 'n':
        print("Instalação cancelada.")
        sys.exit(0)
    
    try:
        check_python_version()
        create_directories()
        create_virtual_environment()
        install_dependencies()
        copy_source_files()
        create_start_script()
        create_start_menu_shortcut()
        
        print("\n" + "=" * 60)
        print("  ✓ Instalação concluída com sucesso!")
        print("=" * 60)
        print(f"\nPara iniciar o aplicativo:")
        print(f"  1. Execute: {INSTALL_DIR / 'start.bat'}")
        print(f"  2. Ou use o atalho no menu Iniciar")
        print(f"\nDiretório de instalação: {INSTALL_DIR}")
        print()
        
    except KeyboardInterrupt:
        print("\n\nInstalação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro durante a instalação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
