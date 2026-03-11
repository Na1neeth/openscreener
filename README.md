# openscreener

`openscreener` is a Python package for extracting structured financial data from [Screener.in](https://www.screener.in/). It uses Playwright to load live stock and index pages and parser modules to convert Screener sections into normalized Python dictionaries and lists.

The public API is built around four entry points:

- `Stock` for one stock page
- `Index` for one index page
- `BatchStock` for fetching the same sections across many stocks
- `PlaywrightScraper` for live page loading

## Features

- Extracts stock summary, analysis, peers, quarterly results, profit and loss, balance sheet, cash flow, ratios, and shareholding
- Extracts index summary and constituents data
- Supports pretty terminal output and JSON export
- Supports pandas DataFrame conversion for tabular sections
- Supports batch fetching across multiple stock symbols
- Handles index constituent pagination across multiple Screener pages

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

Install development dependencies:

```bash
pip install -e .[dev]
```

Install pandas if you want `to_dataframe()` support:

```bash
pip install pandas
```

## Quick Start

### Stock example

```python
from openscreener import Stock

stock = Stock("TCS")

print(stock.summary()["company_name"])
print(stock.summary()["current_price"])
print(stock.summary()["ratios"]["market_cap"])

analysis = stock.pros_cons()
print(analysis["pros"][0])

payload = stock.fetch(["summary", "ratios", "shareholding"])
print(payload["ratios"]["roce_percent"])

stock.pretty("summary")
stock.pretty("cash_flow")
```

### Index example

```python
from openscreener import Index

index = Index("CNX500")

print(index.page_type())  # index
print(index.summary()["company_name"])

payload = index.constituents(limit=70)
print(payload["returned_companies"])

index.pretty("constituents", constituents_limit=70)
```

### Batch example

```python
from openscreener import Stock

batch = Stock.batch(["TCS", "INFY"])
payload = batch.fetch("summary")

print(payload["TCS"]["company_name"])
print(payload["INFY"]["company_name"])
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

You can also construct it through:

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

### Stock sections

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

### Index sections

| Canonical section | Accepted aliases | Method | Return shape |
| --- | --- | --- | --- |
| `summary` | `summary` | `summary()` | `dict` |
| `constituents` | `constituents`, `companies` | `constituents(limit=None)` | `dict` |

### Helper-only section names

These work with `pretty()`, `print_section()`, and `to_dataframe()` where applicable:

- `pros`
- `cons`
- `shareholding_quarterly`
- `shareholding_yearly`

## API Notes

- `Stock("TCS")` is for stock pages
- `Index("CNX500")` or `Index("NIFTY")` is for index pages
- `page_type()` returns `stock`, `index`, or `unknown`
- `available_sections()` depends on whether the page is a stock or index
- `stock.fetch("ratios")` returns `{"ratios": {...}}`
- `index.all(constituents_limit=100)` limits the returned constituents in the payload
- `summary()["ratios"]` contains top-card metrics such as market cap, current price, high/low, and similar values
- `ratios()` returns the latest annual ratios row, not the whole historical ratios table
- `shareholding()` defaults to quarterly shareholding data
- `metadata()` returns source metadata such as symbol, entity type, currency, units, and company/index name when available

## Batch Fetching

Use `BatchStock` when you want the same sections for multiple stock symbols.

```python
from openscreener import Stock

batch = Stock.batch(["TCS", "INFY"])

ratios_by_symbol = batch.fetch("ratios")
print(ratios_by_symbol["TCS"]["roce_percent"])

payload_by_symbol = batch.fetch(["summary", "shareholding"])
print(payload_by_symbol["INFY"]["summary"]["company_name"])
```

Behavior:

- If you request one section, each symbol maps directly to that section payload
- If you request multiple sections, each symbol maps to a nested section dictionary

## Output Helpers

Pretty print one section or the full payload:

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

Convert a section to a pandas DataFrame:

```python
from openscreener import Stock

stock = Stock("TCS")
frame = stock.to_dataframe("peers")
print(frame.head())
```

If pandas is not installed, `to_dataframe()` raises an `ImportError`.

## Data Conventions

- Numeric values are converted to `int` or `float` where possible
- Missing values are returned as `None`
- Period labels stay as strings such as `Dec 2025`, `Mar 2025`, or `TTM`
- Monetary values and units follow Screener's presentation
- Default metadata uses `INR` and `crores`

## Manual Test Scripts

The repository also contains simple manual scripts under [`test/`](/home/navaneeth/Desktop/openscreener/test):

- [nifty.py](/home/navaneeth/Desktop/openscreener/test/nifty.py) for manual index testing
- [qa.py](/home/navaneeth/Desktop/openscreener/test/qa.py) to pretty print a chosen number of `CNX500` constituents
- [qa_one.py](/home/navaneeth/Desktop/openscreener/test/qa_one.py) to print one constituent by position
- [batch.py](/home/navaneeth/Desktop/openscreener/test/batch.py) for a minimal `BatchStock` example

Examples:

```bash
python test/qa.py 70
python test/qa_one.py 22
python test/batch.py
```

## Development

Key repository paths:

```text
src/openscreener/         Package source
src/openscreener/parsers/ Section parsers
tests/                    Automated tests
test/                     Manual helper scripts
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

## Limitations

- Parsing depends on Screener.in's current HTML structure
- Live scraping requires Playwright and installed browser binaries
- Missing sections raise `SectionNotFoundError`
- Very large indexes depend on Screener's live pagination remaining accessible
- The project exposes a Python API; it does not currently provide a packaged CLI

Use the live scraper responsibly and in a way that respects Screener.in's terms and rate limits.

## License

MIT. See [`LICENSE`](./LICENSE).
