"""
Informações de versão do LiveCaptionArchiver
"""
__version__ = "1.0.0"
__version_info__ = tuple(map(int, __version__.split('.')))
__app_name__ = "LiveCaptionArchiver"
__author__ = "Legendary Legend"
__description__ = "Arquiva legendas ao vivo usando OCR"

def get_version():
    """Retorna a versão como string."""
    return __version__

def get_version_info():
    """Retorna a versão como tupla (major, minor, patch)."""
    return __version_info__

def get_app_info():
    """Retorna informações completas da aplicação."""
    return {
        "name": __app_name__,
        "version": __version__,
        "author": __author__,
        "description": __description__
    }
