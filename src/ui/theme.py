"""
Tema visual dark moderno para o LiveCaptionArchiver.
Aplica uma paleta premium com cores elegantes, bordas arredondadas
e efeitos hover para todos os widgets PyQt6.
"""


# Paleta de cores
COLORS = {
    'bg_primary': '#1a1a2e',       # Fundo principal (azul escuro)
    'bg_secondary': '#16213e',     # Fundo dos cards/grupos
    'bg_tertiary': '#0f3460',      # Fundo de inputs/campos
    'bg_hover': '#1a3a6a',         # Hover em campos
    'accent': '#7c3aed',           # Roxo vibrante (accent principal)
    'accent_hover': '#6d28d9',     # Hover do accent
    'accent_light': '#8b5cf6',     # Variante mais clara do accent
    'success': '#10b981',          # Verde (pronto, sucesso)
    'danger': '#ef4444',           # Vermelho (erro, gravando)
    'warning': '#f59e0b',          # Amarelo (aviso)
    'text_primary': '#e2e8f0',     # Texto principal
    'text_secondary': '#94a3b8',   # Texto secundário/explicação
    'text_muted': '#64748b',       # Texto muito suave
    'border': '#334155',           # Borda padrão
    'border_focus': '#7c3aed',     # Borda com foco
    'scrollbar': '#475569',        # Scrollbar
    'scrollbar_hover': '#64748b',  # Scrollbar hover
}


def get_stylesheet():
    """Retorna o stylesheet QSS completo para aplicar ao app."""
    c = COLORS
    return f"""
    /* ===== BASE ===== */
    QMainWindow {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}

    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 10pt;
    }}

    /* ===== LABELS ===== */
    QLabel {{
        color: {c['text_primary']};
        background-color: transparent;
        border: none;
    }}

    /* ===== BOTÕES ===== */
    QPushButton {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: {c['bg_hover']};
        border-color: {c['accent']};
    }}

    QPushButton:pressed {{
        background-color: {c['accent']};
        border-color: {c['accent_hover']};
    }}

    QPushButton:disabled {{
        background-color: {c['bg_secondary']};
        color: {c['text_muted']};
        border-color: {c['bg_secondary']};
    }}

    /* Botão accent (Iniciar Gravação) */
    QPushButton#btn_record {{
        background-color: {c['accent']};
        color: white;
        border: none;
        font-size: 11pt;
    }}

    QPushButton#btn_record:hover {{
        background-color: {c['accent_hover']};
    }}

    QPushButton#btn_record:checked {{
        background-color: {c['danger']};
    }}

    QPushButton#btn_record:checked:hover {{
        background-color: #dc2626;
    }}

    /* Botão de instalar (verde) */
    QPushButton#btn_install {{
        background-color: {c['success']};
        color: white;
        border: none;
        font-size: 11pt;
    }}

    QPushButton#btn_install:hover {{
        background-color: #059669;
    }}

    /* ===== SPINBOX ===== */
    QSpinBox {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 4px 8px;
        min-height: 24px;
    }}

    QSpinBox:focus {{
        border-color: {c['accent']};
    }}

    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {c['bg_secondary']};
        border: none;
        width: 20px;
    }}

    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {c['bg_hover']};
    }}

    /* ===== CHECKBOX ===== */
    QCheckBox {{
        color: {c['text_primary']};
        spacing: 8px;
        background-color: transparent;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {c['border']};
        background-color: {c['bg_tertiary']};
    }}

    QCheckBox::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}

    QCheckBox::indicator:hover {{
        border-color: {c['accent_light']};
    }}

    /* ===== GROUP BOX ===== */
    QGroupBox {{
        background-color: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding: 16px 12px 12px 12px;
        font-weight: 700;
        font-size: 10pt;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        padding: 0 8px;
        color: {c['accent_light']};
        background-color: {c['bg_secondary']};
    }}

    /* ===== TEXT EDIT (Logs) ===== */
    QTextEdit {{
        background-color: #0d1117;
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px;
        font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
        font-size: 9pt;
        selection-background-color: {c['accent']};
    }}

    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {c['bg_secondary']};
        color: {c['text_secondary']};
        border-top: 1px solid {c['border']};
        font-size: 9pt;
        padding: 4px 8px;
    }}

    /* ===== SCROLLBAR ===== */
    QScrollBar:vertical {{
        background-color: {c['bg_primary']};
        width: 10px;
        margin: 0;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {c['scrollbar']};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {c['scrollbar_hover']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background-color: {c['bg_primary']};
        height: 10px;
        margin: 0;
        border-radius: 5px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {c['scrollbar']};
        border-radius: 5px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {c['scrollbar_hover']};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ===== PROGRESS BAR ===== */
    QProgressBar {{
        background-color: {c['bg_tertiary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        text-align: center;
        color: {c['text_primary']};
        font-weight: 600;
        min-height: 22px;
    }}

    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 5px;
    }}

    /* ===== MENU BAR ===== */
    QMenuBar {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        border-bottom: 1px solid {c['border']};
        padding: 2px;
    }}

    QMenuBar::item {{
        padding: 6px 12px;
        border-radius: 4px;
    }}

    QMenuBar::item:selected {{
        background-color: {c['bg_hover']};
    }}

    QMenu {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: {c['accent']};
        color: white;
    }}

    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['accent']};
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 9pt;
    }}
    """
