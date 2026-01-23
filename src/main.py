import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

from src.ui.main_window import MainWindow
from src.workers.ocr_worker import OCRWorker
from src.core.stabilizer import CaptionStabilizer
from src.core.file_manager import FileManager

class LiveCaptionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # 1. Model
        self.file_manager = FileManager()
        self.stabilizer = CaptionStabilizer(
            on_commit_callback=self.on_stabilizer_commit,
            initial_timeout_ms=1500
        )

        # 2. Worker
        self.ocr_worker = OCRWorker()

        # 3. View
        self.main_window = MainWindow()

        # 4. Wiring (Conexões)
        self._connect_signals()

        # 5. Timer para "ticks" do Stabilizer (verificar timeouts)
        self.stabilizer_timer = QTimer()
        self.stabilizer_timer.timeout.connect(self.stabilizer.force_check)
        self.stabilizer_timer.start(100) # Checa a cada 100ms

    def _connect_signals(self):
        # UI -> Worker (Controles)
        self.main_window.start_requested.connect(self.on_start_requested)
        self.main_window.stop_requested.connect(self.ocr_worker.stop)
        self.main_window.region_changed.connect(self.ocr_worker.set_region)
        self.main_window.config_changed.connect(self.on_config_changed)

        # Dependency Handling
        self.main_window.install_requested.connect(self.on_install_requested)

        # Worker -> UI (Erros e Status)
        self.ocr_worker.error_occurred.connect(self.on_worker_error)
        self.ocr_worker.dependency_status.connect(self.on_dependency_status)
        self.ocr_worker.installation_progress.connect(self.main_window.update_status)

        # Worker -> Model (Fluxo de dados)
        self.ocr_worker.text_detected.connect(self.on_text_detected)

    def on_install_requested(self):
        self.main_window.set_installing_state()
        self.ocr_worker.install_dependencies()

    def on_dependency_status(self, is_ready, message):
        if is_ready:
            self.main_window.set_ready_state()
            self.main_window.update_status(message)
        else:
            self.main_window.set_dependencies_missing()
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
            return

        self.ocr_worker.start()

    def on_config_changed(self, config):
        self.update_stabilizer_config(config)
        self.ocr_worker.update_config(config)

    def update_stabilizer_config(self, config):
        self.stabilizer.set_timeout_ms(config['timeout_ms'])
        self.stabilizer.set_auto_timeout(config['auto_timeout'])

    def on_text_detected(self, text):
        self.stabilizer.process_new_text(text)

    def on_stabilizer_commit(self, final_text):
        """Chamado quando uma frase é finalizada e estabilizada."""
        self.file_manager.append_text(final_text)
        self.main_window.append_log(final_text)

    def on_worker_error(self, title, message):
        self.main_window.show_error(title, message)
        self.main_window.toggle_recording() # Para a UI

    def run(self):
        self.main_window.show()
        # Inicia verificação de dependências após UI abrir
        QTimer.singleShot(100, self.ocr_worker.check_dependencies)
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = LiveCaptionApp()
    app.run()
