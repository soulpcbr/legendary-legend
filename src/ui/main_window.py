from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QSpinBox, QCheckBox,
                             QGroupBox, QStatusBar, QMessageBox, QProgressBar,
                             QTabWidget, QListWidget, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QAction
from src.ui.overlay import OverlaySelector
from src.ui.theme import get_stylesheet
from src import __version__

class MainWindow(QMainWindow):
    # Sinais para o Controller
    start_requested = pyqtSignal(dict) # Envia config atual
    stop_requested = pyqtSignal()
    region_changed = pyqtSignal(int, int, int, int) # x, y, w, h
    config_changed = pyqtSignal(dict) # Envia nova config em tempo real
    install_requested = pyqtSignal() # Solicita instalação de dependências
    region_saved = pyqtSignal(int, int, int, int) # Emite quando região é salva manualmente
    config_saved = pyqtSignal(dict) # Emite quando configurações devem ser salvas
    clear_captions_requested = pyqtSignal() # Solicita limpeza de todos os arquivos de captions
    custom_dir_changed = pyqtSignal(str) # Emite quando o usuário seleciona uma nova pasta de destino
    generate_summary_requested = pyqtSignal() # Solicita geração do sumário
    
    # Sinais de Reparo e Validação
    verify_system_requested = pyqtSignal()
    repair_system_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        version = __version__.get_version()
        self.setWindowTitle(f"LiveCaptionArchiver v{version}")
        self.resize(900, 700)
        self.setMinimumSize(800, 600)

        self.is_recording = False
        self.capture_region = None # (x, y, w, h)
        self.dependencies_ready = False  # Rastreia se as dependências estão prontas

        # Aplica tema dark
        self.setStyleSheet(get_stylesheet())

        # UI Components
        self.init_ui()

        # Overlay
        self.overlay = OverlaySelector()
        self.overlay.area_selected.connect(self.on_region_selected)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab Widget Global
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Aba 1: Principal
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, "📹 Gravação e Opções")
        layout = QVBoxLayout(self.tab_main)

        # --- Controles Superiores ---
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)  # Espaçamento entre botões

        self.btn_select_region = QPushButton("⬚  Selecionar Região")
        self.btn_select_region.setObjectName("btn_select_region")
        self.btn_select_region.clicked.connect(self.open_overlay)
        self.btn_select_region.setMinimumWidth(140)
        controls_layout.addWidget(self.btn_select_region)

        # Botão de Salvar Seleção
        self.btn_save_region = QPushButton("💾  Salvar Seleção")
        self.btn_save_region.setObjectName("btn_save_region")
        self.btn_save_region.clicked.connect(self.save_current_region)
        self.btn_save_region.setEnabled(False)
        self.btn_save_region.setToolTip("Confirma a seleção no overlay (como ENTER) ou salva a região atual")
        self.btn_save_region.setMinimumWidth(140)
        controls_layout.addWidget(self.btn_save_region)

        self.btn_record = QPushButton("⏺  Iniciar Gravação")
        self.btn_record.setObjectName("btn_record")
        self.btn_record.setCheckable(True)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_record.setEnabled(False)
        self.btn_record.setMinimumWidth(160)
        controls_layout.addWidget(self.btn_record)

        controls_layout.addStretch()

        # --- Controles de Utilidade (Logs, Pastas, Sumário) ---
        utils_layout = QHBoxLayout()
        utils_layout.setSpacing(5)

        # Botão de Abrir Pasta de Logs
        self.btn_open_logs = QPushButton("📂  Abrir Logs")
        self.btn_open_logs.setObjectName("btn_open_logs")
        self.btn_open_logs.clicked.connect(self.open_log_folder)
        self.btn_open_logs.setMinimumWidth(120)
        utils_layout.addWidget(self.btn_open_logs)

        # Botão de Escolher Pasta
        self.btn_choose_dir = QPushButton("📁 Escolher Pasta")
        self.btn_choose_dir.setObjectName("btn_choose_dir")
        self.btn_choose_dir.clicked.connect(self.choose_output_dir)
        self.btn_choose_dir.setMinimumWidth(120)
        self.btn_choose_dir.setToolTip("Escolha onde salvar os arquivos .txt")
        utils_layout.addWidget(self.btn_choose_dir)

        # Botão de Limpar Captions
        self.btn_clear_captions = QPushButton("🗑  Limpar Captions")
        self.btn_clear_captions.setObjectName("btn_clear_captions")
        self.btn_clear_captions.clicked.connect(self.clear_captions_requested.emit)
        self.btn_clear_captions.setMinimumWidth(140)
        self.btn_clear_captions.setToolTip("Remove todos os arquivos de captions (atual e históricos)")
        utils_layout.addWidget(self.btn_clear_captions)
        
        # Botão de Gerar Sumário
        self.btn_generate_summary = QPushButton("📋 Gerar Sumário")
        self.btn_generate_summary.setObjectName("btn_generate_summary")
        self.btn_generate_summary.clicked.connect(self.generate_summary_requested.emit)
        self.btn_generate_summary.setMinimumWidth(140)
        self.btn_generate_summary.setToolTip("Identifica todas palavras únicas nos textos e gera um sumario.txt")
        utils_layout.addWidget(self.btn_generate_summary)
        
        # Label de informações do sumário
        self.lbl_summary_info = QLabel("")
        self.lbl_summary_info.setStyleSheet("color: #aaa; font-size: 9pt;")
        utils_layout.addWidget(self.lbl_summary_info)

        utils_layout.addStretch()
        
        # Ocultamos do row de gravação e movemos p baixo
        layout.addLayout(controls_layout)
        layout.addLayout(utils_layout)

        # Aba 2: Verificação e Reparo
        self.tab_repair = QWidget()
        self.tabs.addTab(self.tab_repair, "🔧 Verificação e Reparo")
        repair_layout = QVBoxLayout(self.tab_repair)

        repair_header = QLabel("<h3>Diagnóstico e Reparo do Sistema</h3>")
        repair_layout.addWidget(repair_header)

        repair_desc = QLabel("Verifique se as pastas de saída estão acessíveis e se os modelos pesados de Inteligência Artificial já estão baixados e instalados no seu computador. Clique em Resolver Tudo caso encontre problemas.")
        repair_desc.setWordWrap(True)
        repair_layout.addWidget(repair_desc)

        # Lista de diagnósticos
        self.list_diagnostics = QListWidget()
        # Estilo customizado na list_diagnostics para fundo escuro, texto claro
        self.list_diagnostics.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0; font-size: 10pt; padding: 5px;")
        repair_layout.addWidget(self.list_diagnostics)

        # Botões de reparo
        repair_btn_layout = QHBoxLayout()
        self.btn_verify = QPushButton("🔍 Verificar Tudo")
        self.btn_verify.setObjectName("btn_verify")
        self.btn_verify.setMinimumHeight(40)
        self.btn_verify.clicked.connect(self.verify_system_requested.emit)
        repair_btn_layout.addWidget(self.btn_verify)

        self.btn_repair = QPushButton("🛠️ Resolver Tudo (Fazer 100% Funcionar)")
        self.btn_repair.setObjectName("btn_repair")
        self.btn_repair.setMinimumHeight(40)
        self.btn_repair.setStyleSheet("background-color: #005A36; color: white; font-weight: bold;")
        self.btn_repair.clicked.connect(self.repair_system_requested.emit)
        repair_btn_layout.addWidget(self.btn_repair)

        repair_layout.addLayout(repair_btn_layout)

        # Progress bar para download oculta e movida para a aba de Reparo, caso precise de feedback visual
        self.repair_progress_bar = QProgressBar()
        self.repair_progress_bar.setVisible(False)
        self.repair_progress_bar.setTextVisible(True)
        self.repair_progress_bar.setFormat("Baixando e Reparando... %p%")
        repair_layout.addWidget(self.repair_progress_bar)

        # --- Configurações (Ainda na aba Principal) ---
        config_group = QGroupBox("Configurações")
        config_layout = QVBoxLayout()
        config_layout.setSpacing(10)  # Espaçamento entre elementos

        # Timeout Row
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout Silêncio (ms):"))
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(500, 10000)
        self.spin_timeout.setValue(1500)
        self.spin_timeout.setSingleStep(100)
        self.spin_timeout.valueChanged.connect(self.emit_config_update)
        timeout_layout.addWidget(self.spin_timeout)
        
        # Explicação
        timeout_explanation = QLabel("Tempo de espera antes de finalizar uma frase")
        timeout_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        timeout_layout.addWidget(timeout_explanation)
        timeout_layout.addStretch()  # Adiciona espaço flexível

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
        
        # Explicação
        invert_explanation = QLabel("Inverte cores da imagem para melhorar OCR")
        invert_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        img_layout.addWidget(invert_explanation)
        img_layout.addStretch()  # Adiciona espaço flexível
        config_layout.addLayout(img_layout)

        # Configurações de Arquivo
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Máx Arquivos Salvos:"))
        self.spin_max_files = QSpinBox()
        self.spin_max_files.setRange(1, 50)
        self.spin_max_files.setValue(5)
        self.spin_max_files.setToolTip("Quantidade máxima de arquivos de textos históricos a serem mantidos.")
        self.spin_max_files.valueChanged.connect(self.emit_config_update)
        file_layout.addWidget(self.spin_max_files)
        
        file_layout.addWidget(QLabel("Tamanho Máx (MB):"))
        self.spin_max_size_mb = QSpinBox()
        self.spin_max_size_mb.setRange(1, 100)
        self.spin_max_size_mb.setValue(2)
        self.spin_max_size_mb.setToolTip("Tamanho máximo em MegaBytes antes de rotacionar para um novo arquivo.")
        self.spin_max_size_mb.valueChanged.connect(self.emit_config_update)
        file_layout.addWidget(self.spin_max_size_mb)
        
        file_layout.addStretch()
        config_layout.addLayout(file_layout)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # --- Configurações Avançadas (Colapsável) ---
        advanced_header_layout = QHBoxLayout()
        self.btn_toggle_advanced = QPushButton("▶  Configurações Avançadas")
        self.btn_toggle_advanced.setObjectName("btn_toggle_advanced")
        self.btn_toggle_advanced.clicked.connect(self._toggle_advanced_settings)
        self.btn_toggle_advanced.setMinimumWidth(220)
        advanced_header_layout.addWidget(self.btn_toggle_advanced)
        advanced_header_layout.addStretch()
        layout.addLayout(advanced_header_layout)

        # Container colapsável
        self.advanced_container = QWidget()
        advanced_group = QGroupBox("")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(10)

        # Threshold de Similaridade
        similarity_layout = QHBoxLayout()
        similarity_layout.addWidget(QLabel("Similaridade Min:"))
        self.spin_similarity = QSpinBox()
        self.spin_similarity.setRange(30, 90)
        self.spin_similarity.setValue(60)
        self.spin_similarity.setSuffix("%")
        self.spin_similarity.setToolTip("Threshold mínimo para considerar que o texto é a mesma frase.")
        self.spin_similarity.valueChanged.connect(self.emit_config_update)
        similarity_layout.addWidget(self.spin_similarity)
        
        # Explicação
        similarity_explanation = QLabel("Similaridade mínima para considerar mesma frase")
        similarity_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        similarity_layout.addWidget(similarity_explanation)
        similarity_layout.addStretch()  # Adiciona espaço flexível
        advanced_layout.addLayout(similarity_layout)

        # Intervalo Mínimo de Update
        min_interval_layout = QHBoxLayout()
        min_interval_layout.addWidget(QLabel("Intervalo Mín (ms):"))
        self.spin_min_interval = QSpinBox()
        self.spin_min_interval.setRange(10, 200)
        self.spin_min_interval.setValue(50)
        self.spin_min_interval.setToolTip("Intervalo mínimo entre atualizações para considerar ruído.")
        self.spin_min_interval.valueChanged.connect(self.emit_config_update)
        min_interval_layout.addWidget(self.spin_min_interval)
        
        # Explicação
        min_interval_explanation = QLabel("Tempo mínimo entre atualizações (filtra ruído)")
        min_interval_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        min_interval_layout.addWidget(min_interval_explanation)
        min_interval_layout.addStretch()  # Adiciona espaço flexível
        advanced_layout.addLayout(min_interval_layout)

        # Intervalo de Recálculo
        recalc_layout = QHBoxLayout()
        recalc_layout.addWidget(QLabel("Recalc. Auto (s):"))
        self.spin_recalc_interval = QSpinBox()
        self.spin_recalc_interval.setRange(5, 60)
        self.spin_recalc_interval.setValue(30)
        self.spin_recalc_interval.setToolTip("Intervalo para recalcular parâmetros automaticamente.")
        self.spin_recalc_interval.valueChanged.connect(self.emit_config_update)
        recalc_layout.addWidget(self.spin_recalc_interval)
        
        # Explicação
        recalc_explanation = QLabel("Intervalo para recalcular parâmetros automaticamente")
        recalc_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        recalc_layout.addWidget(recalc_explanation)
        recalc_layout.addStretch()  # Adiciona espaço flexível
        advanced_layout.addLayout(recalc_layout)

        # Threshold de Detecção de Jitter
        jitter_threshold_layout = QHBoxLayout()
        jitter_threshold_layout.addWidget(QLabel("Threshold Jitter (ms):"))
        self.spin_jitter_threshold = QSpinBox()
        self.spin_jitter_threshold.setRange(20, 200)
        self.spin_jitter_threshold.setValue(50)
        self.spin_jitter_threshold.setToolTip("Threshold para detectar jitter alto (desvio padrão).")
        self.spin_jitter_threshold.valueChanged.connect(self.emit_config_update)
        jitter_threshold_layout.addWidget(self.spin_jitter_threshold)
        
        # Explicação
        jitter_explanation = QLabel("Limite para detectar instabilidade (jitter alto)")
        jitter_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        jitter_threshold_layout.addWidget(jitter_explanation)
        jitter_threshold_layout.addStretch()
        advanced_layout.addLayout(jitter_threshold_layout)

        # Threshold de Detecção de Estabilidade
        stability_threshold_layout = QHBoxLayout()
        stability_threshold_layout.addWidget(QLabel("Threshold Estabilidade (ms):"))
        self.spin_stability_threshold = QSpinBox()
        self.spin_stability_threshold.setRange(5, 50)
        self.spin_stability_threshold.setValue(20)
        self.spin_stability_threshold.setToolTip("Threshold para detectar estabilidade (desvio padrão baixo).")
        self.spin_stability_threshold.valueChanged.connect(self.emit_config_update)
        stability_threshold_layout.addWidget(self.spin_stability_threshold)
        
        # Explicação
        stability_explanation = QLabel("Limite para detectar estabilidade (variação baixa)")
        stability_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        stability_threshold_layout.addWidget(stability_explanation)
        stability_threshold_layout.addStretch()
        advanced_layout.addLayout(stability_threshold_layout)

        # Threshold de Repetição
        repetition_layout = QHBoxLayout()
        repetition_layout.addWidget(QLabel("Threshold Repetição:"))
        self.spin_repetition_threshold = QSpinBox()
        self.spin_repetition_threshold.setRange(50, 95)
        self.spin_repetition_threshold.setValue(80)
        self.spin_repetition_threshold.setSuffix("%")
        self.spin_repetition_threshold.setToolTip("Similaridade mínima para considerar texto como repetição.")
        self.spin_repetition_threshold.valueChanged.connect(self.emit_config_update)
        repetition_layout.addWidget(self.spin_repetition_threshold)
        
        # Explicação
        repetition_explanation = QLabel("Similaridade mínima para considerar repetição")
        repetition_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        repetition_layout.addWidget(repetition_explanation)
        repetition_layout.addStretch()
        advanced_layout.addLayout(repetition_layout)

        # Ajuste Inteligente
        smart_adjust_layout = QHBoxLayout()
        self.chk_smart_adjust = QCheckBox("Ajuste Inteligente Automático")
        self.chk_smart_adjust.setToolTip("Ajusta automaticamente parâmetros baseados na qualidade das detecções.")
        self.chk_smart_adjust.toggled.connect(self.emit_config_update)
        smart_adjust_layout.addWidget(self.chk_smart_adjust)
        
        # Explicação
        smart_adjust_explanation = QLabel("Ajusta parâmetros automaticamente baseado na qualidade")
        smart_adjust_explanation.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        smart_adjust_layout.addWidget(smart_adjust_explanation)
        
        # Indicador de Autoajuste Ativo
        self.lbl_auto_adjust_indicator = QLabel("")
        self.lbl_auto_adjust_indicator.setStyleSheet("color: green; font-weight: bold; background-color: #e6ffe6; padding: 2px 8px; border-radius: 3px;")
        self.lbl_auto_adjust_indicator.setVisible(False)
        smart_adjust_layout.addWidget(self.lbl_auto_adjust_indicator)
        smart_adjust_layout.addStretch()
        advanced_layout.addLayout(smart_adjust_layout)

        advanced_group.setLayout(advanced_layout)
        advanced_container_layout = QVBoxLayout(self.advanced_container)
        advanced_container_layout.setContentsMargins(0, 0, 0, 0)
        advanced_container_layout.addWidget(advanced_group)
        self.advanced_container.setVisible(False)  # Inicia colapsado
        layout.addWidget(self.advanced_container)

        # --- Logs Separados ---
        logs_layout = QHBoxLayout()
        
        # Log de Captura (frases gravadas)
        capture_log_widget = QWidget()
        capture_log_layout = QVBoxLayout(capture_log_widget)
        capture_log_layout.setContentsMargins(0, 0, 0, 0)
        capture_log_layout.addWidget(QLabel("Log de Captura (15 linhas):"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(120)
        # Background escuro com texto claro
        self.log_area.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0; font-size: 10pt;")
        capture_log_layout.addWidget(self.log_area)
        logs_layout.addWidget(capture_log_widget)
        
        # Log de Debug (autoajustes, decisões)
        debug_log_widget = QWidget()
        debug_log_layout = QVBoxLayout(debug_log_widget)
        debug_log_layout.setContentsMargins(0, 0, 0, 0)
        debug_log_layout.addWidget(QLabel("Log de Debug (15 linhas):"))
        self.debug_log_area = QTextEdit()
        self.debug_log_area.setReadOnly(True)
        self.debug_log_area.setMinimumHeight(120)
        # Background escuro como o log de captura, com texto claro para contraste
        self.debug_log_area.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0; font-family: 'Courier New', monospace; font-size: 9pt;")
        debug_log_layout.addWidget(self.debug_log_area)
        logs_layout.addWidget(debug_log_widget)
        
        layout.addLayout(logs_layout)

        # --- Status Bar Central ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        version = __version__.get_version()
        self.status_bar.showMessage(f"Verificando dependências... | v{version}")

    # --- Controle de Estado de Diagnósticos ---
    def add_diagnostic_item(self, message, is_ok=True, pending=False):
        """Adiciona ou atualiza item na aba de diagnósticos."""
        item = QListWidgetItem()
        if pending:
            icon = "⏳"
            color = "#a0a000"
        elif is_ok:
            icon = "✅"
            color = "#00a000"
        else:
            icon = "❌"
            color = "#d00000"
            
        item.setText(f"{icon} {message}")
        self.list_diagnostics.addItem(item)
        
    def clear_diagnostics(self):
        self.list_diagnostics.clear()

    # --- Controle de Estado de Dependências ---
    def _update_record_button_state(self):
        """Atualiza o estado do botão de gravação baseado em região e dependências."""
        should_enable = self.capture_region is not None and self.dependencies_ready
        self.btn_record.setEnabled(should_enable)
    
    def set_dependencies_missing(self):
        """Estado quando modelos OCR não foram encontrados."""
        self.dependencies_ready = False
        self.btn_select_region.setVisible(False)
        self.btn_record.setVisible(False)

        self.status_bar.showMessage("Dependências incompletas! Vá para a guia de Verificação e Reparo.")
        self._update_record_button_state()

    def set_installing_state(self):
        """Estado durante download e reparo."""
        self.dependencies_ready = False
        self.btn_repair.setEnabled(False)
        self.btn_verify.setEnabled(False)
        self.repair_progress_bar.setVisible(True)
        self.status_bar.showMessage("Baixando e reparando o sistema. Isso pode demorar...")
        self._update_record_button_state()

    def set_ready_state(self):
        """Estado normal de operação."""
        self.dependencies_ready = True
        self.btn_select_region.setVisible(True)
        self.btn_record.setVisible(True)
        self.btn_repair.setEnabled(True)
        self.btn_verify.setEnabled(True)
        self.repair_progress_bar.setVisible(False)
        self.status_bar.showMessage("Pronto. Selecione uma região para começar.")
        self._update_record_button_state()

    def open_overlay(self):
        self.overlay.show()
        # Habilita o botão de salvar quando o overlay é aberto
        self.btn_save_region.setEnabled(True)
        if self.capture_region:
            # Restaura posição e tamanho salvos
            x, y, w, h = self.capture_region
            self.overlay.move(x, y)
            self.overlay.resize(w, h)
        else:
            # Posição padrão se não houver região salva
            self.overlay.resize(400, 100)
            self.overlay.move(100, 100)

    def on_region_selected(self, x, y, w, h):
        self.capture_region = (x, y, w, h)
        self.btn_select_region.setText(f"Região: {w}x{h} @ ({x},{y})")
        self.btn_save_region.setEnabled(True)
        self._update_record_button_state()  # Atualiza estado baseado em região e dependências
        self.status_bar.showMessage(f"Região definida: {x},{y} {w}x{h}")
        self.region_changed.emit(x, y, w, h)
        # Persiste automaticamente quando selecionada via overlay
        self.region_saved.emit(x, y, w, h)

    def _toggle_advanced_settings(self):
        """Mostra/esconde as configurações avançadas."""
        is_visible = self.advanced_container.isVisible()
        self.advanced_container.setVisible(not is_visible)
        if is_visible:
            self.btn_toggle_advanced.setText("▶  Configurações Avançadas")
        else:
            self.btn_toggle_advanced.setText("▼  Configurações Avançadas")

    def toggle_recording(self):
        if self.btn_record.isChecked():
            # Iniciar
            self.is_recording = True
            self.btn_record.setText("⏹  Parar Gravação")
            self.btn_select_region.setEnabled(False)
            self.start_requested.emit(self.get_current_config())
            self.status_bar.showMessage("⏺ Gravando...")
        else:
            # Parar
            self.is_recording = False
            self.btn_record.setText("⏺  Iniciar Gravação")
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
            "invert_colors": self.chk_invert_colors.isChecked(),
            "similarity_threshold": self.spin_similarity.value() / 100.0,
            "min_update_interval": self.spin_min_interval.value(),
            "auto_recalc_interval": self.spin_recalc_interval.value(),
            "auto_smart_adjust": self.chk_smart_adjust.isChecked(),
            "jitter_detection_threshold": self.spin_jitter_threshold.value(),
            "stability_detection_threshold": self.spin_stability_threshold.value(),
            "repetition_threshold": self.spin_repetition_threshold.value() / 100.0,
            "max_log_files": self.spin_max_files.value(),
            "max_log_size_mb": self.spin_max_size_mb.value()
        }

    def emit_config_update(self):
        config = self.get_current_config()
        # Salva configurações sempre que mudarem (persistência)
        self.config_saved.emit(config)
        # Aplica mudanças em tempo real apenas se estiver gravando
        if self.is_recording:
            self.config_changed.emit(config)

    def load_settings(self, settings):
        """Carrega configurações salvas na UI."""
        # Desconecta temporariamente os sinais para evitar salvar durante o carregamento
        self.spin_timeout.blockSignals(True)
        self.chk_auto_timeout.blockSignals(True)
        self.chk_invert_colors.blockSignals(True)
        self.spin_similarity.blockSignals(True)
        self.spin_min_interval.blockSignals(True)
        self.spin_recalc_interval.blockSignals(True)
        self.chk_smart_adjust.blockSignals(True)
        self.spin_jitter_threshold.blockSignals(True)
        self.spin_stability_threshold.blockSignals(True)
        self.spin_repetition_threshold.blockSignals(True)
        self.spin_max_files.blockSignals(True)
        self.spin_max_size_mb.blockSignals(True)
        
        # Carrega valores salvos (usa valores padrão se não existirem)
        self.spin_timeout.setValue(settings.get('timeout_ms', 1500))
        self.chk_auto_timeout.setChecked(settings.get('auto_timeout', False))
        self.chk_invert_colors.setChecked(settings.get('invert_colors', False))
        
        similarity = settings.get('similarity_threshold', 0.6)
        self.spin_similarity.setValue(int(similarity * 100) if isinstance(similarity, float) else similarity)
        
        self.spin_min_interval.setValue(settings.get('min_update_interval', 50))
        self.spin_recalc_interval.setValue(settings.get('auto_recalc_interval', 30))
        self.chk_smart_adjust.setChecked(settings.get('auto_smart_adjust', False))
        
        # Carrega limitadores de arquivo
        self.spin_max_files.setValue(settings.get('max_log_files', 5))
        self.spin_max_size_mb.setValue(settings.get('max_log_size_mb', 2))
        
        # Novos parâmetros avançados
        self.spin_jitter_threshold.setValue(settings.get('jitter_detection_threshold', 50))
        self.spin_stability_threshold.setValue(settings.get('stability_detection_threshold', 20))
        repetition = settings.get('repetition_threshold', 0.8)
        self.spin_repetition_threshold.setValue(int(repetition * 100) if isinstance(repetition, float) else int(repetition * 100))
        
        # Reconecta os sinais
        self.spin_timeout.blockSignals(False)
        self.chk_auto_timeout.blockSignals(False)
        self.chk_invert_colors.blockSignals(False)
        self.spin_similarity.blockSignals(False)
        self.spin_min_interval.blockSignals(False)
        self.spin_recalc_interval.blockSignals(False)
        self.chk_smart_adjust.blockSignals(False)
        self.spin_jitter_threshold.blockSignals(False)
        self.spin_stability_threshold.blockSignals(False)
        self.spin_repetition_threshold.blockSignals(False)
        self.spin_max_files.blockSignals(False)
        self.spin_max_size_mb.blockSignals(False)

    def save_current_region(self):
        """Salva a região de captura atual. Se o overlay estiver aberto, confirma a seleção."""
        # Se o overlay estiver visível, confirma a seleção (como o ENTER)
        if self.overlay.isVisible():
            self.overlay.confirm_selection()
            return
        
        # Se não houver overlay aberto, salva a região atual se existir
        if self.capture_region:
            x, y, w, h = self.capture_region
            # Emite o sinal para salvar
            self.region_saved.emit(x, y, w, h)
            # Feedback visual
            self.status_bar.showMessage(f"✓ Região salva com sucesso: {w}x{h} @ ({x},{y})", 3000)
            # Feedback no botão temporariamente
            original_text = self.btn_save_region.text()
            self.btn_save_region.setText("✓ Salva!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.btn_save_region.setText(original_text))
        else:
            QMessageBox.warning(self, "Atenção", "Nenhuma região selecionada para salvar!\n\nSelecione uma região primeiro usando o botão 'Selecionar Região'.")

    def restore_region(self, region_data):
        """Restaura região de captura salva."""
        if region_data and 'x' in region_data:
            self.capture_region = (region_data['x'], region_data['y'], region_data['width'], region_data['height'])
            self.btn_select_region.setText(f"Região: {region_data['width']}x{region_data['height']} @ ({region_data['x']},{region_data['y']})")
            self.btn_save_region.setEnabled(True)
            self._update_record_button_state()  # Atualiza estado baseado em região e dependências
            # Emite sinal para atualizar o worker
            self.region_changed.emit(region_data['x'], region_data['y'], region_data['width'], region_data['height'])

    def choose_output_dir(self):
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "Selecione a pasta para salvar legendas")
        if dir_path:
            self.custom_dir_changed.emit(dir_path)
            self.status_bar.showMessage(f"Nova pasta: {dir_path}", 3000)

    # Nova signal para permitir a main app resolver a pasta ou o próprio FileManager.
    open_folder_requested = pyqtSignal()

    def open_log_folder(self):
        """Abre a pasta onde os logs são salvos."""
        self.open_folder_requested.emit()

    @pyqtSlot(str)
    def append_log(self, text):
        """Adiciona texto ao log de captura mantendo apenas as últimas 15 linhas."""
        if not text or not text.strip():
            return  # Ignora texto vazio
        
        text_cleaned = text.strip()
        MAX_LOG_LINES = 15
        
        try:
            # Verifica se o widget existe
            if not hasattr(self, 'log_area') or self.log_area is None:
                return
            
            # Obtém o conteúdo atual
            content = self.log_area.toPlainText()
            lines = []
            
            if content and content.strip():
                # Separa linhas e remove vazias
                all_lines = content.split('\n')
                lines = [line for line in all_lines if line.strip()]
            
            # Adiciona a nova linha
            lines.append(text_cleaned)
            
            # Mantém apenas as últimas MAX_LOG_LINES linhas (substitui as antigas)
            if len(lines) > MAX_LOG_LINES:
                lines = lines[-MAX_LOG_LINES:]
            
            # Atualiza o conteúdo do log
            new_content = '\n'.join(lines)
            
            # Atualiza diretamente
            self.log_area.setPlainText(new_content)
            self.log_area.repaint()
            
            # Scroll para o final após um pequeno delay
            QTimer.singleShot(50, self._scroll_log_to_bottom)
        except Exception as e:
            print(f"[UI] Erro ao atualizar log de captura: {e}")
            import traceback
            traceback.print_exc()
            # Tenta adicionar ao log de debug
            if hasattr(self, 'append_debug_log'):
                try:
                    self.append_debug_log(f"[ERRO] Falha ao atualizar log de captura: {e}")
                except:
                    pass
    
    def _scroll_log_to_bottom(self):
        """Scroll o log de captura para o final."""
        try:
            sb = self.log_area.verticalScrollBar()
            if sb:
                sb.setValue(sb.maximum())
        except:
            pass
    
    @pyqtSlot(str)
    def append_debug_log(self, text):
        """Adiciona texto ao log de debug mantendo apenas as últimas 15 linhas."""
        if not text or not text.strip():
            return  # Ignora texto vazio
        
        MAX_LOG_LINES = 15
        
        # Obtém o conteúdo atual (mantém todas as linhas, incluindo vazias)
        content = self.debug_log_area.toPlainText()
        lines = content.split('\n')
        
        # Remove linhas vazias do final
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Adiciona a nova linha
        lines.append(text.strip())
        
        # Mantém apenas as últimas MAX_LOG_LINES linhas (substitui as antigas)
        if len(lines) > MAX_LOG_LINES:
            lines = lines[-MAX_LOG_LINES:]
        
        # Atualiza o conteúdo do log
        self.debug_log_area.setPlainText('\n'.join(lines))
        
        # Scroll para o final
        sb = self.debug_log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    @pyqtSlot(str)
    def update_status(self, text):
        self.status_bar.showMessage(text)

    def show_auto_adjust_indicator(self, parameter, old_value, new_value):
        """Mostra indicador visual quando autoajuste modifica um parâmetro."""
        param_names = {
            "timeout_ms": "Timeout",
            "similarity_threshold": "Similaridade",
            "min_update_interval": "Intervalo Mín"
        }
        param_name = param_names.get(parameter, parameter)
        
        # Formata valores para exibição
        if isinstance(new_value, float):
            new_display = f"{new_value:.2f}"
            old_display = f"{old_value:.2f}"
        else:
            new_display = str(new_value)
            old_display = str(old_value)
        
        # Mostra indicador
        self.lbl_auto_adjust_indicator.setText(f"⚙️ {param_name}: {old_display} → {new_display}")
        self.lbl_auto_adjust_indicator.setVisible(True)
        
        # Atualiza status bar
        self.status_bar.showMessage(f"Autoajuste: {param_name} ajustado de {old_display} para {new_display}", 5000)
        
        # Esconde após 5 segundos
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.lbl_auto_adjust_indicator.setVisible(False))

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        
    @pyqtSlot(str)
    def update_summary_info(self, text):
        self.lbl_summary_info.setText(text)
