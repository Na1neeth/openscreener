from __future__ import annotations

import unittest
from unittest.mock import patch

from openscreener import Index
from openscreener.exceptions import EntityTypeMismatchError
from tests._support import FakeScraper, load_full_html, load_index_html


class IndexClassTestCase(unittest.TestCase):
    def test_public_import_and_available_sections_work_for_index_pages(self) -> None:
        index = Index("NIFTY", scraper=FakeScraper({"NIFTY": load_index_html()}))

        self.assertEqual(index.page_type(), "index")
        self.assertEqual(index.available_sections(), ["summary", "constituents"])

    def test_all_returns_index_payload_with_limit(self) -> None:
        scraper = FakeScraper(
            {"NIFTY": load_index_html(page=1, page_size=50, total_companies=75)},
            constituent_pages={
                "NIFTY": {
                    (1, 50): load_index_html(page=1, page_size=50, total_companies=75),
                    (2, 50): load_index_html(page=2, page_size=50, total_companies=75),
                }
            },
        )
        index = Index("NIFTY", scraper=scraper)

        payload = index.all(constituents_limit=55)

        self.assertEqual(sorted(payload.keys()), ["constituents", "summary"])
        self.assertEqual(payload["summary"]["company_name"], "Nifty 50")
        self.assertEqual(payload["constituents"]["returned_companies"], 55)
        self.assertEqual(payload["constituents"]["companies"][-1]["symbol"], "COMP55")

    def test_to_dataframe_supports_constituents(self) -> None:
        class FakePandas:
            def DataFrame(self, data):
                return {"data": data}

        index = Index("NIFTY", scraper=FakeScraper({"NIFTY": load_index_html()}))

        with patch("openscreener.stock.importlib.import_module", return_value=FakePandas()):
            frame = index.to_dataframe("constituents")

        self.assertEqual(frame["data"], index.constituents()["companies"])

    def test_wrong_page_type_raises_helpful_error(self) -> None:
        index = Index("TCS", scraper=FakeScraper({"TCS": load_full_html()}))

        self.assertEqual(index.page_type(), "stock")
        with self.assertRaisesRegex(EntityTypeMismatchError, "Use Stock\\('TCS'\\) instead"):
            index.summary()


if __name__ == "__main__":
    unittest.main()
