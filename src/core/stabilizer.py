import difflib
import time
import statistics
from collections import deque

class CaptionStabilizer:
    def __init__(self, on_commit_callback, initial_timeout_ms=1500, usage_logger=None):
        """
        :param on_commit_callback: Função para chamar quando uma frase é finalizada (str).
        :param initial_timeout_ms: Tempo inicial em ms para considerar silêncio.
        :param usage_logger: Instância de UsageLogger para registrar eventos (opcional).
        """
        self.on_commit = on_commit_callback
        self.usage_logger = usage_logger
        self.current_buffer = ""
        self.last_update_time = time.time()

        # Configurações de Timeout
        self.silence_timeout_ms = initial_timeout_ms
        self.is_auto_timeout = False
        self.min_timeout_ms = 1000
        self.max_timeout_ms = 5000

        # Parâmetros de Jitter (básicos)
        self.similarity_threshold = 0.6
        self.min_update_interval = 50  # ms
        self.auto_recalc_interval = 30  # segundos

        # Parâmetros Avançados de Jitter (novos)
        self.max_similarity_threshold = 0.9  # Limite máximo ajustável
        self.min_similarity_threshold = 0.3  # Limite mínimo ajustável
        self.similarity_adjust_step = 0.05  # Passo de ajuste (ajustável)
        self.interval_adjust_step = 5  # Passo de ajuste de intervalo (ajustável)
        self.jitter_detection_threshold = 50  # Threshold para detectar jitter alto (ajustável)
        self.stability_detection_threshold = 20  # Threshold para detectar estabilidade (ajustável)
        self.repetition_detection_window = 5  # Janela para detectar repetições (ajustável)
        
        # Controle de Repetição (melhorado)
        self.last_committed_texts = deque(maxlen=20)  # Últimas 20 frases commitadas (aumentado)
        self.recent_texts = deque(maxlen=10)  # Textos recentes processados (não commitados ainda)
        self.repetition_threshold = 0.8  # Similaridade para considerar repetição
        self.consecutive_repetition_count = 0  # Contador de repetições consecutivas
        self.last_text_hash = None  # Hash do último texto para detecção rápida de duplicatas exatas

        # Ajuste Inteligente
        self.is_auto_smart_adjust = False
        self.auto_adjust_callback = None  # Callback para notificar UI sobre ajustes
        self.debug_log_callback = None  # Callback para enviar logs de debug

        # Para estatísticas dinâmicas
        self.update_deltas = deque(maxlen=50) # Guarda os últimos 50 intervalos entre updates da MESMA frase
        self.similarity_history = deque(maxlen=20)  # Histórico de similaridades
        self.last_recalc_time = time.time()
        
        # Contadores para análise
        self.commit_count = 0
        self.repetition_count = 0
        self.same_phrase_count = 0
        self.new_phrase_count = 0
        self.exact_duplicate_count = 0  # Contador de duplicatas exatas

    def set_usage_logger(self, logger):
        """Define o logger de uso."""
        self.usage_logger = logger

    def set_auto_adjust_callback(self, callback):
        """Define callback para notificar UI sobre autoajustes."""
        self.auto_adjust_callback = callback
    
    def set_debug_log_callback(self, callback):
        """Define callback para enviar logs de debug."""
        self.debug_log_callback = callback

    def set_timeout_ms(self, ms):
        old = self.silence_timeout_ms
        self.silence_timeout_ms = ms
        if self.usage_logger:
            self.usage_logger.log_config_change("timeout_ms", old, ms, "Manual")

    def set_auto_timeout(self, enabled):
        old = self.is_auto_timeout
        self.is_auto_timeout = enabled
        if self.usage_logger:
            self.usage_logger.log_config_change("auto_timeout", old, enabled, "Manual")

    def set_similarity_threshold(self, threshold):
        """
        Define o threshold de similaridade (0.3 - 0.9).
        Valores mais altos = menos sensível a mudanças (mais estável).
        Valores mais baixos = mais sensível a mudanças (mais reativo).
        """
        old = self.similarity_threshold
        self.similarity_threshold = max(self.min_similarity_threshold, min(self.max_similarity_threshold, threshold))
        if self.usage_logger and old != self.similarity_threshold:
            self.usage_logger.log_config_change("similarity_threshold", old, self.similarity_threshold, "Manual")

    def set_min_update_interval(self, interval_ms):
        """
        Define o intervalo mínimo em ms entre atualizações.
        Atualizações mais rápidas que isso são consideradas ruído.
        """
        old = self.min_update_interval
        self.min_update_interval = max(10, min(200, interval_ms))
        if self.usage_logger and old != self.min_update_interval:
            self.usage_logger.log_config_change("min_update_interval", old, self.min_update_interval, "Manual")

    def set_auto_recalc_interval(self, interval_s):
        """
        Define o intervalo em segundos para recalcular parâmetros automaticamente.
        """
        old = self.auto_recalc_interval
        self.auto_recalc_interval = max(5, min(60, interval_s))
        if self.usage_logger and old != self.auto_recalc_interval:
            self.usage_logger.log_config_change("auto_recalc_interval", old, self.auto_recalc_interval, "Manual")

    def set_auto_smart_adjust(self, enabled):
        """
        Ativa/desativa o ajuste automático inteligente.
        Quando ativado, o sistema ajusta similarity_threshold e min_update_interval
        baseado na qualidade das detecções.
        """
        old = self.is_auto_smart_adjust
        self.is_auto_smart_adjust = enabled
        if self.usage_logger:
            self.usage_logger.log_config_change("auto_smart_adjust", old, enabled, "Manual")

    def set_jitter_parameters(self, params):
        """
        Define parâmetros avançados de jitter de uma vez.
        params: dict com chaves opcionais:
        - max_similarity_threshold
        - min_similarity_threshold
        - similarity_adjust_step
        - interval_adjust_step
        - jitter_detection_threshold
        - stability_detection_threshold
        - repetition_detection_window
        - repetition_threshold
        """
        if 'max_similarity_threshold' in params:
            self.max_similarity_threshold = max(0.5, min(0.95, params['max_similarity_threshold']))
        if 'min_similarity_threshold' in params:
            self.min_similarity_threshold = max(0.2, min(0.7, params['min_similarity_threshold']))
        if 'similarity_adjust_step' in params:
            self.similarity_adjust_step = max(0.01, min(0.2, params['similarity_adjust_step']))
        if 'interval_adjust_step' in params:
            self.interval_adjust_step = max(1, min(20, params['interval_adjust_step']))
        if 'jitter_detection_threshold' in params:
            self.jitter_detection_threshold = max(20, min(200, params['jitter_detection_threshold']))
        if 'stability_detection_threshold' in params:
            self.stability_detection_threshold = max(5, min(50, params['stability_detection_threshold']))
        if 'repetition_detection_window' in params:
            self.repetition_detection_window = max(3, min(20, params['repetition_detection_window']))
        if 'repetition_threshold' in params:
            self.repetition_threshold = max(0.5, min(0.95, params['repetition_threshold']))

    def process_new_text(self, raw_text):
        """
        Processa o texto cru vindo do OCR.
        Deve ser chamado frequentemente pelo loop principal.
        """
        now = time.time()

        # Remove espaços extras e normaliza
        raw_text = raw_text.strip()
        
        # Se texto vazio, apenas checa timeout
        if not raw_text:
            self._check_timeout(now)
            return

        # Hash simples para detecção rápida de duplicatas exatas
        text_hash = hash(raw_text.lower())
        
        # Detecção de duplicata exata (mesmo texto que acabou de ser processado)
        if text_hash == self.last_text_hash:
            self.exact_duplicate_count += 1
            if self.debug_log_callback:
                self.debug_log_callback(f"[DUPLICATA] Texto exato ignorado: {raw_text[:50]}...")
            if self.usage_logger:
                self.usage_logger.log_decision("EXACT_DUPLICATE_DETECTED", "Duplicata exata ignorada", {
                    "text_preview": raw_text[:50],
                    "duplicate_count": self.exact_duplicate_count
                })
            return  # Ignora duplicata exata
        
        self.last_text_hash = text_hash

        # Verifica se o texto é expansão/correção do buffer atual ANTES de checar repetição.
        # Isso evita falsos positivos: "Ola" → "Ola tudo" não é repetição, é construção.
        is_expanding_buffer = False
        if self.current_buffer:
            # Texto contém o buffer atual (expansão direta)
            if self.current_buffer in raw_text:
                is_expanding_buffer = True
            else:
                # Verifica similaridade com buffer atual
                matcher = difflib.SequenceMatcher(None, self.current_buffer, raw_text)
                buffer_similarity = matcher.ratio()
                if buffer_similarity > self.similarity_threshold:
                    is_expanding_buffer = True

        # Verifica repetição APENAS se NÃO for expansão do buffer atual.
        # Se for expansão, é a mesma frase sendo construída, não repetição.
        if not is_expanding_buffer:
            repetition_info = self._is_repetition(raw_text)
            if repetition_info['is_repetition']:
                self.repetition_count += 1
                self.consecutive_repetition_count += 1
                
                similarity = repetition_info.get('similarity', 0)
                matched = repetition_info.get('matched_text', '')[:30]
                if self.debug_log_callback:
                    self.debug_log_callback(f"[REPETIÇÃO] Ignorado (sim: {similarity:.2f}, consec: {self.consecutive_repetition_count}): {raw_text[:40]}...")
                
                if self.usage_logger:
                    self.usage_logger.log_decision("REPETITION_DETECTED", "Texto repetido ignorado", {
                        "text_preview": raw_text[:50],
                        "repetition_count": self.repetition_count,
                        "consecutive_repetitions": self.consecutive_repetition_count,
                        "similarity": similarity,
                        "matched_text": repetition_info.get('matched_text', '')[:50]
                    })
                
                # Se muitas repetições consecutivas, força ajuste agressivo
                if self.consecutive_repetition_count >= 3 and self.is_auto_smart_adjust:
                    if self.debug_log_callback:
                        self.debug_log_callback(f"[ALERTA] {self.consecutive_repetition_count} repetições consecutivas! Ajuste agressivo ativado.")
                    self._aggressive_adjust_for_repetitions()
                
                return  # Ignora texto repetido
        
        # Reset contador de repetições consecutivas se não for repetição
        self.consecutive_repetition_count = 0

        # Similaridade
        matcher = difflib.SequenceMatcher(None, self.current_buffer, raw_text)
        similarity = matcher.ratio()
        self.similarity_history.append(similarity)

        # Lógica de decisão
        is_same_phrase = similarity > self.similarity_threshold

        # Caso especial: Buffer atual está contido no novo texto (expansão direta)
        if not is_same_phrase and self.current_buffer and self.current_buffer in raw_text:
             is_same_phrase = True

        # Adiciona aos textos recentes para detecção de repetição
        self.recent_texts.append(raw_text)
        
        if is_same_phrase:
            # É a mesma frase sendo corrigida/expandida
            self.same_phrase_count += 1
            time_since_last = (now - self.last_update_time) * 1000 # ms
            if time_since_last > self.min_update_interval: # Ignora updates instantâneos demais (ruído)
                self.update_deltas.append(time_since_last)

            # Atualiza buffer
            self.current_buffer = raw_text
            self.last_update_time = now
            
            if self.usage_logger:
                self.usage_logger.log_text_processing("UPDATE_SAME_PHRASE", raw_text, similarity=similarity, 
                                                     decision=f"Atualização da mesma frase (similaridade: {similarity:.2f})")
        else:
            # Frase mudou completamente
            self.new_phrase_count += 1
            self._commit_buffer()
            self.current_buffer = raw_text
            self.last_update_time = now
            
            if self.usage_logger:
                self.usage_logger.log_text_processing("NEW_PHRASE", raw_text, similarity=similarity,
                                                     decision=f"Nova frase detectada (similaridade: {similarity:.2f})")

        # Checa e executa lógica dinâmica periodicamente
        if self.is_auto_timeout or self.is_auto_smart_adjust:
            self._recalculate_if_needed(now)

    def _is_repetition(self, text, check_recent_texts=True):
        """
        Verifica se o texto é uma repetição recente.
        Retorna dict com informações sobre a repetição.
        
        :param check_recent_texts: Se False, não verifica recent_texts (usado em _commit_buffer)
        """
        if not text:
            return {'is_repetition': False}
        
        text_lower = text.lower().strip()
        
        # Verifica duplicata exata primeiro (mais rápido)
        if len(self.last_committed_texts) > 0:
            # Verifica nas últimas frases commitadas
            for committed_text in list(self.last_committed_texts)[-self.repetition_detection_window:]:
                if committed_text.lower().strip() == text_lower:
                    return {
                        'is_repetition': True,
                        'similarity': 1.0,
                        'matched_text': committed_text,
                        'type': 'exact'
                    }
        
        # Verifica similaridade com as últimas frases commitadas
        best_similarity = 0
        best_match = None
        
        for committed_text in list(self.last_committed_texts)[-self.repetition_detection_window:]:
            matcher = difflib.SequenceMatcher(None, committed_text.lower(), text_lower)
            similarity = matcher.ratio()
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = committed_text
        
        # Verifica também nos textos recentes (não commitados ainda)
        # IMPORTANTE: Não verifica recent_texts quando chamado de _commit_buffer,
        # pois o texto atual pode estar em recent_texts e causaria bloqueio incorreto
        if check_recent_texts:
            for recent_text in list(self.recent_texts):
                matcher = difflib.SequenceMatcher(None, recent_text.lower(), text_lower)
                similarity = matcher.ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = recent_text
        
        # Threshold adaptativo: mais agressivo se há muitas repetições recentes
        adaptive_threshold = self.repetition_threshold
        if self.repetition_count > 5:
            adaptive_threshold = max(0.7, self.repetition_threshold - 0.1)  # Reduz threshold se há muitas repetições
        
        is_repetition = best_similarity >= adaptive_threshold
        
        if is_repetition:
            return {
                'is_repetition': True,
                'similarity': best_similarity,
                'matched_text': best_match or '',
                'type': 'similar',
                'threshold_used': adaptive_threshold
            }
        
        return {'is_repetition': False}

    def _check_timeout(self, now):
        """Verifica se excedeu o tempo de silêncio."""
        if not self.current_buffer:
            return

        elapsed_ms = (now - self.last_update_time) * 1000
        
        if elapsed_ms > self.silence_timeout_ms:
            if self.debug_log_callback:
                self.debug_log_callback(f"[TIMEOUT] Silêncio detectado ({elapsed_ms:.0f}ms > {self.silence_timeout_ms}ms), commitando frase")
            if self.usage_logger:
                self.usage_logger.log_decision("TIMEOUT_COMMIT", "Timeout de silêncio atingido", {
                    "elapsed_ms": elapsed_ms,
                    "timeout_ms": self.silence_timeout_ms,
                    "buffer_length": len(self.current_buffer)
                })
            
            self._commit_buffer()

    def _commit_buffer(self):
        """Salva a frase atual e limpa o buffer."""
        if self.current_buffer:
            # Verifica se não é repetição antes de commitar
            # IMPORTANTE: Não verifica recent_texts aqui, pois o texto atual pode estar lá
            # e causaria bloqueio incorreto. Só verifica last_committed_texts.
            repetition_info = self._is_repetition(self.current_buffer, check_recent_texts=False)
            
            if not repetition_info['is_repetition']:
                # Log de debug antes de commitar
                if self.debug_log_callback:
                    self.debug_log_callback(f"[COMMIT] Commitando frase ({self.commit_count + 1}): {self.current_buffer[:50]}...")
                
                self.on_commit(self.current_buffer)
                self.last_committed_texts.append(self.current_buffer)
                self.commit_count += 1
                # Limpa textos recentes após commit bem-sucedido
                self.recent_texts.clear()
                
                if self.usage_logger:
                    self.usage_logger.log_event("TEXT_COMMITTED", "Frase commitada", {
                        "text_length": len(self.current_buffer),
                        "total_commits": self.commit_count,
                        "repetitions_blocked": self.repetition_count
                    })
            else:
                self.repetition_count += 1
                similarity = repetition_info.get('similarity', 0)
                if self.debug_log_callback:
                    self.debug_log_callback(f"[PREVENÇÃO] Commit de repetição bloqueado (sim: {similarity:.2f}): {self.current_buffer[:40]}...")
                if self.usage_logger:
                    self.usage_logger.log_decision("REPETITION_PREVENTED", "Commit de repetição prevenido", {
                        "text_preview": self.current_buffer[:50],
                        "similarity": similarity,
                        "matched_text": repetition_info.get('matched_text', '')[:50]
                    })
            self.current_buffer = ""

    def _recalculate_if_needed(self, now):
        """
        Recalcula parâmetros automaticamente se necessário.
        Inclui auto-timeout e ajuste inteligente.
        """
        if (now - self.last_recalc_time) < self.auto_recalc_interval:
            return

        adjustments_made = []

        # Recálculo de timeout (existente)
        if self.is_auto_timeout and len(self.update_deltas) > 5:
            avg = statistics.mean(self.update_deltas)
            try:
                stdev = statistics.stdev(self.update_deltas)
            except:
                stdev = 0

            # Novo timeout sugerido: Média + 3 sigmas + margem
            new_timeout = avg + (3 * stdev) + 500
            new_timeout = max(self.min_timeout_ms, min(new_timeout, self.max_timeout_ms))

            if abs(new_timeout - self.silence_timeout_ms) > 50:  # Só ajusta se mudança significativa
                old_timeout = self.silence_timeout_ms
                self.silence_timeout_ms = int(new_timeout)
                reason = f"Baseado em estatísticas (avg: {avg:.1f}ms, stdev: {stdev:.1f}ms, {len(self.update_deltas)} amostras)"
                adjustments_made.append(("timeout_ms", old_timeout, self.silence_timeout_ms, reason))
                
                if self.usage_logger:
                    self.usage_logger.log_auto_adjust("timeout_ms", old_timeout, self.silence_timeout_ms,
                                                     reason,
                                                     {"avg": avg, "stdev": stdev, "update_count": len(self.update_deltas)})

        # Ajuste Inteligente (melhorado)
        if self.is_auto_smart_adjust and len(self.update_deltas) > 10:
            adjustments = self._smart_adjust_parameters()
            adjustments_made.extend(adjustments)

        # Notifica UI sobre ajustes
        if adjustments_made and self.auto_adjust_callback:
            for adjustment in adjustments_made:
                if len(adjustment) == 4:  # (param, old_val, new_val, reason)
                    param, old_val, new_val, reason = adjustment
                    self.auto_adjust_callback(param, old_val, new_val, reason)
                else:  # Compatibilidade com formato antigo
                    param, old_val, new_val = adjustment
                    self.auto_adjust_callback(param, old_val, new_val)

        self.last_recalc_time = now

    def _smart_adjust_parameters(self):
        """
        Ajusta automaticamente parâmetros baseado na qualidade das detecções recentes.
        Retorna lista de ajustes feitos: [(param_name, old_value, new_value, reason), ...]
        """
        if len(self.update_deltas) < 10:
            return []

        adjustments = []
        deltas_list = list(self.update_deltas)
        avg = statistics.mean(deltas_list)
        stdev = statistics.stdev(deltas_list) if len(deltas_list) > 1 else 0

        # Análise de similaridade média
        avg_similarity = statistics.mean(self.similarity_history) if self.similarity_history else 0.6
        
        # Razão de repetições (incluindo duplicatas exatas)
        total_processed = self.same_phrase_count + self.new_phrase_count + self.repetition_count + self.exact_duplicate_count
        total_repetitions = self.repetition_count + self.exact_duplicate_count
        repetition_rate = total_repetitions / total_processed if total_processed > 0 else 0

        reason_parts = []
        
        # Ajuste baseado em variação (jitter)
        if stdev > self.jitter_detection_threshold:  # Alta variação = muito jitter
            old_threshold = self.similarity_threshold
            old_interval = self.min_update_interval
            
            self.similarity_threshold = min(self.max_similarity_threshold, 
                                          self.similarity_threshold + self.similarity_adjust_step)
            self.min_update_interval = min(100, self.min_update_interval + self.interval_adjust_step)
            
            reason = f"Alta variação detectada (stdev: {stdev:.1f}ms, avg: {avg:.1f}ms)"
            
            if old_threshold != self.similarity_threshold:
                adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
                reason_parts.append(f"Alta variação (stdev: {stdev:.1f}ms)")
            
            if old_interval != self.min_update_interval:
                adjustments.append(("min_update_interval", old_interval, self.min_update_interval, reason))
                reason_parts.append(f"Alta variação (stdev: {stdev:.1f}ms)")
                
        elif stdev < self.stability_detection_threshold:  # Baixa variação = muito estável
            old_threshold = self.similarity_threshold
            old_interval = self.min_update_interval
            
            self.similarity_threshold = max(self.min_similarity_threshold, 
                                          self.similarity_threshold - self.similarity_adjust_step)
            self.min_update_interval = max(30, self.min_update_interval - self.interval_adjust_step)
            
            reason = f"Baixa variação detectada (stdev: {stdev:.1f}ms, avg: {avg:.1f}ms)"
            
            if old_threshold != self.similarity_threshold:
                adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
                reason_parts.append(f"Baixa variação (stdev: {stdev:.1f}ms)")
            
            if old_interval != self.min_update_interval:
                adjustments.append(("min_update_interval", old_interval, self.min_update_interval, reason))
                reason_parts.append(f"Baixa variação (stdev: {stdev:.1f}ms)")

        # Ajuste baseado em taxa de repetição (mais agressivo)
        if repetition_rate > 0.15:  # Mais de 15% de repetições (reduzido de 30%)
            old_threshold = self.similarity_threshold
            old_interval = self.min_update_interval
            
            # Ajuste mais agressivo baseado na taxa de repetição
            if repetition_rate > 0.4:  # Mais de 40% = muito agressivo
                threshold_increase = self.similarity_adjust_step * 3
                interval_increase = self.interval_adjust_step * 2
                severity = "muito alta"
            elif repetition_rate > 0.25:  # Mais de 25% = agressivo
                threshold_increase = self.similarity_adjust_step * 2
                interval_increase = self.interval_adjust_step
                severity = "alta"
            else:  # 15-25% = moderado
                threshold_increase = self.similarity_adjust_step * 1.5
                interval_increase = self.interval_adjust_step
                severity = "moderada"
            
            self.similarity_threshold = min(self.max_similarity_threshold,
                                          self.similarity_threshold + threshold_increase)
            self.min_update_interval = min(150, self.min_update_interval + interval_increase)
            
            reason = f"Taxa de repetição {severity} ({repetition_rate*100:.1f}%, {total_repetitions} repetições de {total_processed} processados)"
            
            if old_threshold != self.similarity_threshold:
                adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
                reason_parts.append(f"Alta taxa de repetição ({repetition_rate*100:.1f}%)")
            
            if old_interval != self.min_update_interval:
                adjustments.append(("min_update_interval", old_interval, self.min_update_interval, reason))
                reason_parts.append(f"Alta taxa de repetição ({repetition_rate*100:.1f}%)")
        
        # Ajuste baseado em repetições consecutivas
        if self.consecutive_repetition_count >= 2:
            old_threshold = self.similarity_threshold
            old_interval = self.min_update_interval
            
            # Ajuste muito agressivo para repetições consecutivas
            self.similarity_threshold = min(self.max_similarity_threshold,
                                          self.similarity_threshold + self.similarity_adjust_step * 2)
            self.min_update_interval = min(120, self.min_update_interval + self.interval_adjust_step * 2)
            
            reason = f"Repetições consecutivas detectadas ({self.consecutive_repetition_count} consecutivas, {self.repetition_count} total)"
            
            if old_threshold != self.similarity_threshold:
                adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
                reason_parts.append(f"Repetições consecutivas ({self.consecutive_repetition_count})")
            
            if old_interval != self.min_update_interval:
                adjustments.append(("min_update_interval", old_interval, self.min_update_interval, reason))
                reason_parts.append(f"Repetições consecutivas ({self.consecutive_repetition_count})")

        # Ajuste baseado em similaridade média
        if avg_similarity < 0.4:  # Similaridade muito baixa = muitas mudanças
            old_threshold = self.similarity_threshold
            self.similarity_threshold = max(self.min_similarity_threshold,
                                          self.similarity_threshold - self.similarity_adjust_step)
            
            reason = f"Similaridade média baixa ({avg_similarity:.2f}), muitas mudanças detectadas"
            
            if old_threshold != self.similarity_threshold:
                adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
                reason_parts.append(f"Similaridade média baixa ({avg_similarity:.2f})")

        # Log de ajustes
        if adjustments and self.usage_logger:
            for adjustment in adjustments:
                param, old_val, new_val, adj_reason = adjustment
                self.usage_logger.log_auto_adjust(param, old_val, new_val, adj_reason, {
                    "stdev": stdev,
                    "avg_delta": avg,
                    "avg_similarity": avg_similarity,
                    "repetition_rate": repetition_rate,
                    "repetition_count": self.repetition_count,
                    "exact_duplicate_count": self.exact_duplicate_count,
                    "consecutive_repetitions": self.consecutive_repetition_count,
                    "update_count": len(self.update_deltas)
                })

        return adjustments

    def _aggressive_adjust_for_repetitions(self):
        """
        Ajuste agressivo imediato quando detecta muitas repetições consecutivas.
        Este método é chamado quando há 3+ repetições consecutivas.
        """
        adjustments = []
        reason_parts = []
        
        # Aumenta threshold de similaridade agressivamente
        old_threshold = self.similarity_threshold
        old_interval = self.min_update_interval
        old_repetition_threshold = self.repetition_threshold
        
        # Ajustes agressivos
        self.similarity_threshold = min(self.max_similarity_threshold,
                                      self.similarity_threshold + self.similarity_adjust_step * 3)
        self.min_update_interval = min(150, self.min_update_interval + self.interval_adjust_step * 3)
        # Reduz threshold de repetição para detectar mais cedo
        self.repetition_threshold = max(0.7, self.repetition_threshold - 0.05)
        
        reason = f"Ajuste agressivo: {self.consecutive_repetition_count} repetições consecutivas detectadas (total: {self.repetition_count} repetições, {self.exact_duplicate_count} duplicatas exatas)"
        
        if old_threshold != self.similarity_threshold:
            adjustments.append(("similarity_threshold", old_threshold, self.similarity_threshold, reason))
            reason_parts.append(f"Repetições consecutivas detectadas ({self.consecutive_repetition_count})")
        
        if old_interval != self.min_update_interval:
            adjustments.append(("min_update_interval", old_interval, self.min_update_interval, reason))
            reason_parts.append(f"Repetições consecutivas detectadas ({self.consecutive_repetition_count})")
        
        if old_repetition_threshold != self.repetition_threshold:
            adjustments.append(("repetition_threshold", old_repetition_threshold, self.repetition_threshold, reason))
            reason_parts.append(f"Repetições consecutivas detectadas ({self.consecutive_repetition_count})")
        
        # Log e notificação
        if adjustments and self.usage_logger:
            reason_text = "; ".join(reason_parts)
            for adjustment in adjustments:
                param, old_val, new_val, adj_reason = adjustment
                self.usage_logger.log_auto_adjust(param, old_val, new_val, 
                                                 f"Ajuste agressivo: {adj_reason}",
                                                 {
                                                     "consecutive_repetitions": self.consecutive_repetition_count,
                                                     "total_repetitions": self.repetition_count,
                                                     "exact_duplicates": self.exact_duplicate_count,
                                                     "repetition_rate": self.repetition_count / max(1, self.commit_count + self.repetition_count)
                                                 })
        
        # Notifica UI
        if adjustments and self.auto_adjust_callback:
            for adjustment in adjustments:
                param, old_val, new_val, adj_reason = adjustment
                self.auto_adjust_callback(param, old_val, new_val, adj_reason)
        
        # Reset contador após ajuste agressivo
        self.consecutive_repetition_count = 0

    def force_check(self):
        """Método auxiliar para forçar checagem de timeout (usado por timers externos se necessário)."""
        self._check_timeout(time.time())
