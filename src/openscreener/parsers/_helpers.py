"""Shared parsing helpers for Screener sections."""

from __future__ import annotations

import re

from openscreener.exceptions import SectionNotFoundError

from ._html import Node, parse_html

_LABEL_MAP = {
    "eps in rs": "eps",
    "eps": "eps",
    "sales +": "sales",
    "sales": "sales",
    "expenses +": "expenses",
    "expenses": "expenses",
    "operating profit": "operating_profit",
    "opm %": "operating_margin_percent",
    "opm": "operating_margin_percent",
    "other income": "other_income",
    "interest": "interest",
    "depreciation": "depreciation",
    "profit before tax": "profit_before_tax",
    "tax %": "tax_percent",
    "tax": "tax_percent",
    "net profit +": "net_profit",
    "net profit": "net_profit",
    "dividend payout %": "dividend_payout_percent",
    "equity capital": "equity_capital",
    "reserves": "reserves",
    "borrowings +": "borrowings",
    "borrowings": "borrowings",
    "other liabilities +": "other_liabilities",
    "other liabilities": "other_liabilities",
    "total liabilities": "total_liabilities",
    "fixed assets +": "fixed_assets",
    "fixed assets": "fixed_assets",
    "cwip": "capital_work_in_progress",
    "investments": "investments",
    "other assets +": "other_assets",
    "other assets": "other_assets",
    "total assets": "total_assets",
    "cash from operating activity +": "operating_cash_flow",
    "cash from operating activity": "operating_cash_flow",
    "cash from investing activity +": "investing_cash_flow",
    "cash from investing activity": "investing_cash_flow",
    "cash from financing activity +": "financing_cash_flow",
    "cash from financing activity": "financing_cash_flow",
    "net cash flow": "net_cash_flow",
    "debtor days": "debtor_days",
    "inventory days": "inventory_days",
    "days payable": "days_payable",
    "cash conversion cycle": "cash_conversion_cycle",
    "working capital days": "working_capital_days",
    "roce %": "roce_percent",
    "roce": "roce_percent",
    "return on equity %": "roe_percent",
    "roe": "roe_percent",
    "promoters +": "promoters",
    "promoters": "promoters",
    "fiis +": "fiis",
    "fiis": "fiis",
    "diis +": "diis",
    "diis": "diis",
    "government": "government",
    "public +": "public",
    "public": "public",
    "no. of shareholders": "number_of_shareholders",
}
_SLUG_MAP = {
    "opm": "operating_margin_percent",
    "tax": "tax_percent",
    "roce": "roce_percent",
    "roe": "roe_percent",
}
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


def require_node(html: str, node_id: str) -> Node:
    root = parse_html(html)
    node = root.find(id_=node_id)
    if node is None:
        raise SectionNotFoundError(f"Could not find section with id '{node_id}'.")
    return node


def clean_text(value: str) -> str:
    text = value.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" +", "")
    return text.strip()


def node_text(node: Node | None) -> str:
    if node is None:
        return ""
    return clean_text(node.text())


def normalize_key(label: str) -> str:
    lowered = clean_text(label).lower().replace("%", " %").replace("+", " +")
    lowered = re.sub(r"\[[^\]]+\]", "", lowered).strip()
    if lowered in _LABEL_MAP:
        return _LABEL_MAP[lowered]
    slug = _NON_ALNUM_RE.sub("_", lowered).strip("_")
    slug = slug.replace("_in_rs", "").replace("_rs", "")
    slug = slug.replace("_crores", "").replace("_crore", "")
    slug = slug.replace("_percent", "_percent")
    return _SLUG_MAP.get(slug, slug)


def parse_number(value: str) -> int | float | None | str:
    text = clean_text(value)
    if text in {"", "-", "--", "N/A"}:
        return None
    negative = text.startswith("(") and text.endswith(")")
    cleaned = text.strip("()")
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("₹", "")
    cleaned = cleaned.replace("%", "")
    cleaned = cleaned.replace("Cr.", "")
    cleaned = cleaned.replace("x", "")
    cleaned = cleaned.replace("X", "")
    cleaned = cleaned.replace("times", "")
    cleaned = cleaned.strip()
    if _NUMBER_RE.match(cleaned):
        number: int | float
        if "." in cleaned:
            number = float(cleaned)
        else:
            number = int(cleaned)
        return -number if negative else number
    return text


def find_primary_table(section: Node) -> Node:
    for table in section.find_all("table"):
        classes = set(table.classes())
        if "data-table" in classes:
            return table
    raise SectionNotFoundError("Could not find a primary data table in the requested section.")


def row_cells(row: Node) -> list[Node]:
    return row.direct_children("th", "td")


def header_values(row: Node) -> list[str]:
    return [node_text(cell) for cell in row_cells(row)]


def parse_transposed_table(section: Node, period_key: str) -> list[dict[str, int | float | None | str]]:
    table = find_primary_table(section)
    header_row = table.find("thead").find_all("tr")[0] if table.find("thead") else table.find_all("tr")[0]
    headers = [value for value in header_values(header_row)[1:] if value]
    records: list[dict[str, int | float | None | str]] = [{period_key: header} for header in headers]

    body = table.find("tbody") or table
    for row in body.find_all("tr"):
        cells = row_cells(row)
        if len(cells) <= 1:
            continue
        label = node_text(cells[0]).rstrip("+").strip()
        if not label:
            continue
        key = normalize_key(label)
        for index, cell in enumerate(cells[1 : len(headers) + 1]):
            records[index][key] = parse_number(node_text(cell))

    return [record for record in records if len(record) > 1]


def parse_row_table(section: Node) -> list[dict[str, int | float | None | str]]:
    table = find_primary_table(section)
    rows = table.find_all("tr")
    if not rows:
        return []
    headers = [normalize_key(value) for value in header_values(rows[0])]
    items: list[dict[str, int | float | None | str]] = []
    for row in rows[1:]:
        cells = row_cells(row)
        if not cells:
            continue
        values = [node_text(cell) for cell in cells]
        if len(values) != len(headers):
            continue
        item: dict[str, int | float | None | str] = {}
        for header, value in zip(headers, values):
            if not header:
                continue
            item[header] = parse_number(value)
        if item:
            items.append(item)
    return items


def parse_ratio_list(section: Node) -> dict[str, int | float | None | str | dict[str, int | float | None]]:
    ratios: dict[str, int | float | None | str | dict[str, int | float | None]] = {}
    ratio_list = section.find("ul", id_="top-ratios")
    if ratio_list is None:
        return ratios
    for item in ratio_list.find_all("li"):
        name_node = item.find(class_="name")
        value_node = item.find(class_="value")
        name = normalize_key(node_text(name_node))
        value = node_text(value_node)
        if not name or not value:
            continue
        if name == "high_low":
            parts = [clean_text(part) for part in value.replace("₹", "").split("/")]
            if len(parts) == 2:
                ratios[name] = {
                    "high": parse_number(parts[0]),
                    "low": parse_number(parts[1]),
                }
                continue
        ratios[name] = parse_number(value)
    return ratios


def build_fixture_page(section_html_by_id: dict[str, str]) -> str:
    ordered_ids = [
        "top",
        "analysis",
        "peers",
        "quarters",
        "profit-loss",
        "balance-sheet",
        "cash-flow",
        "ratios",
        "shareholding",
    ]
    fragments = [section_html_by_id[section_id] for section_id in ordered_ids if section_id in section_html_by_id]
    return "<html><body>" + "\n".join(fragments) + "</body></html>"
