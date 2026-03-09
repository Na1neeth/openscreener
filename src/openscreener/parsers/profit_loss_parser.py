"""Parser for profit and loss statements."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_profit_loss(html: str) -> list[dict[str, object]]:
    section = require_node(html, "profit-loss")
    return parse_transposed_table(section, "year")
