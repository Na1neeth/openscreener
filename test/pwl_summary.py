"""Manual demo script for the Stock helper methods."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openscreener import Stock


def main() -> int:
    stock = Stock("PWL")

    stock.pretty()
    stock.print_section("quarterly_results")
    stock.print_section("profit_loss")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
