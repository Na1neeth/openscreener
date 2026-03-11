"""Simple manual helper for testing the Index API."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Index

CONSTITUENTS_LIMIT = 50


def main() -> int:
    index = Index("CNX500") #for NIFTY500 IT WILL TAKE SOME TIME TO FETCH ALL THE DATA OF 500 COMPANIES, SO BE PATIENT

    print("Page type:", index.page_type())
    print("Available sections:", index.available_sections())
    print()

    summary = index.summary()
    print("Index name:", summary.get("company_name"))
    print("Current price:", summary.get("current_price"))
    print("Market cap:", summary.get("ratios", {}).get("market_cap"))
    print()

    constituents = index.constituents(limit=CONSTITUENTS_LIMIT)
    print("Returned companies:", constituents.get("returned_companies"))
    print("Total companies:", constituents.get("total_companies"))
    print()

    for company in constituents.get("companies", []):
        print(company.get("symbol"), "-", company.get("name"))

    # Remove the # below to see the full summary dictionary.
    print(index.summary())

    # Remove the # below to see the full constituents payload.
    # print(index.constituents(limit=CONSTITUENTS_LIMIT))

    # Remove the # below to test all().
    # print(index.all(constituents_limit=CONSTITUENTS_LIMIT))

    # Remove the # below to test to_json().
    # print(index.to_json(constituents_limit=CONSTITUENTS_LIMIT))

    # Remove the # below to test pretty().
    index.pretty(constituents_limit=CONSTITUENTS_LIMIT)

    # Remove the # below to pretty print only one section.
    # index.print_section("constituents", constituents_limit=CONSTITUENTS_LIMIT)

    # Remove the # below to test metadata().
    # print(index.metadata())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
