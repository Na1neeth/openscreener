import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openscreener import StaticScraper, Stock
from openscreener.parsers import parse_chart


def load_sections() -> dict[str, str]:
    fixture_dir = Path(__file__).resolve().parents[1] / "examples" / "html"
    return {
        "top": (fixture_dir / "summary.html").read_text(encoding="utf-8"),
        "analysis": (fixture_dir / "pros_cons.html").read_text(encoding="utf-8"),
        "peers": (fixture_dir / "peers.html").read_text(encoding="utf-8"),
        "quarters": (fixture_dir / "quarterly_results.html").read_text(encoding="utf-8"),
        "profit-loss": (fixture_dir / "profit_loss.html").read_text(encoding="utf-8"),
        "balance-sheet": (fixture_dir / "balance_sheet.html").read_text(encoding="utf-8"),
        "cash-flow": (fixture_dir / "cash_flow.html").read_text(encoding="utf-8"),
        "ratios": (fixture_dir / "ratios.html").read_text(encoding="utf-8"),
        "shareholding": (fixture_dir / "shareholding.html").read_text(encoding="utf-8"),
        "chart": (fixture_dir / "peratio.html").read_text(encoding="utf-8"),
    }


class OpenScreenerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sections = load_sections()
        cls.stock = Stock.from_sections("TCS", cls.sections)

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
        scraper = StaticScraper(
            sections={
                "TCS": self.sections,
                "INFY": self.sections,
            }
        )
        batch = Stock.batch(["TCS", "INFY"], scraper=scraper)
        payload = batch.fetch("ratios")

        self.assertEqual(sorted(payload.keys()), ["INFY", "TCS"])
        self.assertEqual(payload["TCS"]["year"], "Mar 2025")

    def test_chart_fixture_exposes_metadata(self) -> None:
        chart = parse_chart(self.sections["chart"])

        self.assertEqual(chart["active_range"], "5Y")
        self.assertIn("PE Ratio", chart["available_metrics"])
        self.assertIn("MAX", chart["available_ranges"])
        self.assertEqual(chart["data"], [])


if __name__ == "__main__":
    unittest.main()
