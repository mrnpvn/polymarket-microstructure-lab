"""Snapshot replay with explicitly labelled proxy fills."""
from __future__ import annotations

from dataclasses import dataclass

from .maker import MakerConfig, quote
from .models import BookSnapshot, Fill, ReplayResult


@dataclass(frozen=True)
class ReplayConfig:
    maker: MakerConfig = MakerConfig()
    adverse_window: int = 5
    mark_to_mid: bool = True
    fill_fraction: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 < self.fill_fraction <= 1.0:
            raise ValueError("fill_fraction must be in (0, 1]")


def _crosses(side: str, quote_price: float | None, snapshot: BookSnapshot) -> bool:
    if quote_price is None or snapshot.last_trade_price is None:
        return False
    if side == "BUY":
        return snapshot.last_trade_price <= quote_price
    return snapshot.last_trade_price >= quote_price


def replay(snapshots: list[BookSnapshot], config: ReplayConfig | None = None) -> ReplayResult:
    """Replay snapshots in timestamp order.

    A proxy fill occurs only when a later public trade crosses the previous
    quote. This is deliberately conservative in wording: a crossing is not an
    exchange fill, and the result must not be presented as realized profit.
    """
    cfg = config or ReplayConfig()
    snapshots = sorted(snapshots, key=lambda x: x.ts)
    instruments = {(s.market_id, s.token_id) for s in snapshots}
    if len(instruments) > 1:
        raise ValueError("replay one market/token at a time; aggregate results after replay")
    fills: list[Fill] = []
    equity: list[tuple[float, float]] = []
    inventory_shares = 0.0
    average_cost = 0.0
    cash = 0.0
    realized = 0.0
    max_inventory = 0.0
    previous_quote = None

    for snapshot in snapshots:
        if previous_quote is not None:
            mark = snapshot.mid or snapshot.last_trade_price or 0.0
            inventory_usd = inventory_shares * mark
            if _crosses("BUY", previous_quote.bid, snapshot) and inventory_usd < cfg.maker.max_inventory_usd:
                size = min(cfg.maker.quote_size_usd, cfg.maker.max_inventory_usd - inventory_usd)
                size *= cfg.fill_fraction
                shares = size / previous_quote.bid
                average_cost = ((inventory_shares * average_cost) + (shares * previous_quote.bid)) / max(
                    inventory_shares + shares, 1e-12
                )
                inventory_shares += shares
                cash -= size
                fills.append(Fill(snapshot.ts, snapshot.market_id, snapshot.token_id,
                                  "BUY", previous_quote.bid, size, "trade_cross_proxy"))
            inventory_usd = inventory_shares * mark
            if _crosses("SELL", previous_quote.ask, snapshot) and inventory_usd > -cfg.maker.max_inventory_usd:
                shares = min(cfg.maker.quote_size_usd / previous_quote.ask, inventory_shares)
                shares *= cfg.fill_fraction
                size = shares * previous_quote.ask
                realized += (previous_quote.ask - average_cost) * shares
                inventory_shares -= shares
                if inventory_shares <= 1e-12:
                    inventory_shares = 0.0
                    average_cost = 0.0
                cash += size
                fills.append(Fill(snapshot.ts, snapshot.market_id, snapshot.token_id,
                                  "SELL", previous_quote.ask, size, "trade_cross_proxy"))

        mark = snapshot.mid or snapshot.last_trade_price or 0.0
        current_quote = quote(snapshot, inventory_shares * mark, cfg.maker)
        previous_quote = current_quote
        mark = (snapshot.mid if cfg.mark_to_mid else snapshot.last_trade_price) or 0.0
        equity_value = cash + inventory_shares * mark
        max_inventory = max(max_inventory, abs(inventory_shares * mark))
        equity.append((snapshot.ts, equity_value))

    peak = 0.0
    max_dd = 0.0
    for _, value in equity:
        peak = max(peak, value)
        max_dd = max(max_dd, peak - value)

    adverse = 0.0
    for i, fill in enumerate(fills):
        future = [s for s in snapshots if s.ts > fill.ts][:cfg.adverse_window]
        if not future:
            continue
        future_mid = future[-1].mid
        if future_mid is None:
            continue
        if fill.side == "BUY":
            adverse += max(0.0, fill.price - future_mid) * fill.size_usd / fill.price
        else:
            adverse += max(0.0, future_mid - fill.price) * fill.size_usd / fill.price

    last_mark = (snapshots[-1].mid or snapshots[-1].last_trade_price or 0.0) if snapshots else 0.0
    open_value = inventory_shares * last_mark
    return ReplayResult(
        fills=fills,
        equity=equity,
        proxy_realized_pnl=realized,
        proxy_unrealized_pnl=(open_value - inventory_shares * average_cost),
        max_drawdown=max_dd,
        max_inventory_usd=max_inventory,
        adverse_selection_usd=adverse,
    )
