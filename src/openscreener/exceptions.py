"""Project-specific exceptions."""


class OpenScreenerError(Exception):
    """Base exception for openscreener."""


class SectionNotFoundError(OpenScreenerError):
    """Raised when a requested Screener section is not present in the HTML."""


class EntityTypeMismatchError(OpenScreenerError):
    """Raised when a stock/index class is used against the wrong Screener page type."""
