# Maker Shadow Validation

This is an offline validation of the existing PolyBot `maker_shadow` database.
The database itself is not included in this repository.

## Source

- Source: `/opt/polybot/maker_shadow/maker_shadow.db`
- Table: `book_snapshots`
- Historical rows through the last continuous run: 44,837
- Historical observation window: 2026-05-25 15:27:20 UTC through 2026-06-18 02:13:01 UTC
- Read-only refresh on 2026-10-13 11:46:27 UTC: 40 additional rows across 40 instruments
- Current totals: 44,877 rows and 1,469 distinct market/token instruments
- Rows with `last_trade_price`: 44,877

There is no continuous coverage between 2026-06-18 and 2026-10-13. The refresh
is useful as a recorder smoke test, but it does not create a 14-day validation
window.

## Replay Result

Using the default public replay configuration:

- Instruments replayed independently: 1,429
- Instruments with at least one inferred fill: 367
- Inferred fills: 4,440
- Sum of proxy realized P&L: approximately `$350.90`
- Sum of proxy unrealized P&L at the final marks: approximately `$681.39`
- Sum of adverse-selection estimate: approximately `$1,242.94`
- Maximum per-instrument drawdown: approximately `$43.17`

As a simple fill-availability stress, accepting only 50% of each inferred fill
produced 4,605 proxy fills, approximately `$240.57` of proxy realized P&L,
approximately `$400.37` of proxy unrealized P&L, and approximately `$608.82` of
adverse-selection estimate. This is still the same uncalibrated proxy model;
the different fill count shows why a fractional-fill control is not a substitute
for queue-position data.

These numbers are **not evidence of profitability**. The replay has no exchange
acknowledgements, queue position, real order lifetime, partial-fill messages,
network latency, or authenticated account data. The positive proxy number is
therefore expected to be fragile and must not be used to activate a wallet.

The adverse-selection estimate being larger than the aggregate proxy P&L is a
warning sign, not a signal to tune the strategy. It indicates that the public
snapshot data is currently more useful for detecting execution risk than for
proving spread capture.

The legacy recorder initially failed because Gamma now rejects offset pagination
above 2,000 with `422 offset too large; use /markets/keyset`. Its scan was
limited to the supported offset range for the smoke test. A proper current
recorder still needs Gamma keyset pagination before starting the validation
window.

## Next Validation Required

1. Keep recording current L2 snapshots with quote timestamps.
2. Run a private paper executor that records submitted quotes, acknowledgements,
   cancellations and fills without sending money.
3. Calibrate the proxy model against those confirmations.
4. Replay two future, untouched time windows.
5. Apply the research gate in `docs/research-plan.md`.
