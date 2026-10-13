"""Polymarket fee model from the public fee schedule.

The formula is expressed in shares and price:
    fee = shares * fee_rate * price * (1 - price)

Makers pay zero protocol fee. Rebate eligibility is deliberately not included
in the default model because rebate tiers and eligibility must be verified from
account-level data before being treated as P&L.
"""
from __future__ import annotations

FEE_RATES = {
    "crypto": 0.07,
    "sports": 0.05,
    "finance": 0.04,
    "politics": 0.04,
    "mentions": 0.04,
    "tech": 0.04,
    "geopolitics": 0.00,
    "economics": 0.05,
    "culture": 0.05,
    "weather": 0.05,
    "other": 0.05,
}


def category_fee_rate(category: str | None) -> float:
    tokens = {
        token.strip()
        for token in (category or "other").lower().replace(",", "|").split("|")
        if token.strip()
    }
    if "geopolitics" in tokens:
        return FEE_RATES["geopolitics"]
    for name, rate in sorted(FEE_RATES.items(), key=lambda item: len(item[0]), reverse=True):
        if name in tokens:
            return rate
    return FEE_RATES["other"]


def taker_fee(shares: float, price: float, category: str | None) -> float:
    if shares <= 0 or not 0.0 <= price <= 1.0:
        return 0.0
    return shares * category_fee_rate(category) * price * (1.0 - price)


def maker_fee(shares: float, price: float, category: str | None) -> float:
    del shares, price, category
    return 0.0
