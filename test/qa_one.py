"""Print one CNX500 constituent by position."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Index


def main() -> int:
    position = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    payload = Index("CNX500").constituents(limit=position)
    company = payload["companies"][position - 1]
    print(company["symbol"], "-", company["name"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
