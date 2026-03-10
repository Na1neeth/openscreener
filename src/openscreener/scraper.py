"""HTML loaders for live usage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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

    def _load_page(self, page, symbol: str) -> None:
        page.goto(self._build_url(symbol), wait_until="domcontentloaded", timeout=self.timeout_ms)
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("#top", timeout=self.timeout_ms)

    def _build_url(self, symbol: str) -> str:
        path_suffix = "/consolidated/" if self.consolidated else "/"
        return self.base_url.format(symbol=symbol.upper(), path_suffix=path_suffix)
