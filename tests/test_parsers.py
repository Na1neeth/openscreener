from __future__ import annotations

import unittest

from openscreener.parsers import (
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
from tests._support import load_full_html


class ParserEntrypointsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.page_html = load_full_html()

    def test_parse_summary(self) -> None:
        payload = parse_summary(self.page_html)

        self.assertEqual(payload["company_name"], "Tata Consultancy Services Ltd")
        self.assertEqual(payload["current_price"], 2527)
        self.assertEqual(payload["bse_code"], "532540")
        self.assertEqual(payload["nse_symbol"], "TCS")

    def test_parse_pros_cons(self) -> None:
        payload = parse_pros_cons(self.page_html)

        self.assertGreaterEqual(len(payload["pros"]), 1)
        self.assertGreaterEqual(len(payload["cons"]), 1)

    def test_parse_peers(self) -> None:
        payload = parse_peers(self.page_html)

        self.assertIn("Nifty 50", payload["benchmarks"])
        self.assertEqual(payload["companies"][0]["name"], "TCS")
        self.assertIsNone(payload["median"])

    def test_parse_quarterly_results(self) -> None:
        payload = parse_quarterly_results(self.page_html)
        self.assertEqual(payload[-1]["date"], "Dec 2025")
        self.assertEqual(payload[-1]["sales"], 55567)

    def test_parse_profit_loss(self) -> None:
        payload = parse_profit_loss(self.page_html)
        self.assertEqual(payload[-1]["year"], "TTM")
        self.assertIsNone(payload[-1]["dividend_payout"])

    def test_parse_balance_sheet(self) -> None:
        payload = parse_balance_sheet(self.page_html)
        self.assertEqual(payload[-1]["year"], "Sep 2025")
        self.assertIn("total_assets", payload[-1])

    def test_parse_cash_flow(self) -> None:
        payload = parse_cash_flow(self.page_html)
        self.assertEqual(payload[-1]["year"], "Mar 2025")
        self.assertIn("net_cash_flow", payload[-1])

    def test_parse_ratios(self) -> None:
        payload = parse_ratios(self.page_html)
        self.assertEqual(payload["year"], "Mar 2025")
        self.assertEqual(payload["roce_percent"], 78)

    def test_parse_shareholding_for_each_frequency(self) -> None:
        quarterly = parse_shareholding(self.page_html, frequency="quarterly")
        yearly = parse_shareholding(self.page_html, frequency="yearly")

        self.assertEqual(quarterly[-1]["date"], "Dec 2025")
        self.assertEqual(yearly[-1]["date"], "Dec 2025")

    def test_parse_shareholding_returns_empty_list_when_frequency_container_missing(self) -> None:
        html = "<section id='shareholding'></section>"
        self.assertEqual(parse_shareholding(html, frequency="yearly"), [])
