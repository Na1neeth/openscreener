# openscreener

`openscreener` is a Python package for extracting structured financial data from [Screener.in](https://www.screener.in/). It uses Playwright to load live company pages and parser modules to turn Screener sections into normalized Python dictionaries and lists.

The package is built around four public entry points:

- `Stock` for single-company access
- `BatchStock` for fetching one or more sections across multiple symbols
- `PlaywrightScraper` for live page loading
- `StaticScraper` for offline parsing from saved HTML fixtures

## Features

- Extracts structured data for summary, analysis, peers, quarterly results, profit and loss, balance sheet, cash flow, ratios, and shareholding
- Uses a high-level `Stock` API with one method per Screener section
- Supports live scraping and offline fixture-based development
- Includes JSON export, pretty terminal output, and optional pandas DataFrame conversion
- Provides a batch API for fetching the same section set across multiple stocks

## Installation

`openscreener` requires Python 3.10 or newer.

Install the package:

```bash
pip install -e .
```

Install Playwright browser binaries for live scraping:

```bash
python -m playwright install chromium
```

Install development dependencies:

```bash
pip install -e .[dev]
```

Install pandas if you want `to_dataframe()` support:

```bash
pip install pandas
```

## Quick Start

`Stock(symbol)` uses the live Playwright scraper by default.

```python
from openscreener import Stock

stock = Stock("TCS")

summary = stock.summary()
print(summary["company_name"])
print(summary["current_price"])
print(summary["ratios"]["market_cap"])

analysis = stock.pros_cons()
print(analysis["pros"][0])

payload = stock.fetch(["summary", "ratios", "shareholding"])
print(payload["ratios"]["roce_percent"])

stock.pretty("cash_flow")
```

Export everything as JSON:

```python
from openscreener import Stock

stock = Stock("TCS")
print(stock.to_json())
```

## Supported Sections

These names work with `Stock.fetch(...)`:

| Canonical section | Accepted aliases | Stock method | Return shape |
| --- | --- | --- | --- |
| `summary` | `summary` | `summary()` | `dict` |
| `analysis` | `analysis`, `pros_cons` | `pros_cons()` | `dict` |
| `peers` | `peers` | `peers()` | `dict` |
| `quarterly_results` | `quarters`, `quarterly_results` | `quarterly_results()` | `list[dict]` |
| `profit_loss` | `profit-loss`, `profit_loss` | `profit_loss()` | `list[dict]` |
| `balance_sheet` | `balance-sheet`, `balance_sheet` | `balance_sheet()` | `list[dict]` |
| `cash_flow` | `cash-flow`, `cash_flow` | `cash_flow()` | `list[dict]` |
| `ratios` | `ratios` | `ratios()` | `dict` |
| `shareholding` | `shareholding` | `shareholding()` | `list[dict]` |

Helper-only section names supported by `pretty()`, `print_section()`, and `to_dataframe()`:

- `pros`
- `cons`
- `shareholding_quarterly`
- `shareholding_yearly`

## API Notes

- `stock.fetch("ratios")` returns `{"ratios": {...}}`
- `stock.all()` fetches every canonical section
- `stock.available_sections()` returns the supported canonical section names
- `stock.pros()` and `stock.cons()` return plain string lists from the analysis block
- `stock.shareholding()` defaults to quarterly data
- `stock.shareholding_yearly()` fetches yearly shareholding history
- `stock.metadata()` returns source metadata such as symbol, currency, units, and company name when available

## Batch Fetching

Use `Stock.batch(...)` when you want the same section set for multiple symbols.

```python
from openscreener import Stock

batch = Stock.batch(["TCS", "INFY"])

ratios_by_symbol = batch.fetch("ratios")
print(ratios_by_symbol["TCS"]["roce_percent"])

payload_by_symbol = batch.fetch(["summary", "shareholding"])
print(payload_by_symbol["INFY"]["summary"]["company_name"])
```

For a single requested section, `BatchStock.fetch(...)` returns one payload per symbol. For multiple sections, it returns a nested dictionary keyed by symbol and then section.

## Offline Fixtures and Parser Development

The repository includes saved section HTML under [`examples/html`](./examples/html) for offline development and parser testing.

Load them directly:

```python
from openscreener import PlaywrightScraper, Stock

scraper = PlaywrightScraper.from_fixture_directory("examples/html", symbol="TCS")
stock = Stock("TCS", scraper=scraper)

print(stock.summary()["company_name"])
print(stock.quarterly_results()[-1]["date"])
```

Or build a stock from section fragments:

```python
from pathlib import Path

from openscreener import Stock

fixture_dir = Path("examples/html")

stock = Stock.from_sections(
    "TCS",
    {
        "top": (fixture_dir / "summary.html").read_text(encoding="utf-8"),
        "analysis": (fixture_dir / "pros_cons.html").read_text(encoding="utf-8"),
        "peers": (fixture_dir / "peers.html").read_text(encoding="utf-8"),
        "quarters": (fixture_dir / "quarterly_results.html").read_text(encoding="utf-8"),
        "profit-loss": (fixture_dir / "profit_loss.html").read_text(encoding="utf-8"),
        "balance-sheet": (fixture_dir / "balance_sheet.html").read_text(encoding="utf-8"),
        "cash-flow": (fixture_dir / "cash_flow.html").read_text(encoding="utf-8"),
        "ratios": (fixture_dir / "ratios.html").read_text(encoding="utf-8"),
        "shareholding": (fixture_dir / "shareholding.html").read_text(encoding="utf-8"),
    },
)

print(stock.ratios()["year"])
```

## Data Conventions

- Numeric values are converted to `int` or `float` when possible
- Missing values are returned as `None`
- Period labels are preserved as strings such as `Dec 2025`, `Mar 2025`, or `TTM`
- Summary metrics from the Screener top card are exposed under `summary()["ratios"]`
- `ratios()` returns the latest available annual ratios row, not the full ratios history
- Monetary values and units follow Screener's presentation, with metadata defaulting to `INR` and `crores`

## Scraper Configuration

The live scraper can be customized:

```python
from openscreener import PlaywrightScraper, Stock

scraper = PlaywrightScraper(
    headless=False,
    timeout_ms=60000,
)

stock = Stock("TCS", scraper=scraper)
print(stock.summary()["company_name"])
```

`PlaywrightScraper` defaults to:

- `base_url="https://www.screener.in/company/{symbol}/"`
- `headless=True`
- `timeout_ms=30000`

## Output Helpers

Pretty print one section or the full payload:

```python
from openscreener import Stock

stock = Stock("TCS")
stock.pretty()
stock.print_section("pros")
```

Convert a section to a pandas DataFrame:

```python
from openscreener import Stock

stock = Stock("TCS")
frame = stock.to_dataframe("peers")
print(frame.head())
```

If pandas is not installed, `to_dataframe()` raises an `ImportError` with an installation hint.

## Development

Key repository paths:

```text
src/openscreener/         Package source
src/openscreener/parsers/ Section parsers
examples/html/            Offline Screener HTML fixtures
tests/                    Automated tests
docs/PROJECT_SPEC.md      High-level project spec
```

Run the test suite:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Limitations

- The parser depends on Screener.in's current HTML structure and section IDs
- Live scraping requires Playwright plus installed browser binaries
- Missing Screener sections raise `SectionNotFoundError`
- There is no CLI yet; the project currently exposes a Python API only

Use the live scraper responsibly and in a way that respects Screener.in's terms and rate limits.

## License

MIT. See [`LICENSE`](./LICENSE).
