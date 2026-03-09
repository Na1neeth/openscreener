"""Parser for the Screener analysis section."""

from __future__ import annotations

from ._helpers import node_text, require_node


def parse_pros_cons(html: str) -> dict[str, list[str]]:
    section = require_node(html, "analysis")
    pros_block = section.find(class_="pros")
    cons_block = section.find(class_="cons")

    pros = [node_text(item) for item in pros_block.find_all("li")] if pros_block is not None else []
    cons = [node_text(item) for item in cons_block.find_all("li")] if cons_block is not None else []
    return {"pros": pros, "cons": cons}
