"""Batch stock fetching API."""

from __future__ import annotations

from dataclasses import dataclass

from .scraper import PlaywrightScraper, StaticScraper


@dataclass(slots=True)
class BatchStock:
    """Fetches one or more sections for multiple stocks."""

    symbols: list[str]
    scraper: PlaywrightScraper | StaticScraper | None = None

    def __post_init__(self) -> None:
        self.symbols = [symbol.upper() for symbol in self.symbols]
        if self.scraper is None:
            self.scraper = PlaywrightScraper()

    def fetch(self, sections: str | list[str]) -> dict[str, object]:
        from .stock import Stock

        is_single_section = isinstance(sections, str)
        requested = [sections] if is_single_section else list(sections)
        page_html_by_symbol = self.scraper.fetch_pages(self.symbols)

        results: dict[str, object] = {}
        for symbol in self.symbols:
            stock = Stock(symbol=symbol, scraper=self.scraper, page_html=page_html_by_symbol.get(symbol))
            payload = stock.fetch(requested)
            results[symbol] = payload[next(iter(payload))] if is_single_section else payload
        return results
