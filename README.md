# openscreener

`openscreener` is a Python package for extracting structured financial data from [Screener.in](https://www.screener.in/). It uses Playwright to load live company and index pages and parser modules to turn Screener sections into normalized Python dictionaries and lists.

The package is built around three public entry points:

- `Stock` for single-company access
- `Index` for single-index access
- `BatchStock` for fetching one or more sections across multiple symbols
- `PlaywrightScraper` for live page loading

## Features

- Extracts structured data for stock summary, analysis, peers, quarterly results, profit and loss, balance sheet, cash flow, ratios, and shareholding
- Extracts structured index summary and constituents data
- Uses a high-level `Stock` API with one method per Screener section
- Supports live scraping through Playwright
- Includes JSON export, pretty terminal output, and optional pandas DataFrame conversion
- Provides a batch API for fetching the same section set across multiple stocks

## Installation

`openscreener` requires Python 3.10 or newer.

Install from PyPI:

```bash
pip install openscreener
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
from openscreener import Index, Stock

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

index = Index("NIFTY")
print(index.summary()["company_name"])
print(index.constituents(limit=5)["returned_companies"])
```

Export everything as JSON:

```python
from openscreener import Stock

stock = Stock("TCS")
print(stock.to_json())
```

Fetch an index and limit the returned constituents:

```python
from openscreener import Index

index = Index("NIFTY")

print(index.page_type())  # index
print(index.available_sections())  # ['summary', 'constituents']

payload = index.all(constituents_limit=10)
print(payload["summary"]["company_name"])
print(payload["constituents"]["returned_companies"])

index.pretty(constituents_limit=10)
```

## API Reference

### Imports

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
- `pretty(section=None)`
- `print_section(section)`
- `to_json(indent=2)`
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

Batch constructor:

```python
Stock.batch(
    symbols,
    scraper: PlaywrightScraper | None = None,
    consolidated: bool = False,
)
```

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

Stock page sections:

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

Index page sections:

| Canonical section | Accepted aliases | Index method | Return shape |
| --- | --- | --- | --- |
| `summary` | `summary` | `summary()` | `dict` |
| `constituents` | `constituents`, `companies` | `constituents(limit=None)` | `dict` |

Helper-only section names supported by `pretty()`, `print_section()`, and `to_dataframe()`:

- `pros`
- `cons`
- `shareholding_quarterly`
- `shareholding_yearly`

## API Notes

- `stock.page_type()` returns `stock`, `index`, or `unknown`
- `Index("NIFTY")` is the preferred public API for index pages
- `Stock("NIFTY")` now raises a helpful error telling you to use `Index("NIFTY")`
- `stock.fetch("ratios")` returns `{"ratios": {...}}`
- `stock.all()` fetches every stock section
- `index.all(constituents_limit=10)` limits index constituents in the output
- `stock.available_sections()` returns stock section names, while `index.available_sections()` returns index section names
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

- `base_url="https://www.screener.in/company/{symbol}{path_suffix}"`
- `consolidated=False`
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
tests/                    Automated tests
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
