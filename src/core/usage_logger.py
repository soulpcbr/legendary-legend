import os
import datetime
import json
from src.utils.paths import get_logs_dir

class UsageLogger:
    """
    Sistema de log de uso detalhado para registrar:
    - Acontecimentos e decisões
    - Funcionamento das configurações
    - Autoajustes e suas razões
    - Mudanças de parâmetros
    """
    
    def __init__(self, log_dir=None, max_file_size=10 * 1024 * 1024):  # 10MB
        """
        :param log_dir: Diretório onde os logs serão salvos (padrão: auto-detectado via paths.py)
        :param max_file_size: Tamanho máximo do arquivo em bytes (padrão: 10MB)
        """
        self.log_dir = log_dir or get_logs_dir()
        self.MAX_FILE_SIZE = max_file_size
        self.MAX_LOG_FILES = 5 # Mantém no máximo 5 arquivos de 10MB (= 50MB top teto)
        self.file_counter = 1
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.filepath = self._create_new_filepath()
        self.file = open(self.filepath, "a", encoding="utf-8")
        self._log("SYSTEM", "UsageLogger inicializado", {"max_file_size_mb": self.MAX_FILE_SIZE / (1024*1024)})
    
    def _create_new_filepath(self):
        """Cria um novo caminho de arquivo rotativo sempre reaproveitando de 1 a MAX_LOG_FILES."""
        # Se ultrapassar o num máximo de arquivos, recicla a numeração
        if self.file_counter > self.MAX_LOG_FILES:
            self.file_counter = 1
            
        file_path = os.path.join(self.log_dir, f"usage_history_part{self.file_counter}.log")
        
        # Se o arquivo já existir do ciclo passado, o modo 'w' na rotação vai limpá-lo
        return file_path
    
    def _rotate_file_if_needed(self):
        """Verifica se o arquivo atual atingiu o limite e rotaciona destruindo os ciclos mais velhos."""
        try:
            current_size = os.path.getsize(self.filepath)
            if current_size >= self.MAX_FILE_SIZE:
                self._log("SYSTEM", "Rotacionando arquivo de log", {"size_mb": current_size / (1024*1024)})
                self.file.close()
                self.file_counter += 1
                
                self.filepath = self._create_new_filepath()
                # Modo 'w' trunca (deleta o conteúdo velho) ao ciclar por cima
                self.file = open(self.filepath, "w", encoding="utf-8")
                self._log("SYSTEM", "Novo arquivo de log criado (ciclo truncado)", {"filepath": self.filepath})
        except Exception as e:
            print(f"Erro ao verificar tamanho do arquivo de log: {e}")
    
    def _log(self, category, message, data=None):
        """Método interno para escrever no log."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_entry = {
                "timestamp": timestamp,
                "category": category,
                "message": message,
                "data": data or {}
            }
            
            # Escreve em formato JSON (uma linha por entrada - NDJSON)
            self.file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            self.file.flush()
            os.fsync(self.file.fileno())
            
            # Verifica e rotaciona *após* escrever para garantir que o _log interno 
            # de rotação no 'w' do próximo arquivo de ciclo seja o primeiro da tela
            self._rotate_file_if_needed()
        except Exception as e:
            print(f"Erro ao escrever no log de uso: {e}")
    
    def log_config_change(self, config_name, old_value, new_value, reason=None):
        """Registra mudança de configuração."""
        self._log("CONFIG", f"Configuração '{config_name}' alterada", {
            "config_name": config_name,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason or "Manual"
        })
    
    def log_auto_adjust(self, parameter, old_value, new_value, reason, stats=None):
        """Registra autoajuste de parâmetro."""
        self._log("AUTO_ADJUST", f"Autoajuste: {parameter}", {
            "parameter": parameter,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "statistics": stats or {}
        })
    
    def log_decision(self, decision_type, decision, context=None):
        """Registra uma decisão tomada pelo sistema."""
        self._log("DECISION", f"Decisão: {decision_type}", {
            "decision_type": decision_type,
            "decision": decision,
            "context": context or {}
        })
    
    def log_event(self, event_type, description, details=None):
        """Registra um evento do sistema."""
        self._log("EVENT", f"Evento: {event_type}", {
            "event_type": event_type,
            "description": description,
            "details": details or {}
        })
    
    def log_text_processing(self, action, text, similarity=None, decision=None):
        """Registra processamento de texto."""
        data = {
            "action": action,
            "text_length": len(text) if text else 0,
            "text_preview": text[:50] + "..." if text and len(text) > 50 else text
        }
        if similarity is not None:
            data["similarity"] = similarity
        if decision:
            data["decision"] = decision
        self._log("TEXT_PROCESSING", f"Processamento: {action}", data)
    
    def close(self):
        """Fecha o arquivo com segurança."""
        if self.file:
            self._log("SYSTEM", "UsageLogger finalizado")
            self.file.close()
