import os
import datetime
import glob
from src.utils.paths import get_captions_dir

class FileManager:
    MAX_FILES = 5  # 1 atual + 4 históricos
    CURRENT_FILE = "captions_current.txt"
    
    def __init__(self, output_dir=None):
        """
        Gerencia a escrita de legendas em arquivo.
        Mantém apenas 5 arquivos (1 atual + 4 históricos).
        Não cria novo arquivo a cada inicialização - reutiliza o arquivo atual.
        Rola automaticamente para novo arquivo quando atinge 2MB.
        """
        self.output_dir = output_dir or get_captions_dir()
        self.MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Usa arquivo fixo para o atual (não cria novo a cada inicialização)
        self.filepath = os.path.join(self.output_dir, self.CURRENT_FILE)
        
        # Abre o arquivo atual em modo append (cria se não existir)
        self.file = open(self.filepath, "a", encoding="utf-8")
        print(f"Arquivo de legenda aberto: {self.filepath}")
    
    def _get_historical_files(self):
        """Retorna lista de arquivos históricos ordenados por data de modificação (mais antigo primeiro)."""
        pattern = os.path.join(self.output_dir, "captions_hist*.txt")
        files = glob.glob(pattern)
        # Ordena por data de modificação (mais antigo primeiro)
        files.sort(key=lambda f: os.path.getmtime(f))
        return files
    
    def _rotate_file_if_needed(self):
        """Verifica se o arquivo atingiu 2MB e rotaciona se necessário."""
        try:
            if not os.path.exists(self.filepath):
                return
            
            current_size = os.path.getsize(self.filepath)
            if current_size >= self.MAX_FILE_SIZE:
                print(f"Arquivo atingiu {current_size / (1024*1024):.2f}MB. Rotacionando...")
                
                # Fecha o arquivo atual
                self.file.close()
                
                # Obtém arquivos históricos existentes
                historical_files = self._get_historical_files()
                
                # Se já temos 4 históricos, remove o mais antigo
                if len(historical_files) >= (self.MAX_FILES - 1):
                    oldest_file = historical_files[0]
                    try:
                        os.remove(oldest_file)
                        print(f"Arquivo histórico mais antigo removido: {oldest_file}")
                    except Exception as e:
                        print(f"Erro ao remover arquivo histórico: {e}")
                    # Remove da lista para não contar
                    historical_files = historical_files[1:]
                
                # Renomeia o arquivo atual para histórico
                # Encontra o próximo número disponível (1 a 4)
                # Se já temos 4 históricos, o mais antigo foi removido, então temos espaço
                next_hist_num = len(historical_files) + 1
                # Garante que não exceda 4
                if next_hist_num > (self.MAX_FILES - 1):
                    next_hist_num = (self.MAX_FILES - 1)
                
                new_hist_path = os.path.join(self.output_dir, f"captions_hist{next_hist_num}.txt")
                
                try:
                    os.rename(self.filepath, new_hist_path)
                    print(f"Arquivo atual renomeado para histórico: {new_hist_path}")
                except Exception as e:
                    print(f"Erro ao renomear arquivo: {e}")
                
                # Cria novo arquivo atual
                self.filepath = os.path.join(self.output_dir, self.CURRENT_FILE)
                self.file = open(self.filepath, "a", encoding="utf-8")
                print(f"Novo arquivo atual criado: {self.filepath}")
        except Exception as e:
            print(f"Erro ao verificar/rotacionar arquivo: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_all_files(self):
        """Remove todos os arquivos de captions (atual e históricos)."""
        try:
            # Remove arquivo atual se existir
            if os.path.exists(self.filepath):
                self.file.close()
                os.remove(self.filepath)
                print(f"Arquivo atual removido: {self.filepath}")
            
            # Remove todos os arquivos históricos
            historical_files = self._get_historical_files()
            for hist_file in historical_files:
                try:
                    os.remove(hist_file)
                    print(f"Arquivo histórico removido: {hist_file}")
                except Exception as e:
                    print(f"Erro ao remover arquivo histórico {hist_file}: {e}")
            
            # Cria novo arquivo atual vazio
            self.filepath = os.path.join(self.output_dir, self.CURRENT_FILE)
            self.file = open(self.filepath, "a", encoding="utf-8")
            print(f"Novo arquivo atual criado: {self.filepath}")
            return True
        except Exception as e:
            print(f"Erro ao limpar arquivos: {e}")
            import traceback
            traceback.print_exc()
            return False

    def append_text(self, text):
        """
        Escreve uma linha de texto no arquivo com timestamp atual e força o flush.
        """
        if not text:
            return

        # Verifica e rotaciona arquivo antes de escrever
        self._rotate_file_if_needed()

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}\n"

        try:
            self.file.write(line)
            self.file.flush() # Garante escrita imediata no disco
            os.fsync(self.file.fileno()) # Força extra para o SO salvar
            print(f"[FILE_MANAGER] Texto gravado no arquivo: {text[:50]}...")
        except Exception as e:
            print(f"Erro ao escrever no arquivo: {e}")
            import traceback
            traceback.print_exc()

    def export_as_srt(self, output_path=None):
        """
        Exporta as captions do arquivo atual no formato SRT.
        Lê o arquivo atual e converte timestamps para formato SRT.
        Retorna o caminho do arquivo gerado.
        """
        import re
        if output_path is None:
            output_path = os.path.join(self.output_dir, "captions_export.srt")
        
        try:
            current_file = os.path.join(self.output_dir, self.CURRENT_FILE)
            if not os.path.exists(current_file):
                return None
            
            with open(current_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(output_path, 'w', encoding='utf-8') as out:
                index = 1
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse timestamp e texto: [HH:MM:SS] texto
                    match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*(.*)', line)
                    if match:
                        timestamp = match.group(1)
                        text = match.group(2)
                        
                        # SRT precisa de start --> end
                        start_time = f"{timestamp},000"
                        # End time: +3 segundos (estimativa)
                        h, m, s = map(int, timestamp.split(':'))
                        total_secs = h * 3600 + m * 60 + s + 3
                        eh, em, es = total_secs // 3600, (total_secs % 3600) // 60, total_secs % 60
                        end_time = f"{eh:02d}:{em:02d}:{es:02d},000"
                        
                        out.write(f"{index}\n")
                        out.write(f"{start_time} --> {end_time}\n")
                        out.write(f"{text}\n\n")
                        index += 1
            
            return output_path
        except Exception as e:
            print(f"Erro ao exportar SRT: {e}")
            return None

    def export_as_vtt(self, output_path=None):
        """
        Exporta as captions do arquivo atual no formato WebVTT.
        """
        import re
        if output_path is None:
            output_path = os.path.join(self.output_dir, "captions_export.vtt")
        
        try:
            current_file = os.path.join(self.output_dir, self.CURRENT_FILE)
            if not os.path.exists(current_file):
                return None
            
            with open(current_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write("WEBVTT\n\n")
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*(.*)', line)
                    if match:
                        timestamp = match.group(1)
                        text = match.group(2)
                        
                        start_time = f"{timestamp}.000"
                        h, m, s = map(int, timestamp.split(':'))
                        total_secs = h * 3600 + m * 60 + s + 3
                        eh, em, es = total_secs // 3600, (total_secs % 3600) // 60, total_secs % 60
                        end_time = f"{eh:02d}:{em:02d}:{es:02d}.000"
                        
                        out.write(f"{start_time} --> {end_time}\n")
                        out.write(f"{text}\n\n")
            
            return output_path
        except Exception as e:
            print(f"Erro ao exportar VTT: {e}")
            return None

    def close(self):
        """Fecha o arquivo com segurança."""
        if self.file:
            self.file.close()
