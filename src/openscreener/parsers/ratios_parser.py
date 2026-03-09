"""Parser for ratios."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_ratios(html: str) -> dict[str, object]:
    section = require_node(html, "ratios")
    history = parse_transposed_table(section, "year")
    return history[-1] if history else {}
