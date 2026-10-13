"""Readers for sanitized order-book snapshot sources."""
from __future__ import annotations

import csv
import sqlite3

from .models import BookSnapshot


def _float(value):
    return None if value in (None, "") else float(value)


def from_csv(path: str) -> list[BookSnapshot]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            BookSnapshot(
                market_id=row["market_id"], token_id=row["token_id"], ts=float(row["ts"]),
                category=row.get("category") or "other", best_bid=_float(row.get("best_bid")),
                best_ask=_float(row.get("best_ask")), bid_depth_usd=float(row.get("bid_depth_usd") or 0),
                ask_depth_usd=float(row.get("ask_depth_usd") or 0),
                last_trade_price=_float(row.get("last_trade_price")),
                tick_size=float(row.get("tick_size") or 0.01),
            )
            for row in csv.DictReader(handle)
        ]


def from_sqlite(path: str, market_id: str | None = None) -> list[BookSnapshot]:
    where = " WHERE market_id = ?" if market_id else ""
    args = (market_id,) if market_id else ()
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT market_id,token_id,ts,category,best_bid,best_ask,bid_depth_usd,"
            "ask_depth_usd,last_trade_price,tick_size FROM book_snapshots" + where + " ORDER BY ts",
            args,
        )
        return [
            BookSnapshot(
                market_id=r[0], token_id=r[1], ts=float(r[2]), category=r[3] or "other",
                best_bid=_float(r[4]), best_ask=_float(r[5]), bid_depth_usd=float(r[6] or 0),
                ask_depth_usd=float(r[7] or 0), last_trade_price=_float(r[8]),
                tick_size=float(r[9] or 0.01),
            )
            for r in rows
        ]
