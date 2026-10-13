"""Command-line entry point for read-only replay."""
from __future__ import annotations

import argparse
import json

from .io import from_csv, from_sqlite
from .metrics import summarize
from .replay import ReplayConfig, replay


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay Polymarket maker quotes without placing orders")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sqlite", help="SQLite file containing book_snapshots")
    source.add_argument("--csv", help="CSV file containing normalized snapshots")
    parser.add_argument("--market-id")
    parser.add_argument("--fill-fraction", type=float, default=1.0,
                        help="fraction of each proxy fill to accept, for stress tests")
    args = parser.parse_args()
    snapshots = from_sqlite(args.sqlite, args.market_id) if args.sqlite else from_csv(args.csv)
    result = replay(snapshots, ReplayConfig(fill_fraction=args.fill_fraction))
    print(json.dumps({"snapshots": len(snapshots), **summarize(result)}, indent=2))


if __name__ == "__main__":
    main()
