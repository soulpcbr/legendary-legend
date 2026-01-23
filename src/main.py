import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

# Adiciona o diretório pai ao path para encontrar o módulo src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import MainWindow
from src.workers.ocr_worker import OCRWorker
from src.core.stabilizer import CaptionStabilizer
from src.core.file_manager import FileManager
from src.core.settings_manager import SettingsManager
from src.core.usage_logger import UsageLogger

class LiveCaptionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # 0. Settings (Configurações Persistidas)
        self.settings = SettingsManager()

        # 0.5. Usage Logger (Log de uso detalhado)
        self.usage_logger = UsageLogger()
        self.usage_logger.log_event("APP_START", "Aplicativo iniciado")

        # 1. Model
        self.file_manager = FileManager()
        
        # Carrega configurações salvas para o Stabilizer
        stabilizer_config = {
            'timeout_ms': self.settings.get('timeout_ms', 1500),
            'auto_timeout': self.settings.get('auto_timeout', False)
        }
        self.stabilizer = CaptionStabilizer(
            on_commit_callback=self.on_stabilizer_commit,
            initial_timeout_ms=stabilizer_config['timeout_ms'],
            usage_logger=self.usage_logger
        )
        
        # Conecta callbacks
        self.stabilizer.set_auto_adjust_callback(self.on_auto_adjust)
        self.stabilizer.set_debug_log_callback(self.on_debug_log)

        # 2. Worker
        self.ocr_worker = OCRWorker()

        # 3. View
        self.main_window = MainWindow()
        
        # Inicialmente desabilita o botão de iniciar gravação até que todos os módulos estejam prontos
        self.main_window.btn_record.setEnabled(False)

        # 4. Wiring (Conexões)
        self._connect_signals()

        # 5. Timer para "ticks" do Stabilizer (verificar timeouts)
        self.stabilizer_timer = QTimer()
        self.stabilizer_timer.timeout.connect(self.stabilizer.force_check)
        self.stabilizer_timer.start(100) # Checa a cada 100ms

        # 6. Carregar configurações salvas na UI
        self._load_ui_settings()
        
        # 7. Verificar dependências do OCR (isso vai sinalizar quando estiver pronto)
        self.ocr_worker.check_dependencies()

    def _connect_signals(self):
        # UI -> Worker (Controles)
        self.main_window.start_requested.connect(self.on_start_requested)
        self.main_window.stop_requested.connect(self.on_stop_requested)
        self.main_window.region_changed.connect(self.ocr_worker.set_region)
        self.main_window.config_changed.connect(self.on_config_changed)
        self.main_window.region_saved.connect(self.on_region_saved)
        self.main_window.config_saved.connect(self.on_config_saved)

        # Dependency Handling
        self.main_window.install_requested.connect(self.on_install_requested)
        
        # Clear Captions
        self.main_window.clear_captions_requested.connect(self.on_clear_captions_requested)

        # Worker -> UI (Erros e Status)
        self.ocr_worker.error_occurred.connect(self.on_worker_error)
        self.ocr_worker.dependency_status.connect(self.on_dependency_status)
        self.ocr_worker.installation_progress.connect(self.main_window.update_status)

        # Worker -> Model (Fluxo de dados)
        self.ocr_worker.text_detected.connect(self.on_text_detected)

    def _load_ui_settings(self):
        """Carrega configurações salvas na UI e aplica ao Stabilizer."""
        # Carregar região de captura se existir
        saved_region = self.settings.get('capture_region')
        if saved_region:
            self.main_window.restore_region(saved_region)
        
        # Carregar outras configurações na UI
        all_settings = self.settings.get_all()
        self.main_window.load_settings(all_settings)
        
        # Aplicar configurações ao Stabilizer
        if 'timeout_ms' in all_settings:
            self.stabilizer.set_timeout_ms(all_settings['timeout_ms'])
        if 'auto_timeout' in all_settings:
            self.stabilizer.set_auto_timeout(all_settings['auto_timeout'])
        if 'similarity_threshold' in all_settings:
            self.stabilizer.set_similarity_threshold(all_settings['similarity_threshold'])
        if 'min_update_interval' in all_settings:
            self.stabilizer.set_min_update_interval(all_settings['min_update_interval'])
        if 'auto_recalc_interval' in all_settings:
            self.stabilizer.set_auto_recalc_interval(all_settings['auto_recalc_interval'])
        if 'auto_smart_adjust' in all_settings:
            self.stabilizer.set_auto_smart_adjust(all_settings['auto_smart_adjust'])
        
        # Aplicar novos parâmetros avançados de jitter
        jitter_params = {}
        if 'jitter_detection_threshold' in all_settings:
            jitter_params['jitter_detection_threshold'] = all_settings['jitter_detection_threshold']
        if 'stability_detection_threshold' in all_settings:
            jitter_params['stability_detection_threshold'] = all_settings['stability_detection_threshold']
        if 'repetition_threshold' in all_settings:
            jitter_params['repetition_threshold'] = all_settings['repetition_threshold']
        
        if jitter_params:
            self.stabilizer.set_jitter_parameters(jitter_params)

    def on_region_saved(self, x, y, w, h):
        """Chamado quando usuário salva uma nova região."""
        region = {'x': x, 'y': y, 'width': w, 'height': h}
        self.settings.set('capture_region', region)
        self.ocr_worker.set_region(x, y, w, h)
        if self.usage_logger:
            self.usage_logger.log_event("REGION_SAVED", "Região de captura salva", region)

    def on_config_saved(self, config):
        """Chamado quando configurações devem ser salvas."""
        # Salva todas as configurações exceto capture_region (que é salva separadamente)
        settings_to_save = {
            'timeout_ms': config.get('timeout_ms', 1500),
            'auto_timeout': config.get('auto_timeout', False),
            'invert_colors': config.get('invert_colors', False),
            'similarity_threshold': config.get('similarity_threshold', 0.6),
            'min_update_interval': config.get('min_update_interval', 50),
            'auto_recalc_interval': config.get('auto_recalc_interval', 30),
            'auto_smart_adjust': config.get('auto_smart_adjust', False),
            'jitter_detection_threshold': config.get('jitter_detection_threshold', 50),
            'stability_detection_threshold': config.get('stability_detection_threshold', 20),
            'repetition_threshold': config.get('repetition_threshold', 0.8)
        }
        self.settings.set_multiple(settings_to_save)
        
        if self.usage_logger:
            self.usage_logger.log_event("CONFIG_SAVED", "Configurações salvas", settings_to_save)
        
        # Aplica as configurações ao Stabilizer imediatamente (mesmo quando não está gravando)
        # Isso garante que as configurações estejam ativas quando a gravação começar
        self.update_stabilizer_config(config)

    def on_install_requested(self):
        self.main_window.set_installing_state()
        self.ocr_worker.install_dependencies()

    def on_dependency_status(self, is_ready, message):
        if is_ready:
            self.main_window.set_ready_state()
            self.main_window.update_status(message)
            # Habilita o botão de iniciar gravação quando todos os módulos estiverem prontos
            # (mas ainda precisa ter região selecionada para funcionar)
            if hasattr(self.main_window, 'btn_record'):
                # O botão só será habilitado se houver região selecionada
                # Isso é verificado em restore_region ou quando região é selecionada
                if self.main_window.capture_region:
                    self.main_window.btn_record.setEnabled(True)
            if self.usage_logger:
                self.usage_logger.log_event("DEPENDENCIES_READY", "Dependências verificadas e prontas")
        else:
            self.main_window.set_dependencies_missing()
            # Mantém o botão desabilitado se dependências não estiverem prontas
            if hasattr(self.main_window, 'btn_record'):
                self.main_window.btn_record.setEnabled(False)
            if self.usage_logger:
                self.usage_logger.log_event("DEPENDENCIES_MISSING", "Dependências não encontradas", {"message": message})
            # Só mostra popup se for uma mensagem de erro real vinda da instalação
            if "Erro" in message:
                self.main_window.show_error("Erro de Dependência", message)

    def on_start_requested(self, config):
        # Aplica configurações iniciais antes de começar
        self.update_stabilizer_config(config)
        self.ocr_worker.update_config(config)

        if not self.ocr_worker.region:
            QMessageBox.warning(self.main_window, "Atenção", "Selecione uma região primeiro!")
            self.main_window.toggle_recording() # Reverte botão
            if self.usage_logger:
                self.usage_logger.log_event("RECORDING_START_FAILED", "Tentativa de iniciar sem região selecionada")
            return

        self.ocr_worker.start()
        if self.usage_logger:
            self.usage_logger.log_event("RECORDING_STARTED", "Gravação iniciada", {
                "timeout_ms": config.get('timeout_ms'),
                "auto_timeout": config.get('auto_timeout'),
                "auto_smart_adjust": config.get('auto_smart_adjust')
            })

    def on_stop_requested(self):
        """Chamado quando usuário para a gravação."""
        self.ocr_worker.stop()
        if self.usage_logger:
            self.usage_logger.log_event("RECORDING_STOPPED", "Gravação parada")

    def on_config_changed(self, config):
        self.update_stabilizer_config(config)
        self.ocr_worker.update_config(config)

    def update_stabilizer_config(self, config):
        self.stabilizer.set_timeout_ms(config['timeout_ms'])
        self.stabilizer.set_auto_timeout(config['auto_timeout'])
        
        # Parâmetros avançados de jitter
        if 'similarity_threshold' in config:
            self.stabilizer.set_similarity_threshold(config['similarity_threshold'])
        if 'min_update_interval' in config:
            self.stabilizer.set_min_update_interval(config['min_update_interval'])
        if 'auto_recalc_interval' in config:
            self.stabilizer.set_auto_recalc_interval(config['auto_recalc_interval'])
        if 'auto_smart_adjust' in config:
            self.stabilizer.set_auto_smart_adjust(config['auto_smart_adjust'])
        
        # Novos parâmetros avançados de jitter
        jitter_params = {}
        if 'jitter_detection_threshold' in config:
            jitter_params['jitter_detection_threshold'] = config['jitter_detection_threshold']
        if 'stability_detection_threshold' in config:
            jitter_params['stability_detection_threshold'] = config['stability_detection_threshold']
        if 'repetition_threshold' in config:
            jitter_params['repetition_threshold'] = config['repetition_threshold']
        
        if jitter_params:
            self.stabilizer.set_jitter_parameters(jitter_params)

    def on_text_detected(self, text):
        if self.usage_logger:
            self.usage_logger.log_event("TEXT_DETECTED", "Texto detectado pelo OCR", {"text_length": len(text) if text else 0})
        self.stabilizer.process_new_text(text)

    def on_stabilizer_commit(self, final_text):
        """Chamado quando uma frase é finalizada e estabilizada."""
        if final_text and final_text.strip():  # Verifica se há texto válido
            # Log de debug para verificar se está chegando aqui
            if hasattr(self.main_window, 'append_debug_log'):
                self.main_window.append_debug_log(f"[COMMIT] Frase commitada: {final_text[:50]}...")
            
            # Salva no arquivo
            self.file_manager.append_text(final_text)
            
            # Adiciona ao log de captura (frases gravadas)
            try:
                self.main_window.append_log(final_text)
                if self.usage_logger:
                    self.usage_logger.log_event("TEXT_SAVED", "Texto salvo no arquivo", {"text_length": len(final_text)})
            except Exception as e:
                print(f"[MAIN] Erro ao adicionar ao log de captura: {e}")
                import traceback
                traceback.print_exc()
                # Tenta adicionar ao log de debug também
                if hasattr(self.main_window, 'append_debug_log'):
                    self.main_window.append_debug_log(f"[ERRO] Falha ao adicionar ao log de captura: {e}")

    def on_auto_adjust(self, parameter, old_value, new_value, reason=None):
        """Chamado quando o autoajuste modifica um parâmetro."""
        # Notifica a UI para mostrar indicador visual
        self.main_window.show_auto_adjust_indicator(parameter, old_value, new_value)
        
        # Adiciona informação de autoajuste no log de DEBUG
        param_names = {
            "timeout_ms": "Timeout",
            "similarity_threshold": "Similaridade",
            "min_update_interval": "Intervalo Mín",
            "repetition_threshold": "Threshold Repetição"
        }
        param_name = param_names.get(parameter, parameter)
        
        # Formata valores para exibição
        if isinstance(new_value, float):
            new_display = f"{new_value:.2f}"
            old_display = f"{old_value:.2f}"
        else:
            new_display = str(new_value)
            old_display = str(old_value)
        
        # Mensagem de log de debug
        reason_text = f" ({reason})" if reason else ""
        log_message = f"[AUTO-AJUSTE] {param_name}: {old_display} → {new_display}{reason_text}"
        self.main_window.append_debug_log(log_message)
        
        if self.usage_logger:
            self.usage_logger.log_event("AUTO_ADJUST_UI_NOTIFIED", f"UI notificada sobre ajuste de {parameter}", {
                "parameter": parameter,
                "old_value": old_value,
                "new_value": new_value,
                "reason": reason
            })
    
    def on_clear_captions_requested(self):
        """Chamado quando usuário solicita limpar todos os arquivos de captions."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self.main_window,
            "Confirmar Limpeza",
            "Tem certeza que deseja remover TODOS os arquivos de captions?\n\n"
            "Isso irá deletar:\n"
            "- O arquivo atual (captions_current.txt)\n"
            "- Todos os arquivos históricos (captions_hist*.txt)\n\n"
            "Esta ação não pode ser desfeita!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.file_manager.clear_all_files()
            if success:
                self.main_window.status_bar.showMessage("✓ Todos os arquivos de captions foram removidos.", 5000)
                if hasattr(self.main_window, 'append_debug_log'):
                    self.main_window.append_debug_log("[INFO] Todos os arquivos de captions foram limpos.")
                if self.usage_logger:
                    self.usage_logger.log_event("CAPTIONS_CLEARED", "Todos os arquivos de captions foram removidos")
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Erro",
                    "Ocorreu um erro ao tentar limpar os arquivos de captions."
                )
    
    def on_debug_log(self, message):
        """Chamado quando há uma mensagem de debug para exibir."""
        self.main_window.append_debug_log(message)

    def on_worker_error(self, title, message):
        self.main_window.show_error(title, message)
        self.main_window.toggle_recording() # Para a UI
        if self.usage_logger:
            self.usage_logger.log_event("ERROR", f"Erro: {title}", {"message": message})

    def run(self):
        self.main_window.show()
        # Inicia verificação de dependências após UI abrir
        QTimer.singleShot(100, self.ocr_worker.check_dependencies)
        
        try:
            sys.exit(self.app.exec())
        finally:
            # Garante que o logger seja fechado ao encerrar
            if hasattr(self, 'usage_logger') and self.usage_logger:
                self.usage_logger.close()
            if hasattr(self, 'file_manager') and self.file_manager:
                self.file_manager.close()

if __name__ == "__main__":
    app = LiveCaptionApp()
    app.run()
