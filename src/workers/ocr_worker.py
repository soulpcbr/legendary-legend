import time
import sys
import numpy as np
import pytesseract
import mss
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from src.utils.image_processing import process_image_for_ocr

class OCRWorker(QThread):
    text_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str) # Título, Mensagem

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._mutex = QMutex()

        # Configuração padrão
        self.region = None # {'top': y, 'left': x, 'width': w, 'height': h}
        self.invert_colors = False

        # MSS instance
        self.sct = mss.mss()

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

    def run(self):
        self._is_running = True

        # Validação inicial do Tesseract
        try:
            # Tenta pegar versão apenas para checar existência
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            self.error_occurred.emit("Tesseract Não Encontrado",
                "O binário do Tesseract não foi encontrado no PATH.\n"
                "Por favor, instale-o e adicione ao PATH do sistema conforme o README.")
            return
        except Exception as e:
            self.error_occurred.emit("Erro Inicialização", f"Falha ao iniciar Tesseract: {e}")
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
                # mss retorna um raw bytes, precisamos converter para numpy
                sct_img = self.sct.grab(region)
                img = np.array(sct_img)

                # 2. Image Processing
                processed_img = process_image_for_ocr(img, invert=invert)

                # 3. OCR
                # psm 6: Assume a single uniform block of text. Bom para legendas.
                # psm 7: Treat the image as a single text line.
                # Legendas podem ter 2 linhas. PSM 6 ou 3 (default) é seguro.
                # lang='por+eng' se quiser suporte a ambos, mas default 'eng' costuma funcionar bem.
                # Vamos deixar default por enquanto, ou configurar 'eng'.
                text = pytesseract.image_to_string(processed_img, config='--psm 6')

                self.text_detected.emit(text)

            except Exception as e:
                print(f"Erro no loop OCR: {e}")
                # Não para o loop por erro transiente de captura, mas loga

            # Controle de taxa de quadros (não saturar CPU)
            # Se o OCR for muito rápido (< 100ms), espera um pouco.
            elapsed = time.time() - start_time
            if elapsed < 0.2:
                time.sleep(0.2 - elapsed)
