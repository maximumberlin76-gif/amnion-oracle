import unittest

from controller.metrics import Metrics


class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.m = Metrics()

    def test_initial_state(self):
        snap = self.m.snapshot()
        self.assertIsInstance(snap, dict)
        self.assertIn("steps", snap)
        self.assertIn("violations", snap)

    def test_record_step(self):
        self.m.record_step(
            input_data={"temperature": 22.0, "pressure": 1.0, "coherence": 0.95},
            output_data={"allowed": True, "risk": 0.1, "violations": []},
        )
        snap = self.m.snapshot()
        self.assertGreaterEqual(snap["steps"], 1)

    def test_record_violation(self):
        self.m.record_violation("coherence_out_of_range")
        snap = self.m.snapshot()
        self.assertGreaterEqual(snap["violations"], 1)

    def test_reset(self):
        self.m.record_violation("x")
        self.m.reset()
        snap = self.m.snapshot()
        self.assertEqual(snap["violations"], 0)


if __name__ == "__main__":
    unittest.main()
