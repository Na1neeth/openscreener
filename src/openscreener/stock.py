"""Public stock API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .parsers import (
    parse_balance_sheet,
    parse_cash_flow,
    parse_peers,
    parse_profit_loss,
    parse_pros_cons,
    parse_quarterly_results,
    parse_ratios,
    parse_shareholding,
    parse_summary,
)
from .scraper import PlaywrightScraper, StaticScraper

_SECTION_ALIASES = {
    "summary": "summary",
    "analysis": "analysis",
    "pros_cons": "analysis",
    "peers": "peers",
    "quarters": "quarterly_results",
    "quarterly_results": "quarterly_results",
    "profit-loss": "profit_loss",
    "profit_loss": "profit_loss",
    "balance-sheet": "balance_sheet",
    "balance_sheet": "balance_sheet",
    "cash-flow": "cash_flow",
    "cash_flow": "cash_flow",
    "ratios": "ratios",
    "shareholding": "shareholding",
}
_ALL_SECTIONS = [
    "summary",
    "analysis",
    "peers",
    "quarterly_results",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "ratios",
    "shareholding",
]


@dataclass(slots=True)
class Stock:
    """High-level API for one Screener company."""

    symbol: str
    scraper: PlaywrightScraper | StaticScraper | None = None
    page_html: str | None = None

    def __post_init__(self) -> None:
        self.symbol = self.symbol.upper()
        if self.scraper is None:
            self.scraper = PlaywrightScraper()

    @classmethod
    def from_html(cls, symbol: str, html: str) -> "Stock":
        return cls(symbol=symbol, page_html=html, scraper=StaticScraper())

    @classmethod
    def from_sections(cls, symbol: str, sections: dict[str, str]) -> "Stock":
        return cls(symbol=symbol, scraper=StaticScraper(sections={symbol.upper(): sections}))

    @classmethod
    def batch(cls, symbols: Iterable[str], scraper: PlaywrightScraper | StaticScraper | None = None):
        from .batch_stock import BatchStock

        return BatchStock(list(symbols), scraper=scraper)

    def summary(self) -> dict[str, object]:
        return parse_summary(self._get_page_html())

    def pros_cons(self) -> dict[str, list[str]]:
        return parse_pros_cons(self._get_page_html())

    def peers(self) -> dict[str, object]:
        return parse_peers(self._get_page_html())

    def quarterly_results(self) -> list[dict[str, object]]:
        return parse_quarterly_results(self._get_page_html())

    def profit_loss(self) -> list[dict[str, object]]:
        return parse_profit_loss(self._get_page_html())

    def balance_sheet(self) -> list[dict[str, object]]:
        return parse_balance_sheet(self._get_page_html())

    def cash_flow(self) -> list[dict[str, object]]:
        return parse_cash_flow(self._get_page_html())

    def ratios(self) -> dict[str, object]:
        return parse_ratios(self._get_page_html())

    def shareholding(self, *, frequency: str = "quarterly") -> list[dict[str, object]]:
        return parse_shareholding(self._get_page_html(), frequency=frequency)

    def fetch(self, sections: str | Iterable[str]) -> dict[str, object]:
        requested = [sections] if isinstance(sections, str) else list(sections)
        results: dict[str, object] = {}
        for raw_name in requested:
            section = self._canonical_section(raw_name)
            if section == "summary":
                results[section] = self.summary()
            elif section == "analysis":
                results[section] = self.pros_cons()
            elif section == "peers":
                results[section] = self.peers()
            elif section == "quarterly_results":
                results[section] = self.quarterly_results()
            elif section == "profit_loss":
                results[section] = self.profit_loss()
            elif section == "balance_sheet":
                results[section] = self.balance_sheet()
            elif section == "cash_flow":
                results[section] = self.cash_flow()
            elif section == "ratios":
                results[section] = self.ratios()
            elif section == "shareholding":
                results[section] = self.shareholding()
        return results

    def all(self) -> dict[str, object]:
        return self.fetch(_ALL_SECTIONS)

    def available_sections(self) -> list[str]:
        return list(_ALL_SECTIONS)

    def _canonical_section(self, name: str) -> str:
        key = name.strip().lower()
        if key not in _SECTION_ALIASES:
            raise KeyError(f"Unsupported section '{name}'.")
        return _SECTION_ALIASES[key]

    def _get_page_html(self) -> str:
        if self.page_html is None:
            self.page_html = self.scraper.fetch_page(self.symbol)
        return self.page_html
