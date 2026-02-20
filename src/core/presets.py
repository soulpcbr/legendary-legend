"""
Presets de configuração para diferentes fontes de legendas.
Cada preset contém valores otimizados para o cenário específico.
"""


PRESETS = {
    'youtube': {
        'name': 'YouTube',
        'description': 'Legendas automáticas do YouTube (geralmente na parte inferior)',
        'timeout_ms': 2000,
        'auto_timeout': True,
        'invert_colors': False,
        'similarity_threshold': 0.6,
        'min_update_interval': 100,
        'auto_recalc_interval': 30,
        'auto_smart_adjust': True,
        'jitter_detection_threshold': 50,
        'stability_detection_threshold': 20,
        'repetition_threshold': 0.8,
    },
    'zoom': {
        'name': 'Zoom',
        'description': 'Legendas ao vivo do Zoom (cc no rodapé)',
        'timeout_ms': 3000,
        'auto_timeout': True,
        'invert_colors': False,
        'similarity_threshold': 0.5,
        'min_update_interval': 150,
        'auto_recalc_interval': 20,
        'auto_smart_adjust': True,
        'jitter_detection_threshold': 60,
        'stability_detection_threshold': 25,
        'repetition_threshold': 0.75,
    },
    'windows_live_captions': {
        'name': 'Windows Live Captions',
        'description': 'Legendas ao vivo do Windows 11 (texto branco em fundo escuro)',
        'timeout_ms': 1500,
        'auto_timeout': True,
        'invert_colors': True,
        'similarity_threshold': 0.6,
        'min_update_interval': 50,
        'auto_recalc_interval': 30,
        'auto_smart_adjust': True,
        'jitter_detection_threshold': 40,
        'stability_detection_threshold': 15,
        'repetition_threshold': 0.8,
    },
    'teams': {
        'name': 'Microsoft Teams',
        'description': 'Legendas ao vivo do Microsoft Teams',
        'timeout_ms': 2500,
        'auto_timeout': True,
        'invert_colors': False,
        'similarity_threshold': 0.55,
        'min_update_interval': 120,
        'auto_recalc_interval': 25,
        'auto_smart_adjust': True,
        'jitter_detection_threshold': 55,
        'stability_detection_threshold': 20,
        'repetition_threshold': 0.75,
    },
    'custom': {
        'name': 'Personalizado',
        'description': 'Configurações personalizadas pelo usuário',
        # Não define valores — usa os valores atuais
    },
}


def get_preset_names():
    """Retorna lista de nomes de presets disponíveis."""
    return [(key, preset['name']) for key, preset in PRESETS.items()]


def get_preset(preset_key):
    """Retorna o preset pelo identificador. None se não existir."""
    return PRESETS.get(preset_key)


def apply_preset(preset_key, settings_manager=None):
    """
    Retorna as configurações do preset como dict.
    Se settings_manager for fornecido, salva no arquivo.
    """
    preset = PRESETS.get(preset_key)
    if not preset or preset_key == 'custom':
        return None
    
    # Copia apenas as configurações (exclui 'name' e 'description')
    config = {k: v for k, v in preset.items() if k not in ('name', 'description')}
    
    if settings_manager:
        settings_manager.set_multiple(config)
    
    return config
