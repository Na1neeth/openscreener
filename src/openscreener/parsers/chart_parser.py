"""Parser for chart metadata."""

from __future__ import annotations

from ._helpers import node_text, normalize_range_label, require_node


def parse_chart(html: str) -> dict[str, object]:
    section = require_node(html, "chart")
    range_buttons = [
        normalize_range_label(node_text(button))
        for button in section.find_all("button")
        if button.get("name") == "days"
    ]
    active_range = ""
    active_metric = ""
    available_metrics: list[str] = []
    for button in section.find_all("button"):
        text = node_text(button)
        if button.get("name") == "metrics" and text:
            available_metrics.append(text)
            if "active" in button.classes():
                active_metric = text
        if button.get("name") == "days" and "active" in button.classes():
            active_range = normalize_range_label(text)

    more_button = section.find(id_="company-chart-metrics-more-active")
    if more_button is not None and not active_metric:
        active_metric = node_text(more_button)

    legend = [node_text(item) for item in section.find_all("span") if item.parent and item.parent.tag == "label"]

    return {
        "available_ranges": range_buttons,
        "active_range": active_range,
        "available_metrics": available_metrics,
        "active_metric": active_metric,
        "legend": legend,
        "data": [],
    }
