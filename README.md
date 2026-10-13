# Polymarket Microstructure Lab

Read-only research tools for testing whether a Polymarket maker strategy survives
fees, inventory risk, adverse selection, and realistic public-data fills.

This is **not** a profitable bot, a trading signal service, or financial advice.
It never authenticates, signs, or submits orders. There are no private keys,
wallets, account identifiers, or production databases in this repository.

## Why This Exists

Historical Polymarket P&L is easy to overstate. A credible test must keep these
questions separate:

- Did a public trade cross our quote, or did our order actually fill?
- Was the quoted size available at that price?
- Did inventory move against us immediately after the fill?
- Were protocol fees, rebates, resolution, and stale data handled correctly?
- Is the result positive outside the period used to choose parameters?

The lab reports proxy fills explicitly. A proxy fill is not realized exchange P&L.

## Current Scope

- Normalize order-book snapshots from CSV or the existing `maker_shadow` SQLite schema.
- Discover open markets through Gamma's cursor-based `/markets/keyset` endpoint.
- Apply the published Polymarket taker fee model.
- Generate inventory-aware two-sided maker quotes.
- Replay public snapshots with a conservative trade-crossing fill proxy.
- Measure inventory, drawdown, and adverse selection.
- Keep live order submission outside the public repository.
- Provide a hardened, read-only systemd timer for continuous snapshot capture.

## Quick Start

```powershell
python -m unittest discover -s tests -v
python -m polymarket_lab.cli --csv snapshots.csv
python -m polymarket_lab.cli --sqlite maker_shadow.db --market-id CONDITION_ID
python -m polymarket_lab.cli --sqlite maker_shadow.db --market-id CONDITION_ID --fill-fraction 0.5
```

The optional files in `deploy/` run only the existing read-only shadow recorder;
they do not start `bot.main` or submit orders.

The package uses only the Python standard library.

Replay one market/token at a time. Aggregate per-market reports only after each
instrument has been replayed independently.

## Data Contract

CSV input must contain:

```text
market_id,token_id,ts,category,best_bid,best_ask,bid_depth_usd,ask_depth_usd,last_trade_price,tick_size
```

The SQLite reader expects a `book_snapshots` table with the same fields. The
original Polymarket recorder contains additional columns; they are ignored by
the reader.

## Interpretation Rules

The result is not evidence of profitability unless all of the following are
available:

1. Point-in-time data with no look-ahead.
2. A fill model calibrated against real order acknowledgements and fills.
3. Partial fills, queue position, cancellations, and stale quotes.
4. Category-specific fees and verified rebate treatment.
5. Inventory and resolution losses.
6. Walk-forward validation over independent events.

The default replay intentionally fails open to **no claim**: it reports proxy
fills and labels all resulting P&L as `proxy_*`, never as exchange-realized P&L.

`--fill-fraction 0.5` is a simple stress control that accepts only half of each
inferred fill. It is not a queue-position model; confirmed exchange fills are
still required before treating a result as trading evidence.

## Proposed Research Gate

Do not connect a wallet until a private execution harness has demonstrated:

- at least 500 independently supported fills,
- positive net P&L after doubled slippage and fees,
- no single market contributing more than 15% of profit,
- bounded inventory and drawdown,
- positive results in two out-of-sample periods.

If the gate fails, archive Polymarket trading rather than tune another parameter.

## Security Boundary

The public repository deliberately excludes:

- private keys and signing code,
- wallet addresses and personal databases,
- live order submission,
- account-specific rebate assumptions,
- unreviewed strategy parameters.

Live execution belongs in a separate private repository after the research gate
passes.

## Official References

- [Polymarket fees](https://docs.polymarket.com/polymarket-learn/trading/fees)
- [Polymarket SDK and API entry points](https://docs.polymarket.com/getting-started/api)
- [Betfair Exchange API](https://developer.betfair.com/exchange-api/)

## License

MIT. This license does not make the data sources, exchange terms, or trading
outcomes risk-free.
