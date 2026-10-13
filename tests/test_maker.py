import unittest

from polymarket_lab.maker import MakerConfig, quote
from polymarket_lab.models import BookSnapshot


class QuoteTests(unittest.TestCase):
    def test_quote_respects_spread_and_inventory(self):
        snapshot = BookSnapshot("m", "t", 1, "geopolitics", 0.40, 0.50, 100, 100, 0.45, 0.01)
        result = quote(snapshot, 0, MakerConfig(min_spread=0.05, quote_size_usd=10))
        self.assertEqual(result.reason, "ok")
        self.assertLess(result.bid, result.ask)

    def test_bad_book_is_not_quoted(self):
        snapshot = BookSnapshot("m", "t", 1, "other", 0.5, 0.5, 100, 100, 0.5, 0.01)
        self.assertEqual(quote(snapshot, 0, MakerConfig()).reason, "invalid_book")


if __name__ == "__main__":
    unittest.main()
