# Final Verdict

Date: 2026-10-13

## Decision

Close the Polymarket project as a trading operation. Do not deploy a wallet,
start a live executor, or continue parameter hunting.

Keep this repository public as a reproducible research artifact. The reusable
asset is the data/replay/risk infrastructure, not a demonstrated strategy.

## Evidence

The historical maker-shadow replay produced positive numbers only under a proxy
fill model. At the documented snapshot:

- 44,837 continuous historical snapshots were available.
- 1,429 historical market/token instruments were replayed.
- 4,440 fills were inferred from public trade crossings.
- Proxy realized P&L was approximately `$350.90`.
- Proxy unrealized P&L was approximately `$681.39`.
- Estimated adverse selection was approximately `$1,242.94`.
- The model had no exchange acknowledgements, queue position, real order lifetime,
  partial-fill messages, network latency, or account-level rebate evidence.

The positive proxy result is therefore not a trading result. The adverse-selection
estimate is a stronger warning than the proxy P&L is a signal.

## What Was Salvaged

- Public order-book snapshot schema.
- Gamma cursor-based market discovery.
- Fee model.
- Inventory-aware quote generation.
- Snapshot replay and proxy-fill accounting.
- Drawdown and adverse-selection metrics.
- SQLite/CSV readers.
- Tests, CI, documentation and explicit safety boundaries.

## What Was Rejected

- Copy-trading.
- Favorite-fade as a capital strategy.
- BTC short-horizon trading.
- Generic NegRisk arbitrage.
- Historical shadow P&L presented as realized execution.
- A live executor in the public repository.

## Operational Closure

- `polybot.service` remains inactive.
- The temporary `maker-shadow-record.timer` was disabled and removed.
- No live order was submitted during this research cycle.
- The public repository contains no keys, wallet data, or production database.

## AI Limitation

An AI system can help build a recorder, simulator and falsifiable test. It cannot
manufacture an information advantage, queue priority, liquidity, or a guaranteed
positive expectancy. A strategy that fails after realistic execution costs should
be closed rather than explained away with more optimization.

The correct final result for this project is not a forced strategy. It is a clean,
reproducible rejection of an unproven trading thesis and a reusable open-source
research engine.
