from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QSpinBox, QCheckBox,
                             QGroupBox, QStatusBar, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot, QTimer
from src.ui.overlay import OverlaySelector
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

    def __init__(self):
        super().__init__()
        version = __version__.get_version()
        self.setWindowTitle(f"LiveCaptionArchiver v{version}")
        self.resize(850, 650)  # Tamanho aumentado para caber todos os elementos e explicações
        self.setMinimumSize(750, 600)

        self.is_recording = False
        self.capture_region = None # (x, y, w, h)
        self.dependencies_ready = False  # Rastreia se as dependências estão prontas

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
        controls_layout.setSpacing(5)  # Espaçamento entre botões

        self.btn_select_region = QPushButton("Selecionar Região")
        self.btn_select_region.clicked.connect(self.open_overlay)
        self.btn_select_region.setMinimumWidth(120)
        controls_layout.addWidget(self.btn_select_region)

        # Botão de Salvar Seleção
        self.btn_save_region = QPushButton("Salvar Seleção")
        self.btn_save_region.clicked.connect(self.save_current_region)
        self.btn_save_region.setEnabled(False)  # Só habilita se houver região selecionada ou overlay aberto
        self.btn_save_region.setStyleSheet("background-color: #fff4cc; color: darkorange; font-weight: bold;")
        self.btn_save_region.setToolTip("Confirma a seleção no overlay (como ENTER) ou salva a região atual")
        self.btn_save_region.setMinimumWidth(120)
        controls_layout.addWidget(self.btn_save_region)

        self.btn_record = QPushButton("Iniciar Gravação")
        self.btn_record.setCheckable(True)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_record.setEnabled(False) # Só habilita após selecionar região
        self.btn_record.setMinimumWidth(130)
        controls_layout.addWidget(self.btn_record)

        # Botão de Abrir Pasta de Logs
        self.btn_open_logs = QPushButton("Abrir Logs")
        self.btn_open_logs.clicked.connect(self.open_log_folder)
        self.btn_open_logs.setStyleSheet("background-color: #e6f3ff; color: darkblue; font-weight: bold;")
        self.btn_open_logs.setMinimumWidth(100)
        controls_layout.addWidget(self.btn_open_logs)

        # Botão de Limpar Captions
        self.btn_clear_captions = QPushButton("Limpar Captions")
        self.btn_clear_captions.clicked.connect(self.clear_captions_requested.emit)
        self.btn_clear_captions.setStyleSheet("background-color: #ffe6e6; color: darkred; font-weight: bold;")
        self.btn_clear_captions.setMinimumWidth(120)
        self.btn_clear_captions.setToolTip("Remove todos os arquivos de captions (atual e históricos)")
        controls_layout.addWidget(self.btn_clear_captions)

        controls_layout.addStretch()  # Adiciona espaço flexível à direita

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

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # --- Configurações Avançadas (Jitter) ---
        advanced_group = QGroupBox("Configurações Avançadas")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(10)  # Espaçamento entre elementos

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
        layout.addWidget(advanced_group)

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

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        version = __version__.get_version()
        self.status_bar.showMessage(f"Verificando dependências... | v{version}")

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

        self.btn_install.setVisible(True)
        self.btn_install.setEnabled(True)
        self.btn_install.setText("Instalar Dependências (Automático)")
        self.status_bar.showMessage("Dependências necessárias. Clique em Instalar para baixar.")
        self._update_record_button_state()

    def set_installing_state(self):
        """Estado durante download."""
        self.dependencies_ready = False
        self.btn_install.setEnabled(False)
        self.btn_install.setText("Instalando... Aguarde.")
        self.status_bar.showMessage("Baixando modelos OCR. Isso pode levar alguns minutos...")
        self._update_record_button_state()

    def set_ready_state(self):
        """Estado normal de operação."""
        self.dependencies_ready = True
        self.btn_install.setVisible(False)
        self.btn_select_region.setVisible(True)
        self.btn_record.setVisible(True)
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
            "invert_colors": self.chk_invert_colors.isChecked(),
            "similarity_threshold": self.spin_similarity.value() / 100.0,
            "min_update_interval": self.spin_min_interval.value(),
            "auto_recalc_interval": self.spin_recalc_interval.value(),
            "auto_smart_adjust": self.chk_smart_adjust.isChecked(),
            "jitter_detection_threshold": self.spin_jitter_threshold.value(),
            "stability_detection_threshold": self.spin_stability_threshold.value(),
            "repetition_threshold": self.spin_repetition_threshold.value() / 100.0
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
        
        # Carrega valores salvos (usa valores padrão se não existirem)
        self.spin_timeout.setValue(settings.get('timeout_ms', 1500))
        self.chk_auto_timeout.setChecked(settings.get('auto_timeout', False))
        self.chk_invert_colors.setChecked(settings.get('invert_colors', False))
        
        similarity = settings.get('similarity_threshold', 0.6)
        self.spin_similarity.setValue(int(similarity * 100) if isinstance(similarity, float) else similarity)
        
        self.spin_min_interval.setValue(settings.get('min_update_interval', 50))
        self.spin_recalc_interval.setValue(settings.get('auto_recalc_interval', 30))
        self.chk_smart_adjust.setChecked(settings.get('auto_smart_adjust', False))
        
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

    def open_log_folder(self):
        """Abre a pasta onde os logs são salvos."""
        import os
        log_dir = "captions"
        if os.path.exists(log_dir):
            os.startfile(log_dir)
        else:
            QMessageBox.warning(self, "Pasta Não Encontrada", f"A pasta de logs não existe: {log_dir}")

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
