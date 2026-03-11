"""Minimal BatchStock example."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Stock


def main() -> int:
    symbols = ["TCS", "INFY"]
    batch = Stock.batch(symbols)
    payload = batch.fetch("summary")

    for symbol in symbols:
        summary = payload[symbol]
        print(symbol)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print()
        Stock(symbol).pretty("summary")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
