"""Parser for balance sheet statements."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_balance_sheet(html: str) -> list[dict[str, object]]:
    section = require_node(html, "balance-sheet")
    return parse_transposed_table(section, "year")
