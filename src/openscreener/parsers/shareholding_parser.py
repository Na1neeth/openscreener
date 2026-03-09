"""Parser for shareholding data."""

from __future__ import annotations

from ._helpers import parse_transposed_table, require_node


def parse_shareholding(html: str, *, frequency: str = "quarterly") -> list[dict[str, object]]:
    section = require_node(html, "shareholding")
    table_container_id = "quarterly-shp" if frequency == "quarterly" else "yearly-shp"
    container = section.find(id_=table_container_id)
    if container is None:
        return []
    return parse_transposed_table(container, "date")
