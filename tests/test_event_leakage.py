import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from scripts.check_event_leakage import audit_leakage


class TestEventLeakage(unittest.TestCase):
    """Tests the explicit data leakage audit checker and zero-leakage guarantees."""

    def test_audit_leakage_passes_without_exceptions(self):
        """Verify audit_leakage() succeeds and finds 0 violations."""
        result = audit_leakage()
        self.assertEqual(result.get("status"), "PASSED")
        self.assertEqual(result.get("violations_count"), 0)

    def test_chronological_ordering_strictly_maintained(self):
        """Verify train < validation < test timestamps."""
        result = audit_leakage()
        train_max = result["train_max_dt"]
        val_min = result["val_min_dt"]
        val_max = result["val_max_dt"]
        test_min = result["test_min_dt"]

        self.assertLess(train_max, val_min)
        self.assertLess(val_max, test_min)


if __name__ == "__main__":
    unittest.main()
