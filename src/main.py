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

        # Worker -> UI (Erros)
        self.ocr_worker.error_occurred.connect(self.on_worker_error)

        # Worker -> Model (Fluxo de dados)
        self.ocr_worker.text_detected.connect(self.on_text_detected)

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
        # Passa texto cru para o estabilizador
        # Loga texto cru (opcional, pode poluir muito. Melhor logar só o final)
        # self.main_window.status_bar.showMessage(f"Lendo: {text[:30]}...")
        self.stabilizer.process_new_text(text)

    def on_stabilizer_commit(self, final_text):
        """Chamado quando uma frase é finalizada e estabilizada."""
        # 1. Salvar em arquivo
        self.file_manager.append_text(final_text)

        # 2. Atualizar UI
        self.main_window.append_log(final_text)

        # Se o timeout mudou dinamicamente, atualiza a UI para refletir (visual feedback)
        # Cuidado para não gerar loop de sinais.
        # Idealmente a UI apenas mostraria, mas o SpinBox controla o valor.
        # Se for auto, o valor do SpinBox poderia ser desabilitado ou atualizado.
        # Vamos deixar simples por enquanto: Se auto está on, o valor interno muda,
        # o spinbox fica cinza (já implementado na UI).

    def on_worker_error(self, title, message):
        self.main_window.show_error(title, message)
        self.main_window.toggle_recording() # Para a UI

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = LiveCaptionApp()
    app.run()
