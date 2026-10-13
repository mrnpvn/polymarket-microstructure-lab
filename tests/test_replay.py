import unittest

from polymarket_lab.models import BookSnapshot
from polymarket_lab.replay import ReplayConfig, replay


class ReplayTests(unittest.TestCase):
    def test_crossing_trade_creates_proxy_fill_not_realized_pnl(self):
        snapshots = [
            BookSnapshot("m", "t", 1, "geopolitics", 0.40, 0.50, 100, 100, 0.45, 0.01),
            BookSnapshot("m", "t", 2, "geopolitics", 0.39, 0.49, 100, 100, 0.39, 0.01),
        ]
        result = replay(snapshots, ReplayConfig())
        self.assertGreaterEqual(len(result.fills), 1)
        self.assertEqual(result.proxy_realized_pnl, 0.0)
        self.assertIn("proxy", result.proxy_warning.lower())

    def test_fill_fraction_is_available_for_stress_tests(self):
        snapshots = [
            BookSnapshot("m", "t", 1, "geopolitics", 0.40, 0.50, 100, 100, 0.45, 0.01),
            BookSnapshot("m", "t", 2, "geopolitics", 0.39, 0.49, 100, 100, 0.39, 0.01),
        ]
        full = replay(snapshots).fills
        half = replay(snapshots, ReplayConfig(fill_fraction=0.5)).fills
        self.assertEqual(len(full), len(half))
        self.assertLess(sum(f.size_usd for f in half), sum(f.size_usd for f in full))


if __name__ == "__main__":
    unittest.main()
