import json
import os

class SettingsManager:
    """Gerencia persistência de configurações do usuário em JSON."""
    
    def __init__(self, settings_file="user_settings.json"):
        """
        :param settings_file: Nome do arquivo de configurações (padrão: user_settings.json)
        """
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Carrega configurações do arquivo JSON, retorna dict vazio se não existir."""
        if not os.path.exists(self.settings_file):
            return self._get_default_settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self._get_default_settings()
    
    def _get_default_settings(self):
        """Retorna configurações padrão."""
        return {
            "capture_region": None,  # {x, y, width, height}
            "timeout_ms": 1500,
            "auto_timeout": False,
            "invert_colors": False,
            "similarity_threshold": 0.6,
            "min_update_interval": 50,
            "auto_recalc_interval": 30,
            "auto_smart_adjust": False,
            "jitter_detection_threshold": 50,
            "stability_detection_threshold": 20,
            "repetition_threshold": 0.8
        }
    
    def save_settings(self):
        """Salva configurações atuais no arquivo JSON."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Configurações salvas em {self.settings_file}")
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def get(self, key, default=None):
        """Retorna uma configuração específica."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """
        Define um valor de configuração e salva no arquivo.
        
        :param key: Chave da configuração
        :param value: Valor a ser definido
        """
        self.settings[key] = value
        self.save_settings()
    
    def set_multiple(self, settings_dict):
        """
        Define múltiplas configurações de uma vez e salva no arquivo.
        
        :param settings_dict: Dicionário com as configurações a serem definidas
        """
        self.settings.update(settings_dict)
        self.save_settings()
    
    def get_all(self):
        """Retorna todas as configurações atuais."""
        return self.settings.copy()
    
    def reset_to_defaults(self):
        """Restaura configurações para os valores padrão."""
        self.settings = self._get_default_settings()
        self.save_settings()
