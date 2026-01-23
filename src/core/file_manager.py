import os
import datetime

class FileManager:
    def __init__(self, output_dir="captions"):
        """
        Gerencia a escrita de legendas em arquivo.
        Cria um novo arquivo timestamped na inicialização.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filepath = os.path.join(self.output_dir, f"captions_{timestamp}.txt")
        self.file = open(self.filepath, "a", encoding="utf-8")
        print(f"Arquivo de legenda criado: {self.filepath}")

    def append_text(self, text):
        """
        Escreve uma linha de texto no arquivo com timestamp atual e força o flush.
        """
        if not text:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}\n"

        try:
            self.file.write(line)
            self.file.flush() # Garante escrita imediata no disco
            os.fsync(self.file.fileno()) # Força extra para o SO salvar
        except Exception as e:
            print(f"Erro ao escrever no arquivo: {e}")

    def close(self):
        """Fecha o arquivo com segurança."""
        if self.file:
            self.file.close()
