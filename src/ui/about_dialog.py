"""
Dialog "Sobre" com informações do aplicativo.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src import __version__
from src.ui.theme import COLORS


class AboutDialog(QDialog):
    """Dialog com informações sobre o aplicativo."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre — LiveCaptionArchiver")
        self.setFixedSize(420, 350)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 20)
        
        # Título
        title = QLabel("LiveCaptionArchiver")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['accent_light']};")
        layout.addWidget(title)
        
        # Versão
        version = __version__.get_version()
        version_label = QLabel(f"Versão {version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt;")
        layout.addWidget(version_label)
        
        # Descrição
        desc = QLabel(
            "Captura, estabiliza e arquiva legendas ao vivo\n"
            "de qualquer fonte na tela usando OCR.\n\n"
            "Construído com PyQt6 + EasyOCR + OpenCV"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 10pt; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Separador
        separator = QLabel("─" * 40)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(separator)
        
        # Atalhos
        shortcuts = QLabel(
            "⌨ Atalhos de Teclado\n\n"
            "Ctrl+R — Iniciar/Parar Gravação\n"
            "Ctrl+S — Salvar Região\n"
            "Ctrl+E — Exportar SRT\n"
            "Ctrl+Q — Sair"
        )
        shortcuts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcuts.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        layout.addWidget(shortcuts)
        
        layout.addStretch()
        
        # Botão fechar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
