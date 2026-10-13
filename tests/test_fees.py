import unittest

from polymarket_lab.fees import maker_fee, taker_fee


class FeeTests(unittest.TestCase):
    def test_maker_fee_is_zero(self):
        self.assertEqual(maker_fee(100, 0.5, "sports"), 0.0)

    def test_taker_fee_uses_category_rate(self):
        self.assertAlmostEqual(taker_fee(100, 0.5, "sports"), 1.25)

    def test_tagged_geopolitics_category_is_fee_free(self):
        self.assertEqual(taker_fee(100, 0.5, "geopolitics|politics|iran"), 0.0)


if __name__ == "__main__":
    unittest.main()
