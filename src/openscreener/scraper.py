"""HTML loaders for live usage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlencode

from .exceptions import OpenScreenerError


@dataclass(slots=True)
class PlaywrightScraper:
    """Live HTML loader that fetches Screener pages through Playwright."""

    base_url: str = "https://www.screener.in/company/{symbol}{path_suffix}"
    consolidated: bool = False
    headless: bool = True
    timeout_ms: int = 30000

    def fetch_page(self, symbol: str) -> str:
        with self._browser_session() as browser:
            page = browser.new_page()
            self._load_page(page, symbol)
            html = page.content()
            page.close()
            return html

    def fetch_pages(self, symbols: Iterable[str]) -> dict[str, str]:
        result: dict[str, str] = {}
        with self._browser_session() as browser:
            for symbol in symbols:
                page = browser.new_page()
                self._load_page(page, symbol)
                result[symbol.upper()] = page.content()
                page.close()
        return result

    def fetch_constituent_pages(
        self,
        symbol: str,
        *,
        page_numbers: Iterable[int],
        page_size: int = 50,
    ) -> list[str]:
        html_pages: list[str] = []
        with self._browser_session() as browser:
            for page_number in page_numbers:
                page = browser.new_page()
                self._load_page(page, symbol, page_number=page_number, page_size=page_size)
                html_pages.append(page.content())
                page.close()
        return html_pages

    def _browser_session(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise OpenScreenerError(
                "Playwright is not installed. Install project dependencies before using the live scraper."
            ) from exc

        manager = sync_playwright().start()
        browser = manager.chromium.launch(headless=self.headless)

        class _Session:
            def __enter__(self_inner):
                return browser

            def __exit__(self_inner, exc_type, exc, tb):
                browser.close()
                manager.stop()

        return _Session()

    def _load_page(self, page, symbol: str, *, page_number: int | None = None, page_size: int | None = None) -> None:
        page.goto(self._build_url(symbol, page_number=page_number, page_size=page_size), wait_until="domcontentloaded", timeout=self.timeout_ms)
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("#top", timeout=self.timeout_ms)

    def _build_url(self, symbol: str, *, page_number: int | None = None, page_size: int | None = None) -> str:
        path_suffix = "/consolidated/" if self.consolidated else "/"
        base_url = self.base_url.format(symbol=symbol.upper(), path_suffix=path_suffix)
        query: dict[str, int] = {}
        if page_number is not None:
            query["page"] = page_number
        if page_size is not None:
            query["limit"] = page_size
        if not query:
            return base_url
        return f"{base_url}?{urlencode(query)}"
