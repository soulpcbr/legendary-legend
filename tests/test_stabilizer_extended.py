import unittest
from src.core.stabilizer import CaptionStabilizer

class TestStabilizerExtended(unittest.TestCase):
    def setUp(self):
        self.committed = []
        self.stabilizer = CaptionStabilizer(
            on_commit_callback=self.committed.append,
            initial_timeout_ms=500
        )

    def test_partial_overlap(self):
        # Testa scenario on "hello" -> "hello world"
        self.stabilizer.process_new_text("hello")
        self.stabilizer.process_new_text("hello world")
        self.assertEqual(self.stabilizer.current_buffer, "hello world")
        self.assertEqual(len(self.committed), 0)

    def test_correction(self):
        # Testa scenario on "helo" -> "hello" (correction)
        self.stabilizer.process_new_text("helo")
        self.stabilizer.process_new_text("hello") # High similarity
        self.assertEqual(self.stabilizer.current_buffer, "hello")
        self.assertEqual(len(self.committed), 0)

if __name__ == '__main__':
    unittest.main()
