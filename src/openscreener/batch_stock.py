"""Batch stock fetching API."""

from __future__ import annotations

from dataclasses import dataclass

from .scraper import PlaywrightScraper


@dataclass(slots=True)
class BatchStock:
    """Fetches one or more sections for multiple stocks."""

    symbols: list[str]
    consolidated: bool = False
    scraper: PlaywrightScraper | None = None

    def __post_init__(self) -> None:
        self.symbols = [symbol.upper() for symbol in self.symbols]
        if self.scraper is None:
            self.scraper = PlaywrightScraper(consolidated=self.consolidated)
        elif isinstance(self.scraper, PlaywrightScraper):
            self.consolidated = self.scraper.consolidated

    def fetch(self, sections: str | list[str]) -> dict[str, object]:
        from .stock import Stock

        is_single_section = isinstance(sections, str)
        requested = [sections] if is_single_section else list(sections)
        page_html_by_symbol = self.scraper.fetch_pages(self.symbols)

        results: dict[str, object] = {}
        for symbol in self.symbols:
            stock = Stock(
                symbol=symbol,
                consolidated=self.consolidated,
                scraper=self.scraper,
                page_html=page_html_by_symbol.get(symbol),
            )
            payload = stock.fetch(requested)
            results[symbol] = payload[next(iter(payload))] if is_single_section else payload
        return results
