# PROJECT_SPEC.md

## Overview

This project is a **Python package that extracts structured financial data from Screener.in using Playwright**.

The package provides a **clean, agent-friendly API** for retrieving financial data for Indian stocks.

Example usage:

```python
from screener import Stock

tcs = Stock("TCS")

data = tcs.fetch([
    "summary",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "ratios"
])
```

Example output:

```python
{
  "summary": {...},
  "profit_loss": [...],
  "balance_sheet": [...],
  "cash_flow": [...],
  "ratios": {...}
}
```

## Core Principles

1. Use **Playwright for page loading**
2. Extract data using **HTML parsing**
3. Parse specific **`<section id="...">` blocks**
4. Return **structured Python data**
5. Be **easy for AI agents to use**

## Supported Sections

The scraper extracts data from the following HTML sections:

| Section ID | Data |
|---|---|
| analysis | Pros / Cons |
| quarters | Quarterly Results |
| profit-loss | Profit & Loss |
| balance-sheet | Balance Sheet |
| cash-flow | Cash Flow |
| ratios | Financial Ratios |
| shareholding | Shareholding Pattern |

## Project Structure

```text
project/

src/
    stock.py
    batch_stock.py
    scraper.py

    parsers/
        summary_parser.py
        pros_cons_parser.py
        peers_parser.py
        quarterly_parser.py
        profit_loss_parser.py
        balance_sheet_parser.py
        cash_flow_parser.py
        ratios_parser.py
        shareholding_parser.py

examples/
    html/
        tcs/
            summary.html
            pros_cons.html
            peers.html
            quarterly_results.html
            profit_loss.html
            balance_sheet.html
            cash_flow.html
            ratios.html
            shareholding.html

docs/
    PROJECT_SPEC.md
```

Each example HTML file contains **only one `<section>` block**.

Example:

```html
<section id="profit-loss">
...
</section>
```

## Playwright Scraper

The scraper must:

1. Launch Playwright
2. Open:

```text
https://www.screener.in/company/{symbol}/
```

Example:

```text
https://www.screener.in/company/TCS/
```

3. Wait for page load
4. Extract HTML
5. Pass HTML to parsers

Example:

```python
html = await page.content()
```

## Stock API

Create a stock object:

```python
stock = Stock("TCS")
```

## Core Methods

### Summary

Returns general company data.

```python
stock.summary()
```

### Pros / Cons

Source section:

```html
<section id="analysis">
```

Returns:

```python
{
  "pros": [...],
  "cons": [...]
}
```

### Quarterly Results

Source section:

```html
<section id="quarters">
```

Returns:

```python
[
  {
    "date": "Dec 2025",
    "sales": 55567,
    "expenses": 39873,
    "operating_profit": 15694,
    "net_profit": 10190,
    "eps": 28.16
  }
]
```

### Profit & Loss

Source section:

```html
<section id="profit-loss">
```

Returns yearly financials.

Example:

```python
[
  {
    "year": "Mar 2025",
    "sales": 214853,
    "expenses": 156924,
    "operating_profit": 57929,
    "net_profit": 48057,
    "eps": 132.82
  }
]
```

### Balance Sheet

Source section:

```html
<section id="balance-sheet">
```

Returns:

```python
[
  {
    "year": "Mar 2025",
    "equity_capital": 362,
    "reserves": 75255,
    "borrowings": 7577,
    "total_assets": 132586
  }
]
```

### Cash Flow

Source section:

```html
<section id="cash-flow">
```

Returns:

```python
[
  {
    "year": "Mar 2025",
    "operating_cash_flow": 40816,
    "investing_cash_flow": 4874,
    "financing_cash_flow": -46724,
    "net_cash_flow": -1034
  }
]
```

### Ratios

Source section:

```html
<section id="ratios">
```

Returns:

```python
{
  "debtor_days": 88,
  "working_capital_days": 31,
  "roce_percent": 78
}
```

### Shareholding

Source section:

```html
<section id="shareholding">
```

Quarterly output:

```python
[
  {
    "date": "Dec 2025",
    "promoters": 71.77,
    "fiis": 10.37,
    "diis": 12.81,
    "government": 0.06,
    "public": 4.98
  }
]
```

## Universal Fetch Method

Agent-friendly method.

```python
stock.fetch(["profit_loss","ratios"])
```

Returns:

```python
{
 "profit_loss": [...],
 "ratios": {...}
}
```

## Fetch All Data

```python
stock.all()
```

Returns all supported sections.

## Available Sections

```python
stock.available_sections()
```

Example:

```python
[
 "analysis",
 "quarters",
 "profit-loss",
 "balance-sheet",
 "cash-flow",
 "ratios",
 "shareholding"
]
```

## Batch Stock Fetching

Fetch data for multiple stocks.

Create batch:

```python
stocks = Stock.batch(["TCS","INFY","WIPRO"])
```

### Fetch Same Section for Many Stocks

```python
stocks.fetch("ratios")
```

Output:

```python
{
 "TCS": {...},
 "INFY": {...},
 "WIPRO": {...}
}
```

### Fetch Multiple Sections

```python
stocks.fetch([
 "profit_loss",
 "ratios",
 "shareholding"
])
```

Output:

```python
{
 "TCS": {...},
 "INFY": {...},
 "WIPRO": {...}
}
```

## Performance Requirements

Batch scraping must:

- reuse a single Playwright browser
- reuse page contexts
- avoid reopening browser for every stock

Correct approach:

```text
launch browser
scrape TCS
scrape INFY
scrape WIPRO
close browser
```

## Data Format Rules

Return only structured data:

Allowed:

```text
dict
list
float
int
str
None
```

Avoid returning raw HTML unless explicitly requested.

## Agent-Friendly Design Rules

The API must be:

- simple
- predictable
- modular
- JSON-like

Example agent usage:

```python
stocks = Stock.batch(["TCS","INFY"])

data = stocks.fetch(["ratios","profit_loss"])
```

## Future Extensions

Possible extensions:

- peer comparison
- historical financial growth
- technical indicators
- multi-market support
