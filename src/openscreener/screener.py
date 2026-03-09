"""Simple stock screening utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stock:
    """Represents a single stock snapshot."""

    symbol: str
    price: float
    volume: int
    pe_ratio: float | None = None


class Screener:
    """Filters a collection of stocks against common criteria."""

    def __init__(self, stocks: list[Stock] | None = None) -> None:
        self._stocks = list(stocks or [])

    def add_stock(self, stock: Stock) -> None:
        """Add a stock to the in-memory screening universe."""

        self._stocks.append(stock)

    def filter(
        self,
        *,
        min_price: float | None = None,
        max_price: float | None = None,
        min_volume: int | None = None,
        max_pe_ratio: float | None = None,
    ) -> list[Stock]:
        """Return stocks matching the supplied numeric thresholds."""

        results: list[Stock] = []

        for stock in self._stocks:
            if min_price is not None and stock.price < min_price:
                continue
            if max_price is not None and stock.price > max_price:
                continue
            if min_volume is not None and stock.volume < min_volume:
                continue
            if (
                max_pe_ratio is not None
                and stock.pe_ratio is not None
                and stock.pe_ratio > max_pe_ratio
            ):
                continue

            results.append(stock)

        return results
