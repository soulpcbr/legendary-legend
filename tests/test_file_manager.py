import unittest
import os
import shutil
import tempfile
from src.core.file_manager import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        # Cria um diretório temporário para os testes
        self.test_dir = tempfile.mkdtemp()
        self.fm = FileManager(output_dir=self.test_dir, max_files=3, max_size_mb=1)

    def tearDown(self):
        # Limpa após os testes
        self.fm.close()
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertEqual(self.fm.max_files, 3)
        self.assertEqual(self.fm.max_file_size, 1024 * 1024)
        
    def test_append_text(self):
        self.fm.append_text("Primeira linha de teste")
        self.assertTrue(os.path.exists(self.fm.filepath))
        
        with open(self.fm.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Primeira linha de teste", content)
            self.assertIn("[", content) # timestamp

    def test_generate_summary(self):
        # Adiciona algumas frases
        self.fm.append_text("Olá mundo, este é um teste")
        self.fm.append_text("Teste de sumário e extração de mundo")
        
        # Fecha para garantir a gravação e evitar conflitos de leitura simultânea no Windows (se aplicável), 
        # mas o python consegue ler arquivo aberto, o append_text dá flush.
        summary_path, count, timestamp = self.fm.generate_summary()
        
        self.assertIsNotNone(summary_path)
        self.assertTrue(os.path.exists(summary_path))
        self.assertTrue(count > 0)
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines()]
            # "olá", "mundo", "este", "é", "um", "teste", "de", "sumário", "e", "extração"
            # count = 10 unique words
            self.assertIn("mundo", lines)
            self.assertIn("teste", lines)
            self.assertEqual(len(lines), count)

if __name__ == '__main__':
    unittest.main()
