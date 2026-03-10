"""Public index API."""

from __future__ import annotations

from .stock import Stock, _INDEX_SECTIONS


class Index(Stock):
    """High-level API for one Screener index page."""

    __slots__ = ()

    def _expected_page_type(self) -> str:
        return "index"

    def _supported_sections(self) -> list[str]:
        return list(_INDEX_SECTIONS)
