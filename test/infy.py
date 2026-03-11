"""Manual demo script for fetching all INFY data."""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openscreener import Stock


def main() -> int:
    stock = Stock("JIOFIN", consolidated=True)
    stock.pretty()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
