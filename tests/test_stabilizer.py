import unittest
import time
from src.core.stabilizer import CaptionStabilizer

class TestCaptionStabilizer(unittest.TestCase):
    def setUp(self):
        self.committed_phrases = []
        # Callback simples que guarda o que foi commitado
        self.stabilizer = CaptionStabilizer(
            on_commit_callback=lambda text: self.committed_phrases.append(text),
            initial_timeout_ms=100
        )

    def test_basic_deduplication(self):
        # Cenário: Frase sendo construída
        self.stabilizer.process_new_text("Ola")
        self.stabilizer.process_new_text("Ola tudo")
        self.stabilizer.process_new_text("Ola tudo bem")

        # Não deve ter commitado nada ainda, pois são similares/continuação
        self.assertEqual(len(self.committed_phrases), 0)
        self.assertEqual(self.stabilizer.current_buffer, "Ola tudo bem")

    def test_commit_on_new_phrase(self):
        self.stabilizer.process_new_text("Primeira frase")
        # Simula mudança brusca (nova frase)
        self.stabilizer.process_new_text("Segunda frase completamente diferente")

        self.assertEqual(len(self.committed_phrases), 1)
        self.assertEqual(self.committed_phrases[0], "Primeira frase")
        self.assertEqual(self.stabilizer.current_buffer, "Segunda frase completamente diferente")

    def test_commit_on_timeout(self):
        self.stabilizer.process_new_text("Frase isolada")
        time.sleep(0.2) # Espera 200ms (timeout é 100ms)

        # O process_new_text com texto vazio ou force_check deve disparar o commit
        self.stabilizer.force_check()

        self.assertEqual(len(self.committed_phrases), 1)
        self.assertEqual(self.committed_phrases[0], "Frase isolada")
        self.assertEqual(self.stabilizer.current_buffer, "")

    def test_dynamic_timeout_calculation(self):
        # Habilita auto timeout
        self.stabilizer.set_auto_timeout(True)
        # Reduz intervalo de recalculo para teste
        self.stabilizer.auto_recalc_interval = 0.1

        # Popula o deque com intervalos simulados
        # Simula delay de 100ms entre palavras
        for _ in range(10):
            self.stabilizer.update_deltas.append(100)

        # Força recalculo
        time.sleep(0.2)
        self.stabilizer._recalculate_if_needed(time.time())

        # Média = 100. Stdev = 0.
        # Fórmula: Avg + 3*Stdev + 500 = 100 + 0 + 500 = 600
        # Mas existe o MinLimit de 1000. Então deve ser 1000.
        self.assertEqual(self.stabilizer.silence_timeout_ms, 1000)

    def test_broken_input_simulation(self):
        # Teste solicitado no prompt
        inputs = ["Ola", "Ola tudo", "Ola tudo bem.", "Hoje vamos", "Hoje vamos programar"]

        # Passo 1: "Ola" -> "Ola tudo" -> "Ola tudo bem."
        for text in inputs[:3]:
            self.stabilizer.process_new_text(text)

        # Agora vem "Hoje vamos" - similaridade baixa com "Ola tudo bem."
        # Deve commitar "Ola tudo bem."
        self.stabilizer.process_new_text(inputs[3])

        # "Hoje vamos" -> "Hoje vamos programar"
        self.stabilizer.process_new_text(inputs[4])

        # Force flush final
        time.sleep(0.2)
        self.stabilizer.force_check()

        expected = ["Ola tudo bem.", "Hoje vamos programar"]
        self.assertEqual(self.committed_phrases, expected)

if __name__ == '__main__':
    unittest.main()
