"""Small, venue-neutral data models used by the replay engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BookSnapshot:
    market_id: str
    token_id: str
    ts: float
    category: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    bid_depth_usd: float = 0.0
    ask_depth_usd: float = 0.0
    last_trade_price: Optional[float] = None
    tick_size: float = 0.01

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    @property
    def mid(self) -> Optional[float]:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2.0

    def valid(self) -> bool:
        return (
            self.best_bid is not None
            and self.best_ask is not None
            and 0.0 < self.best_bid < self.best_ask < 1.0
            and self.tick_size > 0
        )


@dataclass(frozen=True)
class Quote:
    ts: float
    market_id: str
    token_id: str
    bid: Optional[float]
    ask: Optional[float]
    size_usd: float
    reason: str = ""


@dataclass(frozen=True)
class Fill:
    ts: float
    market_id: str
    token_id: str
    side: str
    price: float
    size_usd: float
    evidence: str


@dataclass
class ReplayResult:
    fills: list[Fill]
    equity: list[tuple[float, float]]
    proxy_realized_pnl: float
    proxy_unrealized_pnl: float
    max_drawdown: float
    max_inventory_usd: float
    adverse_selection_usd: float
    proxy_warning: str = (
        "Proxy fills are inferred from public snapshots and are not exchange confirmations."
    )
