"""Test script to fetch all available stock data."""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openscreener import Stock


def print_section(name: str, payload: object) -> None:
    print(f"\n{name.upper()}")

    if isinstance(payload, dict):
        frame = pd.json_normalize(payload, sep="_")
        print(frame.to_string(index=False))
        return

    if isinstance(payload, list):
        frame = pd.DataFrame(payload)
        if frame.empty:
            print("No data")
        else:
            print(frame.to_string(index=False))
        return

    print(payload)


def main() -> int:
    stock = Stock("PWL")

    data = stock.all()

    for section_name, payload in data.items():
        print_section(section_name, payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
