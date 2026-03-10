from __future__ import annotations

import unittest

from tests._support import FakeScraper, load_full_html, load_index_html
from openscreener.exceptions import EntityTypeMismatchError, SectionNotFoundError
from openscreener.scraper import PlaywrightScraper
from openscreener.stock import Stock


class StockMethodsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.page_html = load_full_html()

    def test_constructors_normalize_symbol_and_defaults(self) -> None:
        stock = Stock("tcs", consolidated=True)

        self.assertEqual(stock.symbol, "TCS")
        self.assertIsInstance(stock.scraper, PlaywrightScraper)
        self.assertTrue(stock.consolidated)
        self.assertTrue(stock.scraper.consolidated)

    def test_batch_classmethod_returns_batch_stock(self) -> None:
        batch = Stock.batch(["tcs"], scraper=FakeScraper({"TCS": self.page_html}), consolidated=True)
        self.assertEqual(batch.symbols, ["TCS"])
        self.assertTrue(batch.consolidated)

    def test_stock_uses_scraper_consolidated_flag_when_scraper_is_provided(self) -> None:
        stock = Stock("tcs", scraper=PlaywrightScraper(consolidated=True))
        self.assertTrue(stock.consolidated)

    def test_available_sections_and_all_cover_public_sections(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        self.assertEqual(
            stock.available_sections(),
            ["summary", "analysis", "peers", "quarterly_results", "profit_loss", "balance_sheet", "cash_flow", "ratios", "shareholding"],
        )
        self.assertEqual(sorted(stock.all().keys()), sorted(stock.available_sections()))

    def test_fetch_supports_aliases(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))
        payload = stock.fetch(["profit-loss", "cash-flow", "quarters"])

        self.assertIn("profit_loss", payload)
        self.assertIn("cash_flow", payload)
        self.assertIn("quarterly_results", payload)

    def test_canonical_section_validation(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        self.assertEqual(stock._canonical_section(" profit-loss "), "profit_loss")
        self.assertEqual(stock._canonical_helper_section("shareholding-yearly"), "shareholding_yearly")
        with self.assertRaises(KeyError):
            stock._canonical_section("unknown")
        with self.assertRaises(ValueError):
            stock._canonical_helper_section("unknown")

    def test_load_helper_section_returns_alias_payloads(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        self.assertEqual(stock._load_helper_section("pros")[0], stock.pros()[0])
        self.assertEqual(stock._load_helper_section("cons")[0], stock.cons()[0])
        self.assertEqual(stock._load_helper_section("shareholding_yearly")[-1]["date"], "Dec 2025")

    def test_load_helper_section_respects_allow_missing(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": "<html><body><section id='top'></section></body></html>"}))

        with self.assertRaises(SectionNotFoundError):
            stock._load_helper_section("analysis")
        self.assertIsNone(stock._load_helper_section("analysis", allow_missing=True))

    def test_formatting_helpers_cover_edge_cases(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        self.assertAlmostEqual(stock._compute_cagr([{"sales": 100}, {"sales": 121}], "sales"), 21.0)
        self.assertIsNone(stock._compute_cagr([{"sales": 0}, {"sales": 121}], "sales"))
        self.assertEqual(stock._format_display_value("high_low", {"high": 10, "low": 5}), "₹10 / ₹5")
        self.assertEqual(stock._format_percent(None), "N/A")
        self.assertEqual(stock._format_currency(2527.4), "₹2,527.4")
        self.assertEqual(stock._format_number(1234.50), "1,234.5")
        self.assertEqual(stock._stringify({"a": 1}), '{"a": 1}')

    def test_format_value_helpers_render_plain_text_structures(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        dict_lines = stock._format_dict({"summary": {"name": "TCS"}})
        table_lines = stock._format_list_of_dicts([{"year": "2025", "sales": 100}])
        string_lines = stock._format_list_of_strings(["alpha", "beta"])

        self.assertIn("Summary:", dict_lines[0])
        self.assertIn("Year", table_lines[0])
        self.assertEqual(string_lines, ["  - alpha", "  - beta"])
        self.assertEqual(stock._format_value(None), ["  No data"])

    def test_profit_loss_highlights_uses_summary_roe(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))
        highlights = dict(stock._profit_loss_highlights(stock.profit_loss()))

        self.assertIn("Compounded Sales Growth", highlights)
        self.assertEqual(highlights["Return On Equity"], "65%")

    def test_get_page_html_caches_scraper_result(self) -> None:
        class CountingScraper(FakeScraper):
            def __init__(self, html: str) -> None:
                super().__init__({"TCS": html})

        scraper = CountingScraper(self.page_html)
        stock = Stock("TCS", scraper=scraper)

        first = stock._get_page_html()
        second = stock._get_page_html()

        self.assertEqual(first, second)
        self.assertEqual(scraper.fetch_page_calls, 1)

    def test_page_type_detects_stock_pages(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}))

        self.assertEqual(stock.page_type(), "stock")
        self.assertTrue(stock.is_stock())
        self.assertFalse(stock.is_index())

    def test_page_type_detects_index_pages(self) -> None:
        stock = Stock("NIFTY", scraper=FakeScraper({"NIFTY": load_index_html()}))

        self.assertEqual(stock.page_type(), "index")
        self.assertTrue(stock.is_index())
        self.assertFalse(stock.is_stock())

    def test_stock_rejects_index_pages_with_helpful_error(self) -> None:
        stock = Stock("NIFTY", scraper=FakeScraper({"NIFTY": load_index_html()}))

        with self.assertRaisesRegex(EntityTypeMismatchError, "Use Index\\('NIFTY'\\) instead"):
            stock.available_sections()
        with self.assertRaisesRegex(EntityTypeMismatchError, "Use Index\\('NIFTY'\\) instead"):
            stock.summary()
