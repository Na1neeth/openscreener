"""Manual QA script to pretty print NIFTY constituents."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from openscreener import Index


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 70
    index = Index("CNX500")
    index.pretty("constituents", constituents_limit=limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
