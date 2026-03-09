"""HTML loaders for live and offline usage."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

from .exceptions import MissingChartDataError, OpenScreenerError
from .parsers._helpers import build_fixture_page

_RANGE_TO_DAYS = {
    "1M": "30",
    "6M": "180",
    "1Y": "365",
    "3Y": "1095",
    "5Y": "1825",
    "10Y": "3652",
    "MAX": "10000",
}


@dataclass(slots=True)
class StaticScraper:
    """Simple in-memory scraper used for tests and offline fixture parsing."""

    pages: dict[str, str] = field(default_factory=dict)
    sections: dict[str, dict[str, str]] = field(default_factory=dict)

    def fetch_page(self, symbol: str) -> str:
        normalized = symbol.upper()
        if normalized in self.pages:
            return self.pages[normalized]
        if normalized in self.sections:
            return build_fixture_page(self.sections[normalized])
        raise OpenScreenerError(f"No HTML fixture registered for symbol '{normalized}'.")

    def fetch_pages(self, symbols: Iterable[str]) -> dict[str, str]:
        return {symbol.upper(): self.fetch_page(symbol) for symbol in symbols}

    def fetch_pe_ratio_history(self, symbol: str, range_label: str = "5Y") -> list[dict[str, object]]:
        return []


@dataclass(slots=True)
class PlaywrightScraper:
    """Live HTML loader that fetches Screener pages through Playwright."""

    base_url: str = "https://www.screener.in/company/{symbol}/"
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

    def fetch_pe_ratio_history(self, symbol: str, range_label: str = "5Y") -> list[dict[str, object]]:
        range_code = _RANGE_TO_DAYS[range_label.upper()]
        with self._browser_session() as browser:
            page = browser.new_page()
            self._load_page(page, symbol)
            page.locator("button[name='metrics'][value='Price to Earning-Median PE-EPS']").click()
            page.locator(f"button[name='days'][value='{range_code}']").click()
            page.wait_for_timeout(500)
            history = self._extract_chart_history(page)
            page.close()
        if not history:
            raise MissingChartDataError("Could not extract PE ratio history from the live chart.")
        return history

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
        page.goto(self.base_url.format(symbol=symbol.upper()), wait_until="domcontentloaded", timeout=self.timeout_ms)
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("#top", timeout=self.timeout_ms)

    def _extract_chart_history(self, page) -> list[dict[str, object]]:
        canvas = page.locator("#canvas-chart-holder canvas")
        if canvas.count() == 0:
            return []
        box = canvas.bounding_box()
        if box is None:
            return []
        x_start = box["x"] + 2
        x_end = box["x"] + box["width"] - 2
        y = box["y"] + (box["height"] / 2)
        samples: dict[str, dict[str, object]] = {}

        for step in range(50):
            x = x_start + ((x_end - x_start) * step / 49)
            page.mouse.move(x, y)
            page.wait_for_timeout(40)
            tooltip = self._read_tooltip(page)
            if tooltip is None:
                continue
            key = str(tooltip.get("date") or len(samples))
            samples[key] = tooltip

        return list(samples.values())

    def _read_tooltip(self, page) -> dict[str, object] | None:
        meta = page.locator("#chart-tooltip-meta").inner_text().strip()
        title = page.locator("#chart-tooltip-title").inner_text().strip()
        info = page.locator("#chart-tooltip-info").inner_text().strip()
        if not (meta or title or info):
            return None

        def _extract_value(label: str, text: str) -> float | None:
            match = re.search(rf"{label}[^0-9-]*(-?\d+(?:\.\d+)?)", text, re.IGNORECASE)
            if match is None:
                return None
            return float(match.group(1))

        combined = "\n".join(part for part in [title, info] if part)
        pe_ratio = _extract_value("PE", combined)
        median_pe = _extract_value("Median", combined)
        eps = _extract_value("EPS", combined)
        return {
            "date": meta or None,
            "pe_ratio": pe_ratio,
            "median_pe": median_pe,
            "eps": eps,
        }

    @classmethod
    def from_fixture_directory(cls, fixture_dir: str | Path, symbol: str = "TCS") -> StaticScraper:
        directory = Path(fixture_dir)
        section_files = {
            "top": (directory / "summary.html").read_text(encoding="utf-8"),
            "analysis": (directory / "pros_cons.html").read_text(encoding="utf-8"),
            "peers": (directory / "peers.html").read_text(encoding="utf-8"),
            "quarters": (directory / "quarterly_results.html").read_text(encoding="utf-8"),
            "profit-loss": (directory / "profit_loss.html").read_text(encoding="utf-8"),
            "balance-sheet": (directory / "balance_sheet.html").read_text(encoding="utf-8"),
            "cash-flow": (directory / "cash_flow.html").read_text(encoding="utf-8"),
            "ratios": (directory / "ratios.html").read_text(encoding="utf-8"),
            "shareholding": (directory / "shareholding.html").read_text(encoding="utf-8"),
            "chart": (directory / "peratio.html").read_text(encoding="utf-8"),
        }
        return StaticScraper(sections={symbol.upper(): section_files})
