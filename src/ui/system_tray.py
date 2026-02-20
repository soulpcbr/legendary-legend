"""
System tray integration para o LiveCaptionArchiver.
Permite minimizar o app para a bandeja do sistema e oferece
controles rápidos via menu contextual.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject


class SystemTrayManager(QObject):
    """Gerencia o ícone na bandeja do sistema e suas ações."""
    
    # Sinais
    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    toggle_recording_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.is_recording = False
        self._setup_tray()
    
    def _setup_tray(self):
        """Configura o ícone e menu da bandeja."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("[TRAY] System tray não disponível neste sistema")
            return
        
        self.tray_icon = QSystemTrayIcon(self.parent())
        
        # Ícone padrão (usa ícone do sistema)
        from PyQt6.QtWidgets import QApplication
        app_icon = QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_MediaPlay
        )
        self.tray_icon.setIcon(app_icon)
        self.tray_icon.setToolTip("LiveCaptionArchiver")
        
        # Menu contextual
        menu = QMenu()
        
        self.action_show = QAction("Abrir", self.parent())
        self.action_show.triggered.connect(self.show_requested.emit)
        menu.addAction(self.action_show)
        
        menu.addSeparator()
        
        self.action_toggle = QAction("Iniciar Gravação", self.parent())
        self.action_toggle.triggered.connect(self.toggle_recording_requested.emit)
        menu.addAction(self.action_toggle)
        
        menu.addSeparator()
        
        self.action_quit = QAction("Sair", self.parent())
        self.action_quit.triggered.connect(self.quit_requested.emit)
        menu.addAction(self.action_quit)
        
        self.tray_icon.setContextMenu(menu)
        
        # Duplo clique abre a janela
        self.tray_icon.activated.connect(self._on_activated)
    
    def _on_activated(self, reason):
        """Chamado quando o ícone na bandeja é ativado."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()
    
    def show(self):
        """Mostra o ícone na bandeja."""
        if self.tray_icon:
            self.tray_icon.show()
    
    def hide(self):
        """Esconde o ícone da bandeja."""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def update_recording_state(self, is_recording):
        """Atualiza o texto do botão de gravação no menu."""
        self.is_recording = is_recording
        if hasattr(self, 'action_toggle'):
            self.action_toggle.setText(
                "Parar Gravação" if is_recording else "Iniciar Gravação"
            )
        
        # Atualiza tooltip
        if self.tray_icon:
            status = "Gravando..." if is_recording else "Pronto"
            self.tray_icon.setToolTip(f"LiveCaptionArchiver — {status}")
    
    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Mostra uma notificação toast do sistema."""
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon, 3000)
    
    def is_available(self):
        """Retorna True se a bandeja do sistema está disponível."""
        return self.tray_icon is not None
