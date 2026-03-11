# openscreener

`openscreener` is a Playwright-powered Python library for extracting structured financial data from [Screener.in](https://www.screener.in/).

It loads live stock and index pages, detects the page type, and returns normalized Python dictionaries and lists for the sections you care about.

## Highlights

- High-level APIs for single stocks, indexes, and batch stock fetches
- Normalized outputs for summary, analysis, peers, quarterly results, profit and loss, balance sheet, cash flow, ratios, and shareholding
- Index support with constituent pagination handling
- Pretty terminal output, JSON export, and optional pandas DataFrame conversion
- Helpful errors when a section is missing or the wrong class is used for a page

## Installation

`openscreener` requires Python `3.10+`.

Install the package:

```bash
pip install openscreener
```

Install Playwright browser binaries:

```bash
python -m playwright install chromium
```

Install pandas if you want `to_dataframe()` support:

```bash
pip install pandas
```

Install development dependencies when working on the repo:

```bash
pip install -e .[dev]
```

## Quick Start

### Stock

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

stock.pretty("summary")
stock.pretty("cash_flow")
print(stock.metadata())
```

### Index

```python
from openscreener import Index

index = Index("CNX500")

print(index.page_type())  # index
print(index.summary()["company_name"])

constituents = index.constituents(limit=70)
print(constituents["returned_companies"])
print(constituents["companies"][0]["symbol"])

index.pretty("constituents", constituents_limit=20)
```

### Batch

```python
from openscreener import Stock

batch = Stock.batch(["TCS", "INFY"])

ratios_by_symbol = batch.fetch("ratios")
print(ratios_by_symbol["TCS"]["roce_percent"])

payload_by_symbol = batch.fetch(["summary", "shareholding"])
print(payload_by_symbol["INFY"]["summary"]["company_name"])
```

### JSON And DataFrame Helpers

```python
from openscreener import Stock

stock = Stock("TCS")

print(stock.to_json())

frame = stock.to_dataframe("peers")
print(frame.head())
```

## Public API

```python
from openscreener import BatchStock, Index, PlaywrightScraper, Stock
```

### `Stock`

```python
Stock(symbol: str, consolidated: bool = False, scraper: PlaywrightScraper | None = None)
```

Main methods:

- `summary()`
- `pros_cons()`
- `pros()`
- `cons()`
- `peers()`
- `quarterly_results()`
- `profit_loss()`
- `balance_sheet()`
- `cash_flow()`
- `ratios()`
- `shareholding(frequency="quarterly")`
- `shareholding_quarterly()`
- `shareholding_yearly()`
- `fetch(sections, constituents_limit=None)`
- `all()`
- `available_sections()`
- `page_type()`
- `is_stock()`
- `is_index()`
- `pretty(section=None, constituents_limit=None)`
- `print_section(section, constituents_limit=None)`
- `to_json(indent=2, constituents_limit=None)`
- `to_dataframe(section)`
- `metadata()`

### `Index`

```python
Index(symbol: str, scraper: PlaywrightScraper | None = None)
```

Main methods:

- `summary()`
- `constituents(limit=None)`
- `fetch(sections, constituents_limit=None)`
- `all(constituents_limit=None)`
- `available_sections()`
- `page_type()`
- `pretty(section=None, constituents_limit=None)`
- `print_section(section, constituents_limit=None)`
- `to_json(indent=2, constituents_limit=None)`
- `to_dataframe(section)`
- `metadata()`

### `BatchStock`

```python
BatchStock(
    symbols,
    consolidated: bool = False,
    scraper: PlaywrightScraper | None = None,
)
```

Main method:

- `fetch(sections)`

Shortcut constructor:

```python
from openscreener import Stock

batch = Stock.batch(["TCS", "INFY"])
```

### `PlaywrightScraper`

```python
PlaywrightScraper(
    base_url="https://www.screener.in/company/{symbol}{path_suffix}",
    consolidated=False,
    headless=True,
    timeout_ms=30000,
)
```

Main methods:

- `fetch_page(symbol)`
- `fetch_pages(symbols)`
- `fetch_constituent_pages(symbol, page_numbers, page_size=50)`

## Supported Sections

### Stock Sections

| Canonical section | Accepted aliases | Method | Return shape |
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

### Index Sections

| Canonical section | Accepted aliases | Method | Return shape |
| --- | --- | --- | --- |
| `summary` | `summary` | `summary()` | `dict` |
| `constituents` | `constituents`, `companies` | `constituents(limit=None)` | `dict` |

### Helper-Only Section Names

These work with `pretty()`, `print_section()`, and `to_dataframe()` where applicable:

- `pros`
- `cons`
- `shareholding_quarterly`
- `shareholding_yearly`

## Behavior Notes

- `Stock("TCS")` is for stock pages.
- `Index("CNX500")` or `Index("NIFTY")` is for index pages.
- `page_type()` returns `stock`, `index`, or `unknown`.
- Using the wrong class for a page raises `EntityTypeMismatchError`.
- `available_sections()` depends on whether the resolved page is a stock or an index.
- `stock.fetch("ratios")` returns `{"ratios": {...}}`.
- `index.all(constituents_limit=100)` limits the returned constituent rows in the payload.
- `summary()["ratios"]` contains top-card metrics such as market cap, current price, high/low, and similar values.
- `ratios()` returns the latest annual ratios row, not the whole historical ratios table.
- `shareholding()` defaults to quarterly data.
- `metadata()` returns source metadata such as symbol, entity type, currency, units, and company or index name when available.

## Output Helpers

Pretty-print one section or the full payload:

```python
from openscreener import Stock

stock = Stock("TCS")

stock.pretty()
stock.pretty("summary")
stock.print_section("pros")
```

Index pretty-printing works the same way:

```python
from openscreener import Index

index = Index("CNX500")
index.pretty("constituents", constituents_limit=50)
```

If `pandas` is installed, you can convert tabular sections to DataFrames:

```python
from openscreener import Stock

stock = Stock("TCS")
frame = stock.to_dataframe("cash_flow")
print(frame.head())
```

If `pandas` is not installed, `to_dataframe()` raises an `ImportError` with an install hint.

## Data Conventions

- Numeric values are converted to `int` or `float` where possible.
- Missing values are returned as `None`.
- Period labels remain strings such as `Dec 2025`, `Mar 2025`, or `TTM`.
- Monetary values and units follow Screener's presentation.
- Default metadata reports `INR` currency and `crores` units.

## Development

Repository layout:

```text
src/openscreener/         Package source
src/openscreener/parsers/ Section parsers
tests/                    Automated tests
```

Run the local checks:

```bash
python -m pytest -q
python -m build --no-isolation
python -m twine check dist/*
```

## Releasing A New Version

1. Bump the version in `pyproject.toml`.
2. Run the test and build checks.
3. Upload the new distribution files.

```bash
python -m pytest -q
python -m build --no-isolation
python -m twine check dist/*
python -m twine upload dist/*
```

Each PyPI upload must use a new version number.

## Limitations

- Parsing depends on Screener.in's current HTML structure.
- Live usage requires Playwright and installed browser binaries.
- Missing sections raise `SectionNotFoundError`.
- Large index fetches depend on Screener's pagination remaining accessible.
- The project exposes a Python API; it does not currently provide a packaged CLI.

Use the live scraper responsibly and in a way that respects Screener.in's terms and rate limits.

## License

MIT. See [`LICENSE`](./LICENSE).
