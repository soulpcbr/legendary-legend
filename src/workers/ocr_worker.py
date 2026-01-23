import time
import sys
import numpy as np
import mss
import threading
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from src.utils.image_processing import process_image_for_ocr

class OCRWorker(QThread):
    text_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str) # Título, Mensagem

    # Sinais de Dependência
    dependency_status = pyqtSignal(bool, str) # is_ready, message
    installation_progress = pyqtSignal(str) # Status message

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._mutex = QMutex()

        # Configuração padrão
        self.region = None # {'top': y, 'left': x, 'width': w, 'height': h}
        self.invert_colors = False

        # MSS instance
        self.sct = mss.mss()

        # EasyOCR Reader
        self.reader = None
        self.gpu = False # Forçar CPU para compatibilidade
        self.languages = ['pt', 'en']

    def set_region(self, x, y, w, h):
        with QMutexLocker(self._mutex):
            self.region = {'top': y, 'left': x, 'width': w, 'height': h}

    def update_config(self, config):
        """
        Atualiza configurações dinâmicas.
        config: dict com chaves como 'invert_colors'
        """
        with QMutexLocker(self._mutex):
            self.invert_colors = config.get('invert_colors', False)

    def stop(self):
        self._is_running = False
        self.wait()

    def check_dependencies(self):
        """Verifica se os modelos existem carregando o Reader sem download."""
        thread = threading.Thread(target=self._check_task)
        thread.daemon = True
        thread.start()

    def _check_task(self):
        try:
            import easyocr
            # Tenta carregar sem download. Se falhar, é porque não tem os modelos.
            # verbose=False para menos logs
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu, download_enabled=False, verbose=False)
            self.dependency_status.emit(True, "Modelos carregados.")
        except Exception as e:
            # Provavelmente modelos faltando
            print(f"Check failed: {e}")
            self.dependency_status.emit(False, "Modelos de OCR não encontrados.")

    def install_dependencies(self):
        """Baixa os modelos."""
        self.installation_progress.emit("Iniciando download dos modelos (pode demorar)...")
        thread = threading.Thread(target=self._install_task)
        thread.daemon = True
        thread.start()

    def _install_task(self):
        try:
            import easyocr
            # Com download_enabled=True, ele baixa se faltar
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu, download_enabled=True, verbose=True)
            self.dependency_status.emit(True, "Modelos instalados com sucesso!")
        except Exception as e:
            self.error_occurred.emit("Erro na Instalação", f"Falha ao baixar modelos: {str(e)}")
            self.dependency_status.emit(False, f"Erro: {str(e)}")

    def run(self):
        self._is_running = True

        if not self.reader:
            self.error_occurred.emit("Erro Interno", "Reader OCR não inicializado.")
            return

        while self._is_running:
            start_time = time.time()

            # Captura Região com Thread Safety na leitura da config
            with QMutexLocker(self._mutex):
                region = self.region
                invert = self.invert_colors

            if not region:
                time.sleep(0.1)
                continue

            try:
                # 1. Screen Capture (mss)
                sct_img = self.sct.grab(region)
                img = np.array(sct_img)

                # 2. Image Processing
                # Converte para grayscale se necessário e aplica filtros
                processed_img = process_image_for_ocr(img, invert=invert)

                # 3. OCR com EasyOCR
                # detail=0 retorna apenas lista de textos
                # paragraph=True tenta combinar linhas
                results = self.reader.readtext(processed_img, detail=0, paragraph=True)

                # Junta resultados em uma string única
                text = " ".join(results).strip()

                if text:
                    self.text_detected.emit(text)

            except Exception as e:
                print(f"Erro no loop OCR: {e}")

            # Controle de taxa de quadros
            # EasyOCR é mais pesado que Tesseract, então talvez demore mais que 200ms
            elapsed = time.time() - start_time
            if elapsed < 0.2:
                time.sleep(0.2 - elapsed)
