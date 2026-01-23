from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QSpinBox, QCheckBox,
                             QGroupBox, QStatusBar, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from src.ui.overlay import OverlaySelector

class MainWindow(QMainWindow):
    # Sinais para o Controller
    start_requested = pyqtSignal(dict) # Envia config atual
    stop_requested = pyqtSignal()
    region_changed = pyqtSignal(int, int, int, int) # x, y, w, h
    config_changed = pyqtSignal(dict) # Envia nova config em tempo real
    install_requested = pyqtSignal() # Solicita instalação de dependências

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiveCaptionArchiver")
        self.resize(500, 600)

        self.is_recording = False
        self.capture_region = None # (x, y, w, h)

        # UI Components
        self.init_ui()

        # Overlay
        self.overlay = OverlaySelector()
        self.overlay.area_selected.connect(self.on_region_selected)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Controles Superiores ---
        controls_layout = QHBoxLayout()

        self.btn_select_region = QPushButton("Selecionar Região")
        self.btn_select_region.clicked.connect(self.open_overlay)
        controls_layout.addWidget(self.btn_select_region)

        self.btn_record = QPushButton("Iniciar Gravação")
        self.btn_record.setCheckable(True)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_record.setEnabled(False) # Só habilita após selecionar região
        controls_layout.addWidget(self.btn_record)

        # Botão de Instalação (Inicialmente Oculto)
        self.btn_install = QPushButton("Instalar Dependências")
        self.btn_install.setStyleSheet("background-color: #e6ffcc; color: darkgreen; font-weight: bold;")
        self.btn_install.setVisible(False)
        self.btn_install.clicked.connect(self.install_requested.emit)
        controls_layout.addWidget(self.btn_install)

        layout.addLayout(controls_layout)

        # --- Configurações ---
        config_group = QGroupBox("Configurações")
        config_layout = QVBoxLayout()

        # Timeout Row
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout Silêncio (ms):"))
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(500, 10000)
        self.spin_timeout.setValue(1500)
        self.spin_timeout.setSingleStep(100)
        self.spin_timeout.valueChanged.connect(self.emit_config_update)
        timeout_layout.addWidget(self.spin_timeout)

        self.chk_auto_timeout = QCheckBox("Auto-Ajuste (Dinâmico)")
        self.chk_auto_timeout.setToolTip("Ajusta o timeout automaticamente a cada 30s baseado na velocidade da fala.")
        self.chk_auto_timeout.toggled.connect(self.toggle_auto_timeout)
        timeout_layout.addWidget(self.chk_auto_timeout)
        config_layout.addLayout(timeout_layout)

        # Image Processing Row
        img_layout = QHBoxLayout()
        self.chk_invert_colors = QCheckBox("Inverter Cores (Texto Branco/Fundo Preto)")
        self.chk_invert_colors.setChecked(False)
        self.chk_invert_colors.setToolTip("Marque se a legenda original for texto branco em fundo preto.")
        self.chk_invert_colors.toggled.connect(self.emit_config_update)
        img_layout.addWidget(self.chk_invert_colors)
        config_layout.addLayout(img_layout)

        layout.addWidget(config_group)

        # --- Log ---
        layout.addWidget(QLabel("Log de Captura:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Verificando dependências...")

    # --- Controle de Estado de Dependências ---
    def set_dependencies_missing(self):
        """Estado quando modelos OCR não foram encontrados."""
        self.btn_select_region.setVisible(False)
        self.btn_record.setVisible(False)

        self.btn_install.setVisible(True)
        self.btn_install.setEnabled(True)
        self.btn_install.setText("Instalar Dependências (Automático)")
        self.status_bar.showMessage("Dependências necessárias. Clique em Instalar para baixar.")

    def set_installing_state(self):
        """Estado durante download."""
        self.btn_install.setEnabled(False)
        self.btn_install.setText("Instalando... Aguarde.")
        self.status_bar.showMessage("Baixando modelos OCR. Isso pode levar alguns minutos...")

    def set_ready_state(self):
        """Estado normal de operação."""
        self.btn_install.setVisible(False)
        self.btn_select_region.setVisible(True)
        self.btn_record.setVisible(True)
        self.status_bar.showMessage("Pronto. Selecione uma região para começar.")

    def open_overlay(self):
        self.overlay.show()
        if not self.capture_region:
            self.overlay.resize(400, 100)
            self.overlay.move(100, 100)

    def on_region_selected(self, x, y, w, h):
        self.capture_region = (x, y, w, h)
        self.btn_select_region.setText(f"Região: {w}x{h} @ ({x},{y})")
        self.btn_record.setEnabled(True)
        self.status_bar.showMessage(f"Região definida: {x},{y} {w}x{h}")
        self.region_changed.emit(x, y, w, h)

    def toggle_recording(self):
        if self.btn_record.isChecked():
            # Iniciar
            self.is_recording = True
            self.btn_record.setText("Parar Gravação")
            self.btn_record.setStyleSheet("background-color: #ffcccc; color: red;")
            self.btn_select_region.setEnabled(False)
            self.start_requested.emit(self.get_current_config())
            self.status_bar.showMessage("Gravando...")
        else:
            # Parar
            self.is_recording = False
            self.btn_record.setText("Iniciar Gravação")
            self.btn_record.setStyleSheet("")
            self.btn_select_region.setEnabled(True)
            self.stop_requested.emit()
            self.status_bar.showMessage("Parado.")

    def toggle_auto_timeout(self, checked):
        self.spin_timeout.setEnabled(not checked)
        self.emit_config_update()

    def get_current_config(self):
        return {
            "timeout_ms": self.spin_timeout.value(),
            "auto_timeout": self.chk_auto_timeout.isChecked(),
            "invert_colors": self.chk_invert_colors.isChecked()
        }

    def emit_config_update(self):
        if self.is_recording:
            self.config_changed.emit(self.get_current_config())

    @pyqtSlot(str)
    def append_log(self, text):
        self.log_area.append(text)
        sb = self.log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    @pyqtSlot(str)
    def update_status(self, text):
        self.status_bar.showMessage(text)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
