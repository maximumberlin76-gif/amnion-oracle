import unittest

from controller.amnion_controller import AmnionController


class TestControllerLoop(unittest.TestCase):
    def setUp(self):
        self.c = AmnionController()

    def test_step_returns_dict(self):
        out = self.c.step({"temperature": 22.0, "pressure": 1.0, "coherence": 0.95})
        self.assertIsInstance(out, dict)

    def test_step_has_basic_contract(self):
        out = self.c.step({"temperature": 22.0, "pressure": 1.0, "coherence": 0.95})
        # базовый контракт ответа контроллера (минимум)
        for k in ["ts", "input", "decision"]:
            self.assertIn(k, out)

    def test_step_handles_missing_fields(self):
        out = self.c.step({"temperature": 22.0})
        self.assertIsInstance(out, dict)


if __name__ == "__main__":
    unittest.main()
  
