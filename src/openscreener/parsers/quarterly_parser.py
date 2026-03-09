"""Parser for quarterly results."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_quarterly_results(html: str) -> list[dict[str, object]]:
    section = require_node(html, "quarters")
    return parse_transposed_table(section, "date")
