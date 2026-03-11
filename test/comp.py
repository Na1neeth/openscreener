from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rich.console import Console
from rich.table import Table

from openscreener import Stock


FIELDS = [
    ("equity_capital", "Equity Capital"),
    ("reserves", "Reserves"),
    ("borrowings", "Borrowings"),
    ("other_liabilities", "Other Liabilities"),
    ("total_liabilities", "Total Liabilities"),
    ("fixed_assets", "Fixed Assets"),
    ("capital_work_in_progress", "CWIP"),
    ("investments", "Investments"),
    ("other_assets", "Other Assets"),
    ("total_assets", "Total Assets"),
]


def format_value(value: object) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


def latest_balance_sheet(symbol: str) -> tuple[str, dict[str, object]]:
    stock = Stock(symbol)
    records = stock.balance_sheet()
    if not records:
        raise ValueError(f"No balance sheet data found for {symbol}.")
    summary = stock.summary()
    name = str(summary.get("company_name") or symbol.upper())
    return name, records[-1]


def main() -> int:
    left_name, left = latest_balance_sheet("PNB")
    right_name, right = latest_balance_sheet("HDFCBANK")

    left_period = str(left.get("year") or "Latest")
    right_period = str(right.get("year") or "Latest")

    console = Console()
    table = Table(title="Balance Sheet Comparison")
    table.add_column("Metric", style="bold cyan")
    table.add_column(f"{left_name} ({left_period})", justify="right")
    table.add_column(f"{right_name} ({right_period})", justify="right")

    for key, label in FIELDS:
        table.add_row(label, format_value(left.get(key)), format_value(right.get(key)))

    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
