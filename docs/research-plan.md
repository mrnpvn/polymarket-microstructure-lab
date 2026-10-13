# Research Plan

## Hypothesis

A maker can capture part of the spread in fee-free or low-fee Polymarket
markets when quotes are inventory-aware and not adversely selected.

This is a hypothesis, not an edge claim.

## Data Collection

Record, with UTC timestamps:

- best bid and ask,
- depth at every relevant level,
- last trade price and size when available,
- market category and resolution time,
- quote creation and cancellation time,
- local network latency,
- real order acknowledgements and fills in the private harness.

Public snapshots alone cannot prove that an order would have filled.

## Experiments

### A. Passive spread capture

Quote one tick inside the market when the spread and depth pass limits. Measure
the price movement after a proxy fill. This is a diagnostic, not production.

### B. Inventory-aware market making

Skew quotes away from the side that increases inventory. Compare fixed, linear,
and volatility-scaled skew without choosing parameters on the final test set.

### C. Fair-value overlay

Use an external, timestamped probability estimate. Quote only when the fair
value is separated from the mid by more than fees, spread, and a declared
adverse-selection buffer.

## Validation

Split by event and time, not random rows. Report:

- proxy fills and confirmed fills separately,
- gross spread capture,
- fees and rebates separately,
- adverse-selection cost,
- realized and mark-to-market P&L separately,
- inventory duration,
- maximum drawdown,
- P&L concentration by market and event.

Minimum gate: 500 supported fills, two independent out-of-sample periods, no
market contributing over 15% of profit, and positive results after doubled
slippage and fees.

## Kill Conditions

- The result disappears when proxy fills are reduced by 50%.
- The result becomes negative with doubled costs.
- Fills are concentrated immediately before adverse price moves.
- Inventory remains open through resolution with losses larger than captured spread.
- The result depends on one market, one event, or one parameter corner.

Any kill condition ends the Polymarket trading experiment. More parameter
search is not a mitigation for missing edge.
