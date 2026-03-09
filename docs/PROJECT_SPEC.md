# openscreener Project Spec

This package extracts structured financial data from Screener.in using
Playwright for page loading and dedicated parser modules for each section.

The implementation is built around:

- `Stock` for single-company access
- `BatchStock` for multi-company fetches
- `PlaywrightScraper` for live page loading
- parser modules under `src/openscreener/parsers`

The example HTML fixtures in `examples/html/` are used as offline parser
fixtures during development and tests.
