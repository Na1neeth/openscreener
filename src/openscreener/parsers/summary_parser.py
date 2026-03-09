"""Parser for the Screener summary block."""

from __future__ import annotations

from ._helpers import node_text, parse_number, parse_ratio_list, require_node


def parse_summary(html: str) -> dict[str, object]:
    section = require_node(html, "top")
    title = node_text(section.find("h1"))
    price_block = section.find(class_="font-size-18")
    price_spans = price_block.find_all("span") if price_block is not None else []
    current_price = parse_number(node_text(price_spans[0])) if price_spans else None
    price_change_percent = None
    if len(price_spans) > 1:
        price_change_percent = parse_number(node_text(price_spans[1]))

    meta_block = section.find(class_="font-size-11")
    about_block = section.find(class_="about")
    commentary_block = section.find(class_="commentary")

    website = ""
    bse_code = ""
    nse_symbol = ""
    for link in section.find_all("a"):
        label = node_text(link)
        href = link.get("href", "")
        if href.startswith("http://www.") or href.startswith("https://www.") and "bseindia" not in href and "nseindia" not in href:
            website = href
        if "BSE:" in label:
            bse_code = label.split("BSE:", 1)[1].strip()
        if "NSE:" in label:
            nse_symbol = label.split("NSE:", 1)[1].strip()

    return {
        "company_name": title,
        "current_price": current_price,
        "price_change_percent": price_change_percent,
        "price_date": node_text(meta_block).replace("- close price", "").strip(),
        "website": website,
        "bse_code": bse_code,
        "nse_symbol": nse_symbol,
        "about": node_text(about_block),
        "key_points": node_text(commentary_block),
        "ratios": parse_ratio_list(section),
    }
