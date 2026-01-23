import difflib
import time
import statistics
from collections import deque

class CaptionStabilizer:
    def __init__(self, on_commit_callback, initial_timeout_ms=1500):
        """
        :param on_commit_callback: Função para chamar quando uma frase é finalizada (str).
        :param initial_timeout_ms: Tempo inicial em ms para considerar silêncio.
        """
        self.on_commit = on_commit_callback
        self.current_buffer = ""
        self.last_update_time = time.time()

        # Configurações de Timeout
        self.silence_timeout_ms = initial_timeout_ms
        self.is_auto_timeout = False
        self.min_timeout_ms = 1000
        self.max_timeout_ms = 5000

        # Para estatísticas dinâmicas
        self.update_deltas = deque(maxlen=50) # Guarda os últimos 50 intervalos entre updates da MESMA frase
        self.last_recalc_time = time.time()
        self.recalc_interval = 30 # segundos

    def set_timeout_ms(self, ms):
        self.silence_timeout_ms = ms

    def set_auto_timeout(self, enabled):
        self.is_auto_timeout = enabled

    def process_new_text(self, raw_text):
        """
        Processa o texto cru vindo do OCR.
        Deve ser chamado frequentemente pelo loop principal.
        """
        now = time.time()

        # Remove espaços extras
        raw_text = raw_text.strip()

        # Se texto vazio, apenas checa timeout
        if not raw_text:
            self._check_timeout(now)
            return

        # Similaridade
        matcher = difflib.SequenceMatcher(None, self.current_buffer, raw_text)
        similarity = matcher.ratio()

        # Lógica de decisão
        is_same_phrase = similarity > 0.6

        # Caso especial: Buffer atual está contido no novo texto (expansão direta)
        # Ex: "Ola" -> "Ola tudo" (Similaridade pode ser baixa se "Ola" for muito curto comparado a "Ola tudo",
        # mas é claramente uma continuação).
        if not is_same_phrase and self.current_buffer and self.current_buffer in raw_text:
             is_same_phrase = True

        if is_same_phrase:
            # É a mesma frase sendo corrigida/expandida
            # Registra estatística de tempo se for uma atualização rápida (continuidade da fala)
            time_since_last = (now - self.last_update_time) * 1000 # ms
            if time_since_last > 50: # Ignora updates instantâneos demais (ruído)
                self.update_deltas.append(time_since_last)

            # Atualiza buffer com a versão mais longa (geralmente a mais completa)
            # Mas cuidado: às vezes o corretor diminui a frase.
            # No Live Captions, geralmente cresce ou corrige palavras.
            # Vamos assumir o novo texto como a verdade atual.
            self.current_buffer = raw_text
            self.last_update_time = now
        else:
            # Frase mudou completamente
            self._commit_buffer()
            self.current_buffer = raw_text
            self.last_update_time = now

        # Checa e executa lógica dinâmica periodicamente
        if self.is_auto_timeout:
            self._recalculate_timeout_if_needed(now)

    def _check_timeout(self, now):
        """Verifica se excedeu o tempo de silêncio."""
        if not self.current_buffer:
            return

        elapsed_ms = (now - self.last_update_time) * 1000
        if elapsed_ms > self.silence_timeout_ms:
            self._commit_buffer()

    def _commit_buffer(self):
        """Salva a frase atual e limpa o buffer."""
        if self.current_buffer:
            self.on_commit(self.current_buffer)
            self.current_buffer = ""

    def _recalculate_timeout_if_needed(self, now):
        if (now - self.last_recalc_time) < self.recalc_interval:
            return

        if len(self.update_deltas) > 5:
            avg = statistics.mean(self.update_deltas)
            try:
                stdev = statistics.stdev(self.update_deltas)
            except:
                stdev = 0

            # Novo timeout sugerido: Média + 3 sigmas + margem
            # Isso cobre 99% dos casos de intervalo entre palavras da mesma frase
            new_timeout = avg + (3 * stdev) + 500

            # Clamp
            new_timeout = max(self.min_timeout_ms, min(new_timeout, self.max_timeout_ms))

            print(f"[Auto-Timeout] Recalculado: {int(new_timeout)}ms (Avg: {int(avg)}ms, Stdev: {int(stdev)}ms)")
            self.silence_timeout_ms = int(new_timeout)

        self.last_recalc_time = now
        # Não limpamos self.update_deltas completamente para manter histórico,
        # mas o deque(maxlen=50) já cuida de manter apenas os recentes.

    def force_check(self):
        """Método auxiliar para forçar checagem de timeout (usado por timers externos se necessário)."""
        self._check_timeout(time.time())
