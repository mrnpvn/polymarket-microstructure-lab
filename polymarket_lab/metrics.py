"""Metrics that keep proxy fills and realized exchange P&L separate."""
from __future__ import annotations

from .models import Fill, ReplayResult


def summarize(result: ReplayResult) -> dict[str, float | int | str]:
    buys = sum(1 for f in result.fills if f.side == "BUY")
    sells = sum(1 for f in result.fills if f.side == "SELL")
    return {
        "proxy_fills": len(result.fills),
        "proxy_buys": buys,
        "proxy_sells": sells,
        "proxy_realized_pnl": round(result.proxy_realized_pnl, 6),
        "proxy_unrealized_pnl": round(result.proxy_unrealized_pnl, 6),
        "max_drawdown": round(result.max_drawdown, 6),
        "max_inventory_usd": round(result.max_inventory_usd, 6),
        "adverse_selection_usd": round(result.adverse_selection_usd, 6),
        "warning": result.proxy_warning,
    }
