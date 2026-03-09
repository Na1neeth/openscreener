# openscreener

`openscreener` is a Python package for extracting structured financial data from
Screener.in. It uses Playwright for page loading and parser modules for turning
Screener sections into JSON-like Python data.

## Project layout

```text
openscreener/
├── docs/
│   └── PROJECT_SPEC.md
├── examples/
│   └── html/
│       ├── summary.html
│       ├── pros_cons.html
│       ├── peers.html
│       ├── quarterly_results.html
│       ├── profit_loss.html
│       ├── balance_sheet.html
│       ├── cash_flow.html
│       ├── ratios.html
│       ├── shareholding.html
│       └── peratio.html
├── src/
│   └── openscreener/
│       ├── __init__.py
│       ├── batch_stock.py
│       ├── scraper.py
│       ├── screener.py
│       ├── stock.py
│       └── parsers/
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

## Usage

```python
from openscreener import Stock

stock = Stock("TCS")
data = stock.fetch(
    [
        "summary",
        "analysis",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "ratios",
        "shareholding",
    ]
)
```

For offline development and parser testing, you can build a stock instance from
the example section HTML:

```bash
python -m unittest
```

```python
from pathlib import Path

from openscreener import Stock

fixture_dir = Path("examples/html")
sections = {
    "summary": (fixture_dir / "summary.html").read_text(),
    "analysis": (fixture_dir / "pros_cons.html").read_text(),
    "peers": (fixture_dir / "peers.html").read_text(),
    "quarters": (fixture_dir / "quarterly_results.html").read_text(),
    "profit-loss": (fixture_dir / "profit_loss.html").read_text(),
    "balance-sheet": (fixture_dir / "balance_sheet.html").read_text(),
    "cash-flow": (fixture_dir / "cash_flow.html").read_text(),
    "ratios": (fixture_dir / "ratios.html").read_text(),
    "shareholding": (fixture_dir / "shareholding.html").read_text(),
    "chart": (fixture_dir / "peratio.html").read_text(),
}

stock = Stock.from_sections("TCS", sections)
print(stock.summary()["company_name"])
```

## Notes

- Live page loading uses Playwright with lazy imports inside the scraper.
- The PE ratio fixture only contains chart controls and canvas markup, not the
  full underlying time-series data. The live scraper includes a tooltip-based
  fallback for PE history extraction.
