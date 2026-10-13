"""Read-only Gamma market discovery with cursor pagination.

Gamma rejects deep ``offset`` pagination. This client uses ``/markets/keyset``
and carries ``next_cursor`` forward. It never authenticates or submits orders.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MarketPage:
    markets: list[dict[str, Any]]
    next_cursor: str | None


def parse_keyset_response(payload: Any) -> MarketPage:
    if isinstance(payload, dict):
        markets = payload.get("markets") or []
        return MarketPage(list(markets), payload.get("next_cursor"))
    if isinstance(payload, list):
        return MarketPage(list(payload), None)
    raise TypeError("Gamma response must be an object or list")


class GammaClient:
    def __init__(self, base_url: str = "https://gamma-api.polymarket.com", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def keyset_page(
        self,
        limit: int = 100,
        ascending: bool = False,
        after_cursor: str | None = None,
    ) -> MarketPage:
        params: dict[str, str | int] = {"limit": limit, "ascending": str(ascending).lower()}
        if after_cursor:
            params["after_cursor"] = after_cursor
        url = f"{self.base_url}/markets/keyset?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers={"User-Agent": "polymarket-microstructure-lab/0.1"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return parse_keyset_response(json.loads(response.read().decode("utf-8")))

    def iter_markets(self, limit: int = 100, max_pages: int = 21):
        cursor = None
        for _ in range(max_pages):
            page = self.keyset_page(limit=limit, after_cursor=cursor)
            if not page.markets:
                return
            yield from page.markets
            if not page.next_cursor:
                return
            cursor = page.next_cursor
