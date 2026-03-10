from __future__ import annotations

import unittest

from openscreener.exceptions import SectionNotFoundError
from openscreener.parsers._helpers import (
    build_fixture_page,
    clean_text,
    find_primary_table,
    header_values,
    node_text,
    normalize_key,
    parse_number,
    parse_ratio_list,
    parse_row_table,
    parse_transposed_table,
    require_node,
    row_cells,
)
from openscreener.parsers._html import parse_html
from tests._support import load_sections


class ParserHelpersTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sections = load_sections()
        cls.page_html = build_fixture_page(cls.sections)

    def test_require_node_returns_matching_section(self) -> None:
        section = require_node(self.page_html, "top")
        self.assertEqual(section.get("id"), "top")

    def test_require_node_raises_for_missing_section(self) -> None:
        with self.assertRaises(SectionNotFoundError):
            require_node("<html></html>", "missing")

    def test_clean_text_and_node_text_normalize_whitespace(self) -> None:
        self.assertEqual(clean_text("  A\xa0 \n B + "), "A B")
        self.assertEqual(node_text(parse_html("<div> Hi <span>there</span></div>").find("div")), "Hi there")

    def test_normalize_key_maps_known_labels(self) -> None:
        self.assertEqual(normalize_key("Sales +"), "sales")
        self.assertEqual(normalize_key("ROCE %"), "roce_percent")
        self.assertEqual(normalize_key("No. of Shareholders"), "number_of_shareholders")

    def test_parse_number_handles_numeric_variants(self) -> None:
        self.assertEqual(parse_number("1,234"), 1234)
        self.assertEqual(parse_number("₹18.72"), 18.72)
        self.assertEqual(parse_number("(42)"), -42)
        self.assertIsNone(parse_number("--"))
        self.assertEqual(parse_number("Text Value"), "Text Value")

    def test_find_primary_table_row_cells_and_header_values_work_together(self) -> None:
        section = parse_html(
            """
            <section id="demo">
              <table class="data-table">
                <tr><th>Name</th><th>Value</th></tr>
                <tr><td>Alpha</td><td>10</td></tr>
              </table>
            </section>
            """
        ).find("section", id_="demo")

        assert section is not None
        table = find_primary_table(section)
        header_row = table.find_all("tr")[0]

        self.assertEqual([cell.tag for cell in row_cells(header_row)], ["th", "th"])
        self.assertEqual(header_values(header_row), ["Name", "Value"])

    def test_parse_transposed_table_reads_period_columns(self) -> None:
        section = require_node(self.page_html, "quarters")
        records = parse_transposed_table(section, "date")

        self.assertEqual(records[0]["date"], "Dec 2022")
        self.assertIn("sales", records[0])
        self.assertEqual(records[-1]["net_profit"], 10190)

    def test_parse_row_table_parses_rows_and_skips_mismatched_data(self) -> None:
        section = parse_html(
            """
            <section id="peers">
              <table class="data-table">
                <tr><th>Text</th><th>CMP</th></tr>
                <tr><td>TCS</td><td>2527.4</td></tr>
                <tr><td>Broken</td></tr>
              </table>
            </section>
            """
        ).find("section", id_="peers")

        assert section is not None
        self.assertEqual(parse_row_table(section), [{"text": "TCS", "cmp": 2527.4}])

    def test_parse_ratio_list_extracts_high_low_and_numeric_values(self) -> None:
        section = require_node(self.page_html, "top")
        ratios = parse_ratio_list(section)

        self.assertEqual(ratios["market_cap"], 914418)
        self.assertEqual(ratios["high_low"], {"high": 3710, "low": 2505})

    def test_build_fixture_page_keeps_expected_section_order(self) -> None:
        html = build_fixture_page({"analysis": "<section id='analysis'></section>", "top": "<section id='top'></section>"})
        self.assertLess(html.index("id='top'"), html.index("id='analysis'"))
