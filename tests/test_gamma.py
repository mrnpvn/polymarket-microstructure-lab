import unittest

from polymarket_lab.gamma import MarketPage, parse_keyset_response


class GammaTests(unittest.TestCase):
    def test_keyset_payload_is_normalized(self):
        page = parse_keyset_response({"markets": [{"conditionId": "m"}], "next_cursor": "c1"})
        self.assertEqual(page, MarketPage([{"conditionId": "m"}], "c1"))

    def test_legacy_list_payload_still_parses_without_cursor(self):
        page = parse_keyset_response([{"conditionId": "m"}])
        self.assertEqual(page, MarketPage([{"conditionId": "m"}], None))


if __name__ == "__main__":
    unittest.main()
