"""
Utilitário para auto-start do LiveCaptionArchiver com o Windows.
Usa o Windows Registry (HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run)
para registrar o executável na inicialização do sistema.
"""
import os
import sys

_REGISTRY_KEY_PATH = r'Software\Microsoft\Windows\CurrentVersion\Run'
_REGISTRY_VALUE_NAME = 'LiveCaptionArchiver'


def _get_exe_path():
    """Retorna o caminho do executável atual."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def is_autostart_enabled():
    """Verifica se o auto-start está habilitado via Windows Registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _REGISTRY_KEY_PATH,
            0,
            winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, _REGISTRY_VALUE_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def enable_autostart():
    """
    Registra o executável no Windows Registry para iniciar com o sistema.
    Retorna True em caso de sucesso, False em caso de erro.
    """
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _REGISTRY_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, _REGISTRY_VALUE_NAME, 0, winreg.REG_SZ, _get_exe_path())
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Erro ao habilitar auto-start: {e}")
        return False


def disable_autostart():
    """
    Remove o auto-start do Windows Registry.
    Retorna True em caso de sucesso, False em caso de erro.
    """
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _REGISTRY_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, _REGISTRY_VALUE_NAME)
        except FileNotFoundError:
            pass  # Já não existe
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Erro ao desabilitar auto-start: {e}")
        return False
