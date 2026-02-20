"""
Módulo utilitário centralizado para resolução de paths do aplicativo.

Quando executado em desenvolvimento (via python src/main.py), usa o diretório
do projeto. Quando instalado (via LL.exe), usa %APPDATA%/LiveCaptionArchiver/.

Isso garante que o app funcione tanto em desenvolvimento quanto após instalação
via Inno Setup, evitando problemas de permissão no Program Files.
"""
import os
import sys


def is_frozen():
    """Verifica se o app está rodando como executável PyInstaller."""
    return getattr(sys, 'frozen', False)


def get_app_data_dir():
    """
    Retorna o diretório de dados do aplicativo.
    
    - Windows instalado: %APPDATA%/LiveCaptionArchiver/
    - Desenvolvimento: diretório raiz do projeto (onde main.py roda)
    
    O diretório é criado automaticamente se não existir.
    """
    if is_frozen():
        # Executável instalado — usar AppData
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(base, 'LiveCaptionArchiver')
    else:
        # Desenvolvimento — usar diretório raiz do projeto
        # src/utils/paths.py → subir 3 níveis para raiz do projeto
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_captions_dir():
    """Retorna o diretório de captions. Criado automaticamente."""
    path = os.path.join(get_app_data_dir(), 'captions')
    os.makedirs(path, exist_ok=True)
    return path


def get_logs_dir():
    """Retorna o diretório de logs. Criado automaticamente."""
    path = os.path.join(get_app_data_dir(), 'logs')
    os.makedirs(path, exist_ok=True)
    return path


def get_settings_path():
    """Retorna o caminho completo para o arquivo de configurações do usuário."""
    return os.path.join(get_app_data_dir(), 'user_settings.json')
