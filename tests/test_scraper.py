from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener.exceptions import OpenScreenerError
from openscreener.scraper import PlaywrightScraper


class PlaywrightScraperTestCase(unittest.TestCase):
    def test_load_page_uses_expected_navigation_sequence(self) -> None:
        page = MagicMock()
        scraper = PlaywrightScraper(timeout_ms=123, base_url="https://example.com/{symbol}{path_suffix}")

        scraper._load_page(page, "tcs")

        page.goto.assert_called_once_with("https://example.com/TCS/", wait_until="domcontentloaded", timeout=123)
        page.wait_for_load_state.assert_called_once_with("networkidle")
        page.wait_for_selector.assert_called_once_with("#top", timeout=123)

    def test_build_url_supports_consolidated_and_standalone(self) -> None:
        standalone = PlaywrightScraper(base_url="https://example.com/{symbol}{path_suffix}")
        consolidated = PlaywrightScraper(base_url="https://example.com/{symbol}{path_suffix}", consolidated=True)

        self.assertEqual(standalone._build_url("tcs"), "https://example.com/TCS/")
        self.assertEqual(consolidated._build_url("tcs"), "https://example.com/TCS/consolidated/")
        self.assertEqual(standalone._build_url("tcs", page_number=2, page_size=50), "https://example.com/TCS/?page=2&limit=50")

    def test_fetch_page_uses_browser_session(self) -> None:
        page = MagicMock()
        page.content.return_value = "<html>TCS</html>"
        browser = MagicMock()
        browser.new_page.return_value = page

        class Session:
            def __enter__(self):
                return browser

            def __exit__(self, exc_type, exc, tb):
                return None

        scraper = PlaywrightScraper()
        with patch.object(PlaywrightScraper, "_browser_session", return_value=Session()), patch.object(PlaywrightScraper, "_load_page") as load_page:
            html = scraper.fetch_page("tcs")

        self.assertEqual(html, "<html>TCS</html>")
        load_page.assert_called_once_with(page, "tcs")
        page.close.assert_called_once()

    def test_fetch_pages_returns_html_by_symbol(self) -> None:
        page_one = MagicMock()
        page_one.content.return_value = "<html>TCS</html>"
        page_two = MagicMock()
        page_two.content.return_value = "<html>INFY</html>"
        browser = MagicMock()
        browser.new_page.side_effect = [page_one, page_two]

        class Session:
            def __enter__(self):
                return browser

            def __exit__(self, exc_type, exc, tb):
                return None

        scraper = PlaywrightScraper()
        with patch.object(PlaywrightScraper, "_browser_session", return_value=Session()), patch.object(PlaywrightScraper, "_load_page") as load_page:
            payload = scraper.fetch_pages(["tcs", "infy"])

        self.assertEqual(payload, {"TCS": "<html>TCS</html>", "INFY": "<html>INFY</html>"})
        self.assertEqual(load_page.call_count, 2)
        page_one.close.assert_called_once()
        page_two.close.assert_called_once()

    def test_fetch_constituent_pages_returns_html_by_page(self) -> None:
        page_one = MagicMock()
        page_one.content.return_value = "<html>page-1</html>"
        page_two = MagicMock()
        page_two.content.return_value = "<html>page-2</html>"
        browser = MagicMock()
        browser.new_page.side_effect = [page_one, page_two]

        class Session:
            def __enter__(self):
                return browser

            def __exit__(self, exc_type, exc, tb):
                return None

        scraper = PlaywrightScraper()
        with patch.object(PlaywrightScraper, "_browser_session", return_value=Session()), patch.object(PlaywrightScraper, "_load_page") as load_page:
            payload = scraper.fetch_constituent_pages("nifty", page_numbers=[1, 2], page_size=50)

        self.assertEqual(payload, ["<html>page-1</html>", "<html>page-2</html>"])
        load_page.assert_any_call(page_one, "nifty", page_number=1, page_size=50)
        load_page.assert_any_call(page_two, "nifty", page_number=2, page_size=50)
        page_one.close.assert_called_once()
        page_two.close.assert_called_once()

    def test_browser_session_raises_helpful_error_without_playwright(self) -> None:
        scraper = PlaywrightScraper()
        original_sync_api = sys.modules.get("playwright.sync_api")
        original_playwright = sys.modules.get("playwright")
        sys.modules.pop("playwright.sync_api", None)
        sys.modules.pop("playwright", None)

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "playwright.sync_api":
                raise ImportError("missing")
            return original_import(name, globals, locals, fromlist, level)

        original_import = __import__
        with patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaisesRegex(OpenScreenerError, "Playwright is not installed"):
                scraper._browser_session()

        if original_playwright is not None:
            sys.modules["playwright"] = original_playwright
        if original_sync_api is not None:
            sys.modules["playwright.sync_api"] = original_sync_api

    def test_browser_session_closes_browser_and_manager(self) -> None:
        browser = MagicMock()
        manager = MagicMock()
        manager.chromium.launch.return_value = browser
        fake_sync_api = types.ModuleType("playwright.sync_api")
        fake_sync_api.sync_playwright = MagicMock(return_value=MagicMock(start=MagicMock(return_value=manager)))

        with patch.dict(sys.modules, {"playwright.sync_api": fake_sync_api, "playwright": types.ModuleType("playwright")}):
            session = PlaywrightScraper(headless=False)._browser_session()
            with session as active_browser:
                self.assertIs(active_browser, browser)

        manager.chromium.launch.assert_called_once_with(headless=False)
        browser.close.assert_called_once()
        manager.stop.assert_called_once()
