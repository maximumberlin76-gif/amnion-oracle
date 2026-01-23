import unittest

from controller.safety_gate import SafetyGate


class TestSafetyGate(unittest.TestCase):
    def setUp(self):
        self.gate = SafetyGate()

    def test_accepts_normal_input(self):
        data = {"temperature": 22.0, "pressure": 1.0, "coherence": 0.95}
        result = self.gate.evaluate(data)
        self.assertIsInstance(result, dict)
        self.assertIn("allowed", result)
        self.assertIn("risk", result)
        self.assertIn("violations", result)

    def test_blocks_invalid_types(self):
        data = {"temperature": "hot", "pressure": 1.0, "coherence": 0.95}
        result = self.gate.evaluate(data)
        self.assertFalse(result["allowed"])
        self.assertGreaterEqual(result["risk"], 0.5)

    def test_blocks_out_of_range(self):
        data = {"temperature": 9999.0, "pressure": -10.0, "coherence": 2.0}
        result = self.gate.evaluate(data)
        self.assertFalse(result["allowed"])
        self.assertGreaterEqual(result["risk"], 0.5)


if __name__ == "__main__":
    unittest.main()
  
