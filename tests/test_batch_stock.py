from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from tests._support import FakeScraper, load_full_html
from openscreener.batch_stock import BatchStock
from openscreener.scraper import PlaywrightScraper


class BatchStockTestCase(unittest.TestCase):
    def test_post_init_normalizes_symbols_and_defaults_scraper(self) -> None:
        batch = BatchStock(["tcs", "infy"], consolidated=True)

        self.assertEqual(batch.symbols, ["TCS", "INFY"])
        self.assertIsInstance(batch.scraper, PlaywrightScraper)
        self.assertTrue(batch.consolidated)
        self.assertTrue(batch.scraper.consolidated)

    def test_fetch_single_section_returns_flat_payload(self) -> None:
        page_html = load_full_html()
        scraper = FakeScraper({"TCS": page_html, "INFY": page_html})
        batch = BatchStock(["tcs", "infy"], scraper=scraper)

        payload = batch.fetch("summary")

        self.assertEqual(sorted(payload.keys()), ["INFY", "TCS"])
        self.assertEqual(payload["TCS"]["company_name"], "Tata Consultancy Services Ltd")

    def test_fetch_multiple_sections_returns_nested_payload(self) -> None:
        scraper = FakeScraper({"TCS": load_full_html()})
        batch = BatchStock(["tcs"], scraper=scraper)

        payload = batch.fetch(["summary", "ratios"])

        self.assertIn("summary", payload["TCS"])
        self.assertIn("ratios", payload["TCS"])

    def test_fetch_uses_shared_scraper_page_map(self) -> None:
        scraper = MagicMock()
        scraper.fetch_pages.return_value = {"TCS": "<html></html>"}
        batch = BatchStock(["tcs"], scraper=scraper)

        with self.assertRaises(KeyError):
            batch.fetch("missing")

        scraper.fetch_pages.assert_called_once_with(["TCS"])
