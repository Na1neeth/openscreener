"""Fetch the full raw payload for Shriram Finance."""

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
    stock = Stock("519604", consolidated=False
                  )

    raw_data = stock.all()
    print(json.dumps(raw_data, indent=2, ensure_ascii=False))
    stock.pretty()
    stock.pretty("ratios")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
