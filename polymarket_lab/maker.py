"""Inventory-aware two-sided quote generation.

This is a quote candidate generator, not an executor. It intentionally does
not know about credentials, wallets, or order submission.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import BookSnapshot, Quote


@dataclass(frozen=True)
class MakerConfig:
    min_spread: float = 0.02
    max_spread: float = 0.15
    quote_size_usd: float = 10.0
    max_inventory_usd: float = 100.0
    min_depth_usd: float = 10.0
    inventory_skew: float = 0.25


def _tick_down(price: float, tick: float) -> float:
    return round((price // tick) * tick, 8)


def _tick_up(price: float, tick: float) -> float:
    return round(((price + tick - 1e-12) // tick) * tick, 8)


def quote(snapshot: BookSnapshot, inventory_usd: float, config: MakerConfig) -> Quote:
    """Generate a conservative quote or a no-quote reason.

    Inventory is positive for a long YES inventory. Positive inventory shifts
    both quotes down so new fills are less likely to add risk and the ask is
    more competitive. The function never assumes that a quote will fill.
    """
    if not snapshot.valid():
        return Quote(snapshot.ts, snapshot.market_id, snapshot.token_id, None, None,
                     config.quote_size_usd, "invalid_book")
    spread = snapshot.spread
    if spread is None or spread < config.min_spread or spread > config.max_spread:
        return Quote(snapshot.ts, snapshot.market_id, snapshot.token_id, None, None,
                     config.quote_size_usd, "spread_outside_limits")
    if min(snapshot.bid_depth_usd, snapshot.ask_depth_usd) < config.min_depth_usd:
        return Quote(snapshot.ts, snapshot.market_id, snapshot.token_id, None, None,
                     config.quote_size_usd, "insufficient_depth")

    mid = snapshot.mid
    skew = config.inventory_skew * (inventory_usd / max(config.max_inventory_usd, 1e-9))
    half = spread / 2.0
    bid = _tick_down(mid - half - skew, snapshot.tick_size)
    ask = _tick_up(mid + half - skew, snapshot.tick_size)
    bid = max(snapshot.tick_size, min(bid, snapshot.best_ask - snapshot.tick_size))
    ask = min(1.0 - snapshot.tick_size, max(ask, snapshot.best_bid + snapshot.tick_size))
    if bid >= ask:
        return Quote(snapshot.ts, snapshot.market_id, snapshot.token_id, None, None,
                     config.quote_size_usd, "crossed_after_skew")
    return Quote(snapshot.ts, snapshot.market_id, snapshot.token_id, bid, ask,
                 config.quote_size_usd, "ok")
