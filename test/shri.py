from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Stock


def main() -> int:
    stock = Stock("SHRIRAMFIN")
    summary = stock.summary()

    print(summary["company_name"])
    print(summary["ratios"]["current_price"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
