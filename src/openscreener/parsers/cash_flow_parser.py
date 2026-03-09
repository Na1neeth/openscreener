"""Parser for cash flow statements."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_cash_flow(html: str) -> list[dict[str, object]]:
    section = require_node(html, "cash-flow")
    return parse_transposed_table(section, "year")
