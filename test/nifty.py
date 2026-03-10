"""Manual helper for checking NIFTY constituents."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Index

CONSTITUENTS_LIMIT = 10


def main() -> int:
    index = Index("NIFTY")

    payload = {
        "page_type": index.page_type(),
        "summary": index.summary(),
        "constituents": index.constituents(limit=CONSTITUENTS_LIMIT),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    index.pretty(constituents_limit=CONSTITUENTS_LIMIT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
