"""Parsers for Screener index pages."""

from __future__ import annotations

import re

from ._helpers import clean_text, node_text, parse_number, require_node

_PAGE_INFO_RE = re.compile(r"(\d+)\s+results found:\s+Showing page\s+(\d+)\s+of\s+(\d+)", re.IGNORECASE)
_CONSTITUENT_HEADER_MAP = {
    "s.no.": "s_no",
    "name": "name",
    "cmp rs.": "current_price",
    "p/e": "p_e",
    "mar cap rs.cr.": "market_cap",
    "div yld %": "dividend_yield",
    "np qtr rs.cr.": "net_profit_quarter",
    "qtr profit var %": "qtr_profit_var",
    "sales qtr rs.cr.": "sales_quarter",
    "qtr sales var %": "qtr_sales_var",
    "roce %": "roce_percent",
}


def parse_constituents(html: str, *, limit: int | None = None) -> dict[str, object]:
    section = require_node(html, "constituents")
    companies_table = section.find("table", class_="data-table")
    if companies_table is None:
        return {
            "title": node_text(section.find("h2")),
            "total_companies": 0,
            "page": 1,
            "total_pages": 1,
            "companies": [],
            "median": None,
            "returned_companies": 0,
        }

    title = node_text(section.find("h2"))
    page_info_text = node_text(section.find(class_="sub"))
    total_companies, page, total_pages = _parse_page_info(page_info_text)
    headers = _parse_headers(companies_table)
    companies = _parse_company_rows(companies_table, headers)
    median = _parse_median_row(companies_table, headers)
    if limit is not None:
        companies = companies[: max(limit, 0)]

    if not total_companies:
        total_companies = len(companies)

    return {
        "title": title,
        "total_companies": total_companies,
        "page": page,
        "total_pages": total_pages,
        "companies": companies,
        "median": median,
        "returned_companies": len(companies),
    }


def _parse_page_info(page_info_text: str) -> tuple[int, int, int]:
    match = _PAGE_INFO_RE.search(page_info_text)
    if not match:
        return 0, 1, 1
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _parse_headers(table) -> list[str]:
    header_row = table.find("tr")
    if header_row is None:
        return []

    headers: list[str] = []
    for cell in header_row.direct_children("th"):
        label = clean_text(node_text(cell)).lower()
        headers.append(_CONSTITUENT_HEADER_MAP.get(label, label))
    return headers


def _parse_company_rows(table, headers: list[str]) -> list[dict[str, object]]:
    body = table.find("tbody") or table
    companies: list[dict[str, object]] = []
    for row in body.direct_children("tr"):
        cells = row.direct_children("td")
        if not cells or len(cells) != len(headers):
            continue

        company: dict[str, object] = {}
        for header, cell in zip(headers, cells):
            if header == "name":
                company["name"] = node_text(cell)
                link = cell.find("a")
                href = link.get("href", "") if link is not None else ""
                if href:
                    company["company_path"] = href
                    company["symbol"] = _extract_symbol_from_path(href)
                continue
            company[header] = parse_number(node_text(cell))
        if company:
            companies.append(company)
    return companies


def _parse_median_row(table, headers: list[str]) -> dict[str, object] | None:
    footer = table.find("tfoot")
    if footer is None:
        return None

    row = footer.find("tr")
    if row is None:
        return None

    cells = row.direct_children("td")
    if not cells or len(cells) != len(headers):
        return None

    payload: dict[str, object] = {}
    for header, cell in zip(headers, cells):
        text = node_text(cell)
        if not text:
            continue
        if header == "name":
            payload["label"] = text
            continue
        payload[header] = parse_number(text)
    return payload or None


def _extract_symbol_from_path(path: str) -> str:
    cleaned = path.strip("/")
    parts = cleaned.split("/")
    if len(parts) < 2:
        return ""
    if parts[0] != "company":
        return ""
    return parts[1].upper()
