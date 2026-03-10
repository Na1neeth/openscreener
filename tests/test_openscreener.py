from contextlib import redirect_stdout
from io import StringIO
import json
import unittest
from unittest.mock import patch

from openscreener import Stock
from tests._support import FakeScraper, load_full_html


class OpenScreenerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.page_html = load_full_html()
        cls.stock = Stock("TCS", scraper=FakeScraper({"TCS": cls.page_html}))

    def test_summary_parser_extracts_company_data(self) -> None:
        summary = self.stock.summary()

        self.assertEqual(summary["company_name"], "Tata Consultancy Services Ltd")
        self.assertEqual(summary["current_price"], 2527)
        self.assertEqual(summary["ratios"]["market_cap"], 914418)
        self.assertEqual(summary["ratios"]["stock_p_e"], 18.7)

    def test_fetch_multiple_sections_returns_structured_payload(self) -> None:
        payload = self.stock.fetch(["summary", "analysis", "profit_loss", "ratios", "shareholding"])

        self.assertIn("summary", payload)
        self.assertIn("analysis", payload)
        self.assertIn("profit_loss", payload)
        self.assertIn("ratios", payload)
        self.assertIn("shareholding", payload)
        self.assertEqual(payload["analysis"]["pros"][0], "Company has a good return on equity (ROE) track record: 3 Years ROE 58.9%")

    def test_quarterly_and_yearly_tables_parse_latest_values(self) -> None:
        quarters = self.stock.quarterly_results()
        profit_loss = self.stock.profit_loss()
        balance_sheet = self.stock.balance_sheet()
        cash_flow = self.stock.cash_flow()

        self.assertEqual(quarters[-1]["date"], "Dec 2025")
        self.assertEqual(quarters[-1]["net_profit"], 10190)
        self.assertEqual(profit_loss[-1]["year"], "TTM")
        self.assertEqual(balance_sheet[-1]["year"], "Sep 2025")
        self.assertEqual(cash_flow[-1]["year"], "Mar 2025")

    def test_ratios_and_shareholding_use_latest_period_shape(self) -> None:
        ratios = self.stock.ratios()
        shareholding = self.stock.shareholding()

        self.assertEqual(ratios["year"], "Mar 2025")
        self.assertEqual(ratios["debtor_days"], 88)
        self.assertEqual(ratios["roce_percent"], 78)
        self.assertEqual(shareholding[-1]["date"], "Dec 2025")
        self.assertAlmostEqual(shareholding[-1]["promoters"], 71.77)

    def test_batch_fetch_reuses_fixture_scraper(self) -> None:
        scraper = FakeScraper({"TCS": self.page_html, "INFY": self.page_html})
        batch = Stock.batch(["TCS", "INFY"], scraper=scraper)
        payload = batch.fetch("ratios")

        self.assertEqual(sorted(payload.keys()), ["INFY", "TCS"])
        self.assertEqual(payload["TCS"]["year"], "Mar 2025")

    def test_to_json_serializes_full_payload(self) -> None:
        payload = json.loads(self.stock.to_json())

        self.assertIn("summary", payload)
        self.assertIn("cash_flow", payload)
        self.assertEqual(payload["summary"]["company_name"], "Tata Consultancy Services Ltd")

    def test_wrapper_methods_expose_pros_cons_and_shareholding_views(self) -> None:
        self.assertIn("Company has a good return on equity", self.stock.pros()[0])
        self.assertIn("Stock is trading at 10.8 times its book value", self.stock.cons()[0])
        self.assertEqual(self.stock.shareholding_quarterly()[-1]["date"], "Dec 2025")
        self.assertEqual(self.stock.shareholding_yearly()[-1]["date"], "Dec 2025")

    def test_pretty_renders_human_readable_section_output(self) -> None:
        buffer = StringIO()

        with redirect_stdout(buffer):
            self.stock.pretty("cash_flow")

        output = buffer.getvalue()
        self.assertIn("Cash Flow", output)
        self.assertIn("Cash From Operating Activity", output)

    def test_pretty_supports_pros_alias(self) -> None:
        buffer = StringIO()

        with redirect_stdout(buffer):
            self.stock.pretty("pros")

        output = buffer.getvalue()
        self.assertIn("PROS", output)
        self.assertRegex(output, r"[•-] Company has a good return on equity")

    def test_print_section_rejects_unsupported_section(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported section"):
            self.stock.print_section("unknown")

    def test_to_dataframe_uses_pandas_lazily(self) -> None:
        class FakePandas:
            def DataFrame(self, data):
                return {"data": data}

        with patch("openscreener.stock.importlib.import_module", return_value=FakePandas()):
            frame = self.stock.to_dataframe("peers")

        self.assertEqual(frame["data"], self.stock.peers()["companies"])

    def test_to_dataframe_raises_helpful_error_when_pandas_is_missing(self) -> None:
        with patch("openscreener.stock.importlib.import_module", side_effect=ImportError("No module named pandas")):
            with self.assertRaisesRegex(ImportError, "pip install pandas"):
                self.stock.to_dataframe("cash_flow")

    def test_metadata_includes_source_defaults_and_company_name(self) -> None:
        metadata = self.stock.metadata()

        self.assertEqual(metadata["symbol"], "TCS")
        self.assertFalse(metadata["consolidated"])
        self.assertEqual(metadata["source"], "screener.in")
        self.assertEqual(metadata["currency"], "INR")
        self.assertEqual(metadata["units"], "crores")
        self.assertEqual(metadata["company_name"], "Tata Consultancy Services Ltd")

    def test_metadata_reports_consolidated_when_enabled(self) -> None:
        stock = Stock("TCS", scraper=FakeScraper({"TCS": self.page_html}), consolidated=True)

        metadata = stock.metadata()

        self.assertTrue(metadata["consolidated"])


if __name__ == "__main__":
    unittest.main()
