"""Parser for the Screener peers section."""

from __future__ import annotations

from ._helpers import node_text, parse_row_table, require_node


def parse_peers(html: str) -> dict[str, object]:
    section = require_node(html, "peers")
    benchmarks_block = section.find(id_="benchmarks")
    benchmarks = [node_text(link) for link in benchmarks_block.find_all("a")] if benchmarks_block is not None else []
    companies = parse_row_table(section)

    median = companies[-1] if companies and isinstance(companies[-1].get("text"), str) and "median" in str(companies[-1]["text"]).lower() else None
    if median is not None:
        companies = companies[:-1]

    return {
        "benchmarks": benchmarks,
        "companies": companies,
        "median": median,
    }
