# openscreener

`openscreener` is a small Python package scaffold for building stock screening
workflows.

## Project layout

```text
openscreener/
├── src/
│   └── openscreener/
│       ├── __init__.py
│       └── screener.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

```bash
pip install -e .
```

## Usage

```python
from openscreener import Screener, Stock

stocks = [
    Stock(symbol="AAA", price=120.0, volume=2_500_000, pe_ratio=18.4),
    Stock(symbol="BBB", price=45.0, volume=900_000, pe_ratio=31.2),
]

screener = Screener(stocks)
results = screener.filter(
    min_price=50.0,
    min_volume=1_000_000,
    max_pe_ratio=25.0,
)

print([stock.symbol for stock in results])
```

## Development

```bash
pytest
```
