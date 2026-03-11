"""Public stock API."""

from __future__ import annotations

import importlib
import json
import math
from dataclasses import dataclass
from typing import Iterable

from .exceptions import EntityTypeMismatchError, SectionNotFoundError
from .parsers import (
    parse_balance_sheet,
    parse_cash_flow,
    parse_constituents,
    parse_peers,
    parse_profit_loss,
    parse_pros_cons,
    parse_quarterly_results,
    parse_ratios,
    parse_shareholding,
    parse_summary,
)
from .scraper import PlaywrightScraper

_SECTION_ALIASES = {
    "summary": "summary",
    "analysis": "analysis",
    "pros_cons": "analysis",
    "peers": "peers",
    "quarters": "quarterly_results",
    "quarterly_results": "quarterly_results",
    "profit-loss": "profit_loss",
    "profit_loss": "profit_loss",
    "balance-sheet": "balance_sheet",
    "balance_sheet": "balance_sheet",
    "cash-flow": "cash_flow",
    "cash_flow": "cash_flow",
    "ratios": "ratios",
    "shareholding": "shareholding",
    "constituents": "constituents",
    "companies": "constituents",
}
_STOCK_SECTIONS = [
    "summary",
    "analysis",
    "peers",
    "quarterly_results",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "ratios",
    "shareholding",
]
_INDEX_SECTIONS = [
    "summary",
    "constituents",
]
_HELPER_SECTION_ALIASES = {
    **_SECTION_ALIASES,
    "pros": "pros",
    "cons": "cons",
    "shareholding-quarterly": "shareholding_quarterly",
    "shareholding_quarterly": "shareholding_quarterly",
    "shareholding-yearly": "shareholding_yearly",
    "shareholding_yearly": "shareholding_yearly",
}
_TOP_CARD_METRICS = [
    ("market_cap", "Market Cap"),
    ("current_price", "Current Price"),
    ("high_low", "High / Low"),
    ("stock_p_e", "Stock P/E"),
    ("book_value", "Book Value"),
    ("dividend_yield", "Dividend Yield"),
    ("roce_percent", "ROCE"),
    ("roe_percent", "ROE"),
    ("face_value", "Face Value"),
]
_INDEX_TOP_CARD_METRICS = [
    ("market_cap", "Market Cap"),
    ("current_price", "Current Price"),
    ("high_low", "High / Low"),
    ("p_e", "P/E"),
    ("price_to_book_value", "Price To Book"),
    ("dividend_yield", "Dividend Yield"),
    ("cagr_1yr", "CAGR 1Y"),
    ("cagr_5yr", "CAGR 5Y"),
    ("cagr_10yr", "CAGR 10Y"),
]
_PEER_COLUMNS = [
    ("s_no", "S.No"),
    ("name", "Name"),
    ("cmp", "CMP"),
    ("p_e", "P/E"),
    ("mar_cap_cr", "Mar Cap"),
    ("div_yld", "Div Yld"),
    ("np_qtr_cr", "NP Qtr"),
    ("qtr_profit_var", "Qtr Profit Var"),
    ("sales_qtr_cr", "Sales Qtr"),
    ("qtr_sales_var", "Qtr Sales Var"),
    ("roce_percent", "ROCE"),
]
_CONSTITUENT_COLUMNS = [
    ("s_no", "S.No"),
    ("name", "Name"),
    ("symbol", "Symbol"),
    ("current_price", "CMP"),
    ("p_e", "P/E"),
    ("market_cap", "Mar Cap"),
    ("dividend_yield", "Div Yld"),
    ("net_profit_quarter", "NP Qtr"),
    ("qtr_profit_var", "Qtr Profit Var"),
    ("sales_quarter", "Sales Qtr"),
    ("qtr_sales_var", "Qtr Sales Var"),
    ("roce_percent", "ROCE"),
]
_QUARTERLY_ROWS = [
    ("sales", "Sales"),
    ("expenses", "Expenses"),
    ("operating_profit", "Operating Profit"),
    ("operating_margin_percent", "OPM %"),
    ("other_income", "Other Income"),
    ("interest", "Interest"),
    ("depreciation", "Depreciation"),
    ("profit_before_tax", "Profit Before Tax"),
    ("tax_percent", "Tax %"),
    ("net_profit", "Net Profit"),
    ("eps", "EPS"),
]
_PROFIT_LOSS_ROWS = [
    ("sales", "Sales"),
    ("expenses", "Expenses"),
    ("operating_profit", "Operating Profit"),
    ("operating_margin_percent", "OPM %"),
    ("other_income", "Other Income"),
    ("interest", "Interest"),
    ("depreciation", "Depreciation"),
    ("profit_before_tax", "Profit Before Tax"),
    ("tax_percent", "Tax %"),
    ("net_profit", "Net Profit"),
    ("eps", "EPS"),
    ("dividend_payout", "Dividend Payout %"),
]
_BALANCE_SHEET_ROWS = [
    ("equity_capital", "Equity Capital"),
    ("reserves", "Reserves"),
    ("borrowings", "Borrowings"),
    ("other_liabilities", "Other Liabilities"),
    ("total_liabilities", "Total Liabilities"),
    ("fixed_assets", "Fixed Assets"),
    ("capital_work_in_progress", "CWIP"),
    ("investments", "Investments"),
    ("other_assets", "Other Assets"),
    ("total_assets", "Total Assets"),
]
_CASH_FLOW_ROWS = [
    ("operating_cash_flow", "Cash From Operating Activity"),
    ("investing_cash_flow", "Cash From Investing Activity"),
    ("financing_cash_flow", "Cash From Financing Activity"),
    ("net_cash_flow", "Net Cash Flow"),
]
_RATIO_ROWS = [
    ("debtor_days", "Debtor Days"),
    ("inventory_days", "Inventory Days"),
    ("days_payable", "Days Payable"),
    ("cash_conversion_cycle", "Cash Conversion Cycle"),
    ("working_capital_days", "Working Capital Days"),
    ("roce_percent", "ROCE"),
]
_SHAREHOLDING_ROWS = [
    ("promoters", "Promoters"),
    ("fiis", "FIIs"),
    ("diis", "DIIs"),
    ("government", "Government"),
    ("public", "Public"),
    ("number_of_shareholders", "No. Of Shareholders"),
]
_PERCENT_KEYS = {
    "dividend_yield",
    "operating_margin_percent",
    "tax_percent",
    "qtr_profit_var",
    "qtr_sales_var",
    "roce_percent",
    "roe_percent",
    "div_yld",
    "promoters",
    "fiis",
    "diis",
    "government",
    "public",
    "dividend_payout",
    "cagr_1yr",
    "cagr_5yr",
    "cagr_10yr",
}
_CURRENCY_KEYS = {"current_price", "cmp", "book_value", "face_value"}
_STOCK_PAGE_MARKERS = (
    'id="analysis"',
    "id='analysis'",
    'id="peers"',
    "id='peers'",
    'id="quarters"',
    "id='quarters'",
    'id="profit-loss"',
    "id='profit-loss'",
    'id="balance-sheet"',
    "id='balance-sheet'",
    'id="cash-flow"',
    "id='cash-flow'",
    'id="ratios"',
    "id='ratios'",
    'id="shareholding"',
    "id='shareholding'",
)
_INDEX_PAGE_MARKERS = (
    'id="constituents"',
    "id='constituents'",
    ">Constituents<",
    "Companies in ",
)


@dataclass(slots=True)
class Stock:
    """High-level API for one Screener company."""

    symbol: str
    consolidated: bool = False
    scraper: PlaywrightScraper | None = None
    page_html: str | None = None
    _page_type: str | None = None
    _constituent_pages: dict[tuple[int, int], str] | None = None

    def __post_init__(self) -> None:
        self.symbol = self.symbol.upper()
        if self.scraper is None:
            self.scraper = PlaywrightScraper(consolidated=self.consolidated)
        elif isinstance(self.scraper, PlaywrightScraper):
            self.consolidated = self.scraper.consolidated

    @classmethod
    def batch(
        cls,
        symbols: Iterable[str],
        scraper: PlaywrightScraper | None = None,
        *,
        consolidated: bool = False,
    ):
        from .batch_stock import BatchStock

        return BatchStock(list(symbols), consolidated=consolidated, scraper=scraper)

    def summary(self) -> dict[str, object]:
        self._require_section_available("summary")
        return parse_summary(self._get_page_html())

    def pros_cons(self) -> dict[str, list[str]]:
        self._require_section_available("analysis")
        return parse_pros_cons(self._get_page_html())

    def pros(self) -> list[str]:
        """Return the analysis pros as a plain list of strings."""

        return self.pros_cons().get("pros", [])

    def cons(self) -> list[str]:
        """Return the analysis cons as a plain list of strings."""

        return self.pros_cons().get("cons", [])

    def peers(self) -> dict[str, object]:
        self._require_section_available("peers")
        return parse_peers(self._get_page_html())

    def quarterly_results(self) -> list[dict[str, object]]:
        self._require_section_available("quarterly_results")
        return parse_quarterly_results(self._get_page_html())

    def profit_loss(self) -> list[dict[str, object]]:
        self._require_section_available("profit_loss")
        return parse_profit_loss(self._get_page_html())

    def balance_sheet(self) -> list[dict[str, object]]:
        self._require_section_available("balance_sheet")
        return parse_balance_sheet(self._get_page_html())

    def cash_flow(self) -> list[dict[str, object]]:
        self._require_section_available("cash_flow")
        return parse_cash_flow(self._get_page_html())

    def ratios(self) -> dict[str, object]:
        self._require_section_available("ratios")
        return parse_ratios(self._get_page_html())

    def shareholding(self, *, frequency: str = "quarterly") -> list[dict[str, object]]:
        self._require_section_available("shareholding")
        return parse_shareholding(self._get_page_html(), frequency=frequency)

    def constituents(self, *, limit: int | None = None) -> dict[str, object]:
        """Return parsed index constituents, optionally capped to the requested count."""

        self._require_section_available("constituents")
        requested_page_size = 50
        first_page = self._parse_constituent_page(page_number=1, page_size=requested_page_size)
        total_companies = int(first_page.get("total_companies") or 0)
        companies = list(first_page.get("companies") or [])
        total_pages = max(1, int(first_page.get("total_pages") or 1))
        effective_page_size = len(companies) or requested_page_size

        if limit is None:
            wanted = total_companies or None
        else:
            wanted = max(limit, 0)
            if total_companies:
                wanted = min(wanted, total_companies)

        if wanted is not None and len(companies) >= wanted:
            companies = companies[:wanted]
        elif total_pages > 1:
            pages_needed = total_pages if wanted is None else min(total_pages, math.ceil(wanted / effective_page_size))
            for page_number in range(2, pages_needed + 1):
                page_payload = self._parse_constituent_page(page_number=page_number, page_size=requested_page_size)
                companies.extend(page_payload.get("companies") or [])
                if wanted is not None and len(companies) >= wanted:
                    break

        constituents = dict(first_page)
        constituents["companies"] = companies[:wanted] if wanted is not None else companies
        constituents["returned_companies"] = len(constituents["companies"])
        if limit is not None:
            constituents["requested_limit"] = max(limit, 0)
        return constituents

    def shareholding_quarterly(self) -> list[dict[str, object]]:
        """Return quarterly shareholding data."""

        return self.shareholding(frequency="quarterly")

    def shareholding_yearly(self) -> list[dict[str, object]]:
        """Return yearly shareholding data."""

        return self.shareholding(frequency="yearly")

    def to_json(self, indent: int = 2, *, constituents_limit: int | None = None) -> str:
        """Return the full stock payload as formatted JSON text."""

        return json.dumps(self.all(constituents_limit=constituents_limit), indent=indent, ensure_ascii=False)

    def page_type(self) -> str:
        """Return the detected Screener page type: stock, index, or unknown."""

        if self._page_type is None:
            self._page_type = self._detect_page_type(self._get_page_html())
        return self._page_type

    def is_stock(self) -> bool:
        """Return True when the current Screener page looks like a stock page."""

        return self.page_type() == "stock"

    def is_index(self) -> bool:
        """Return True when the current Screener page looks like an index page."""

        return self.page_type() == "index"

    def pretty(self, section: str | None = None, *, constituents_limit: int | None = None) -> None:
        """Print one section or the full payload in a human-friendly layout."""

        if self._pretty_rich(section=section, constituents_limit=constituents_limit):
            return
        self._pretty_plain(section=section, constituents_limit=constituents_limit)

    def _pretty_plain(self, section: str | None = None, *, constituents_limit: int | None = None) -> None:
        """Fallback plain-text pretty printer used when Rich is unavailable."""

        section_names = self.available_sections()
        if section is None:
            try:
                payload = self.all(constituents_limit=constituents_limit)
            except SectionNotFoundError:
                payload = {
                    name: self._load_helper_section(name, allow_missing=True, constituents_limit=constituents_limit)
                    for name in section_names
                }

            for index, section_name in enumerate(section_names):
                if index:
                    print()
                self._print_formatted_section(section_name, payload.get(section_name))
            return

        canonical = self._canonical_helper_section(section)
        self._print_formatted_section(
            canonical,
            self._load_helper_section(canonical, allow_missing=True, constituents_limit=constituents_limit),
        )

    def print_section(self, section: str, *, constituents_limit: int | None = None) -> None:
        """Print one validated section in a human-friendly layout."""

        self.pretty(section=self._canonical_helper_section(section), constituents_limit=constituents_limit)

    def to_dataframe(self, section: str):
        """Convert a single section into a pandas DataFrame."""

        canonical = self._canonical_helper_section(section)
        try:
            pd = importlib.import_module("pandas")
        except ImportError as exc:
            raise ImportError("pandas is required for `to_dataframe()`. Install it with `pip install pandas`.") from exc

        section_data = self._load_helper_section(canonical, allow_missing=True)
        if canonical == "peers" and isinstance(section_data, dict) and isinstance(section_data.get("companies"), list):
            return pd.DataFrame(section_data["companies"])
        if canonical == "constituents" and isinstance(section_data, dict) and isinstance(section_data.get("companies"), list):
            return pd.DataFrame(section_data["companies"])
        if isinstance(section_data, list) and all(isinstance(item, dict) for item in section_data):
            return pd.DataFrame(section_data)
        if isinstance(section_data, dict):
            return pd.DataFrame([section_data])
        raise ValueError(f"Section '{canonical}' cannot be converted to a DataFrame.")

    def metadata(self) -> dict[str, object]:
        """Return package and source metadata for the current stock."""

        self._require_expected_page_type()
        payload: dict[str, object] = {
            "symbol": self.symbol,
            "consolidated": self.consolidated,
            "source": "screener.in",
            "entity_type": self.page_type(),
            "currency": "INR",
            "units": "crores",
        }
        try:
            summary = self.fetch("summary").get("summary")
        except SectionNotFoundError:
            summary = None
        if isinstance(summary, dict) and summary.get("company_name"):
            payload["company_name"] = summary["company_name"]
        return payload

    def fetch(self, sections: str | Iterable[str], *, constituents_limit: int | None = None) -> dict[str, object]:
        requested = [sections] if isinstance(sections, str) else list(sections)
        results: dict[str, object] = {}
        supported_sections = set(self.available_sections())
        for raw_name in requested:
            section = self._canonical_section(raw_name)
            if section not in supported_sections:
                raise KeyError(f"Section '{section}' is not available for {self.page_type()} pages.")
            if section == "summary":
                results[section] = self.summary()
            elif section == "analysis":
                results[section] = self.pros_cons()
            elif section == "peers":
                results[section] = self.peers()
            elif section == "quarterly_results":
                results[section] = self.quarterly_results()
            elif section == "profit_loss":
                results[section] = self.profit_loss()
            elif section == "balance_sheet":
                results[section] = self.balance_sheet()
            elif section == "cash_flow":
                results[section] = self.cash_flow()
            elif section == "ratios":
                results[section] = self.ratios()
            elif section == "shareholding":
                results[section] = self.shareholding()
            elif section == "constituents":
                results[section] = self.constituents(limit=constituents_limit)
        return results

    def all(self, *, constituents_limit: int | None = None) -> dict[str, object]:
        return self.fetch(self.available_sections(), constituents_limit=constituents_limit)

    def available_sections(self) -> list[str]:
        self._require_expected_page_type()
        return list(self._supported_sections())

    def _canonical_section(self, name: str) -> str:
        key = name.strip().lower()
        if key not in _SECTION_ALIASES:
            raise KeyError(f"Unsupported section '{name}'.")
        return _SECTION_ALIASES[key]

    def _canonical_helper_section(self, name: str) -> str:
        key = name.strip().lower()
        if key not in _HELPER_SECTION_ALIASES:
            supported = ", ".join(sorted(_HELPER_SECTION_ALIASES))
            raise ValueError(f"Unsupported section '{name}'. Supported sections: {supported}.")
        return _HELPER_SECTION_ALIASES[key]

    def _expected_page_type(self) -> str:
        return "stock"

    def _supported_sections(self) -> list[str]:
        return list(_STOCK_SECTIONS)

    def _require_expected_page_type(self) -> None:
        expected = self._expected_page_type()
        actual = self.page_type()
        if actual == expected:
            return
        if actual == "unknown":
            if expected == "stock":
                return
            raise EntityTypeMismatchError(f"'{self.symbol}' did not resolve to a {expected} page on Screener.in.")

        article = "an" if actual == "index" else "a"
        suggested_class = "Index" if actual == "index" else "Stock"
        raise EntityTypeMismatchError(
            f"'{self.symbol}' resolved to {article} {actual} page. Use {suggested_class}('{self.symbol}') instead."
        )

    def _require_section_available(self, section: str) -> None:
        self._require_expected_page_type()
        if section not in self._supported_sections():
            raise KeyError(f"Section '{section}' is not available for {self._expected_page_type()} pages.")

    def _load_helper_section(
        self,
        section: str,
        *,
        allow_missing: bool = False,
        constituents_limit: int | None = None,
    ) -> object:
        try:
            if section == "pros":
                return self.pros()
            if section == "cons":
                return self.cons()
            if section == "shareholding_quarterly":
                return self.shareholding_quarterly()
            if section == "shareholding_yearly":
                return self.shareholding_yearly()
            if section in _STOCK_SECTIONS or section in _INDEX_SECTIONS:
                return self.fetch(section, constituents_limit=constituents_limit).get(section)
        except (SectionNotFoundError, KeyError):
            if allow_missing:
                return None
            raise
        return None

    def _pretty_rich(self, section: str | None = None, *, constituents_limit: int | None = None) -> bool:
        rich = self._get_rich_components()
        if rich is None:
            return False

        console = rich["Console"]()
        section_names = self.available_sections()
        if section is None:
            try:
                payload = self.all(constituents_limit=constituents_limit)
            except SectionNotFoundError:
                payload = {
                    name: self._load_helper_section(name, allow_missing=True, constituents_limit=constituents_limit)
                    for name in section_names
                }

            for index, section_name in enumerate(section_names):
                if index:
                    console.print(rich["Rule"](style="grey35"))
                console.print(self._render_section_rich(section_name, payload.get(section_name), rich))
            return True

        canonical = self._canonical_helper_section(section)
        console.print(
            self._render_section_rich(
                canonical,
                self._load_helper_section(canonical, allow_missing=True, constituents_limit=constituents_limit),
                rich,
            )
        )
        return True

    def _get_rich_components(self) -> dict[str, object] | None:
        try:
            console_module = importlib.import_module("rich.console")
            columns_module = importlib.import_module("rich.columns")
            panel_module = importlib.import_module("rich.panel")
            rule_module = importlib.import_module("rich.rule")
            table_module = importlib.import_module("rich.table")
            text_module = importlib.import_module("rich.text")
        except ImportError:
            return None

        return {
            "Columns": columns_module.Columns,
            "Console": console_module.Console,
            "Group": console_module.Group,
            "Panel": panel_module.Panel,
            "Rule": rule_module.Rule,
            "Table": table_module.Table,
            "Text": text_module.Text,
        }

    def _render_section_rich(self, section: str, payload: object, rich: dict[str, object]):
        if section == "summary":
            summary = payload if isinstance(payload, dict) else {}
            if self.is_index():
                return self._render_index_top_card(summary, rich)
            return self._render_top_card(summary, rich)
        if section == "analysis":
            return self._render_pros_cons(self.pros(), self.cons(), rich)
        if section == "pros":
            return self._render_list_panel("PROS", payload, rich, border_style="green")
        if section == "cons":
            return self._render_list_panel("CONS", payload, rich, border_style="red")
        if section == "peers":
            return self._render_peers_section(payload if isinstance(payload, dict) else {}, rich)
        if section == "constituents":
            return self._render_constituents_section(payload if isinstance(payload, dict) else {}, rich)
        if section == "quarterly_results":
            return self._render_matrix_section(
                title="Quarterly Results",
                records=payload if isinstance(payload, list) else [],
                period_key="date",
                rows=_QUARTERLY_ROWS,
                rich=rich,
            )
        if section == "profit_loss":
            return self._render_profit_loss_section(payload if isinstance(payload, list) else [], rich)
        if section == "balance_sheet":
            return self._render_matrix_section(
                title="Balance Sheet",
                records=payload if isinstance(payload, list) else [],
                period_key="year",
                rows=_BALANCE_SHEET_ROWS,
                rich=rich,
            )
        if section == "cash_flow":
            return self._render_matrix_section(
                title="Cash Flow",
                records=payload if isinstance(payload, list) else [],
                period_key="year",
                rows=_CASH_FLOW_ROWS,
                rich=rich,
            )
        if section == "ratios":
            return self._render_ratios_section(payload if isinstance(payload, dict) else {}, rich)
        if section == "shareholding":
            return self._render_shareholding_section(
                quarterly=payload if isinstance(payload, list) else [],
                yearly=self.shareholding_yearly(),
                rich=rich,
            )
        if section == "shareholding_quarterly":
            return self._render_shareholding_section(quarterly=payload if isinstance(payload, list) else [], yearly=[], rich=rich)
        if section == "shareholding_yearly":
            return self._render_shareholding_section(quarterly=[], yearly=payload if isinstance(payload, list) else [], rich=rich)
        return self._render_empty_panel(self._format_title(section), rich)

    def _render_top_card(self, summary: dict[str, object], rich: dict[str, object]):
        Columns = rich["Columns"]
        Group = rich["Group"]
        Panel = rich["Panel"]
        Rule = rich["Rule"]
        Table = rich["Table"]
        Text = rich["Text"]

        title = Text(summary.get("company_name") or self.symbol, style="bold white")
        price_line = Text(self._format_currency(summary.get("current_price")), style="bold bright_white")
        change = summary.get("price_change_percent")
        if isinstance(change, (int, float)):
            sign = "+" if change > 0 else ""
            style = "green" if change > 0 else "red" if change < 0 else "yellow"
            price_line.append(f"  {sign}{self._format_number(change)}%", style=style)
        price_date = summary.get("price_date")
        if price_date:
            price_line.append(f"  {price_date}", style="dim")

        meta_bits = []
        if summary.get("website"):
            meta_bits.append(str(summary["website"]))
        if summary.get("bse_code"):
            meta_bits.append(f"BSE {summary['bse_code']}")
        if summary.get("nse_symbol"):
            meta_bits.append(f"NSE {summary['nse_symbol']}")
        meta_line = Text(" | ".join(meta_bits), style="dim") if meta_bits else Text("")

        metrics = Table.grid(expand=True)
        metrics.add_column(style="dim")
        metrics.add_column()
        metrics.add_column(style="dim")
        metrics.add_column()
        metrics.add_column(style="dim")
        metrics.add_column()
        ratios = summary.get("ratios") if isinstance(summary.get("ratios"), dict) else {}
        for metric_slice in [list(_TOP_CARD_METRICS[index : index + 3]) for index in range(0, len(_TOP_CARD_METRICS), 3)]:
            row: list[str] = []
            for key, label in metric_slice:
                value = ratios.get(key) if isinstance(ratios, dict) else None
                row.extend([label, self._format_display_value(key, value)])
            while len(row) < 6:
                row.extend(["", ""])
            metrics.add_row(*row)

        narrative_panels = []
        if summary.get("about"):
            narrative_panels.append(Panel(str(summary["about"]), title="About", border_style="cyan"))
        if summary.get("key_points"):
            narrative_panels.append(Panel(str(summary["key_points"]), title="Key Points", border_style="magenta"))

        body = [title, price_line]
        if meta_bits:
            body.append(meta_line)
        body.extend([Rule(style="grey30"), Panel(metrics, title="Key Metrics", border_style="blue")])
        if narrative_panels:
            body.extend([Rule(style="grey30"), Columns(narrative_panels, expand=True)])
        return Panel(Group(*body), title="Overview", border_style="bright_blue", padding=(1, 1))

    def _render_index_top_card(self, summary: dict[str, object], rich: dict[str, object]):
        Columns = rich["Columns"]
        Group = rich["Group"]
        Panel = rich["Panel"]
        Rule = rich["Rule"]
        Table = rich["Table"]
        Text = rich["Text"]

        title = Text(summary.get("company_name") or self.symbol, style="bold white")
        price_line = Text(self._format_currency(summary.get("current_price")), style="bold bright_white")
        change = summary.get("price_change_percent")
        if isinstance(change, (int, float)):
            sign = "+" if change > 0 else ""
            style = "green" if change > 0 else "red" if change < 0 else "yellow"
            price_line.append(f"  {sign}{self._format_number(change)}%", style=style)
        price_date = summary.get("price_date")
        if price_date:
            price_line.append(f"  {price_date}", style="dim")

        metrics = Table.grid(expand=True)
        metrics.add_column(style="dim")
        metrics.add_column()
        metrics.add_column(style="dim")
        metrics.add_column()
        metrics.add_column(style="dim")
        metrics.add_column()
        ratios = summary.get("ratios") if isinstance(summary.get("ratios"), dict) else {}
        for metric_slice in [
            list(_INDEX_TOP_CARD_METRICS[index : index + 3]) for index in range(0, len(_INDEX_TOP_CARD_METRICS), 3)
        ]:
            row: list[str] = []
            for key, label in metric_slice:
                value = ratios.get(key) if isinstance(ratios, dict) else None
                row.extend([label, self._format_display_value(key, value)])
            while len(row) < 6:
                row.extend(["", ""])
            metrics.add_row(*row)

        body = [title, price_line, Rule(style="grey30"), Panel(metrics, title="Index Metrics", border_style="blue")]
        if summary.get("about"):
            body.extend([Rule(style="grey30"), Columns([Panel(str(summary["about"]), title="About", border_style="cyan")], expand=True)])
        return Panel(Group(*body), title="Index Overview", border_style="bright_blue", padding=(1, 1))

    def _render_pros_cons(self, pros: list[str], cons: list[str], rich: dict[str, object]):
        Columns = rich["Columns"]
        Group = rich["Group"]

        return Group(
            self._render_rule("Pros & Cons", rich),
            Columns(
                [
                    self._render_list_panel("PROS", pros, rich, border_style="green"),
                    self._render_list_panel("CONS", cons, rich, border_style="red"),
                ],
                expand=True,
            ),
        )

    def _render_peers_section(self, peers: dict[str, object], rich: dict[str, object]):
        Group = rich["Group"]
        Panel = rich["Panel"]
        Table = rich["Table"]

        companies = peers.get("companies") if isinstance(peers.get("companies"), list) else []
        table = Table(expand=True, header_style="bold white")
        for _, label in _PEER_COLUMNS:
            justify = "left" if label in {"Name"} else "right"
            table.add_column(label, justify=justify)
        for company in companies:
            table.add_row(*[self._format_display_value(key, company.get(key)) for key, _ in _PEER_COLUMNS])

        renderables = [Panel(table, title="Peer Comparison", border_style="blue")]
        median = peers.get("median")
        if isinstance(median, dict):
            summary = Table.grid(expand=True)
            summary.add_column(style="dim")
            summary.add_column()
            for key, label in _PEER_COLUMNS[2:]:
                if key in median:
                    summary.add_row(label, self._format_display_value(key, median.get(key)))
            renderables.append(Panel(summary, title="Median", border_style="grey50"))
        return Group(*renderables)

    def _render_constituents_section(self, payload: dict[str, object], rich: dict[str, object]):
        Group = rich["Group"]
        Panel = rich["Panel"]
        Table = rich["Table"]

        companies = payload.get("companies") if isinstance(payload.get("companies"), list) else []
        table = Table(expand=True, header_style="bold white")
        for _, label in _CONSTITUENT_COLUMNS:
            table.add_column(label, justify="left" if label in {"Name", "Symbol"} else "right")
        for company in companies:
            table.add_row(*[self._format_display_value(key, company.get(key)) for key, _ in _CONSTITUENT_COLUMNS])

        title_bits = []
        returned = payload.get("returned_companies")
        total = payload.get("total_companies")
        if isinstance(returned, int) and isinstance(total, int) and total:
            title_bits.append(f"{returned} of {total} companies")
        elif isinstance(returned, int):
            title_bits.append(f"{returned} companies")
        if isinstance(payload.get("page"), int) and isinstance(payload.get("total_pages"), int):
            title_bits.append(f"pages {payload['page']}/{payload['total_pages']}")

        renderables = [Panel(table, title="Constituents", subtitle=" | ".join(title_bits), border_style="blue")]
        median = payload.get("median")
        if isinstance(median, dict):
            summary = Table.grid(expand=True)
            summary.add_column(style="dim")
            summary.add_column()
            label = median.get("label")
            if label:
                summary.add_row("Label", str(label))
            for key, display in _CONSTITUENT_COLUMNS[3:]:
                if key in median:
                    summary.add_row(display, self._format_display_value(key, median.get(key)))
            renderables.append(Panel(summary, title="Median", border_style="grey50"))
        return Group(*renderables)

    def _render_profit_loss_section(self, records: list[dict[str, object]], rich: dict[str, object]):
        Columns = rich["Columns"]
        Group = rich["Group"]
        Panel = rich["Panel"]

        cards = []
        for title, value in self._profit_loss_highlights(records):
            cards.append(Panel(value, title=title, border_style="cyan"))

        renderables = [
            self._render_matrix_section(
                title="Profit & Loss",
                records=records,
                period_key="year",
                rows=_PROFIT_LOSS_ROWS,
                rich=rich,
            )
        ]
        if cards:
            renderables.append(Columns(cards, expand=True))
        return Group(*renderables)

    def _render_ratios_section(self, payload: dict[str, object], rich: dict[str, object]):
        Panel = rich["Panel"]
        Table = rich["Table"]

        table = Table(expand=True, header_style="bold white")
        period = str(payload.get("year") or "Value")
        table.add_column("Metric")
        table.add_column(period, justify="right")
        for key, label in _RATIO_ROWS:
            if key in payload:
                table.add_row(label, self._format_display_value(key, payload.get(key)))
        return Panel(table, title="Ratios", border_style="blue")

    def _render_shareholding_section(self, quarterly: list[dict[str, object]], yearly: list[dict[str, object]], rich: dict[str, object]):
        Group = rich["Group"]

        renderables = []
        if quarterly:
            renderables.append(
                self._render_matrix_section(
                    title="Shareholding Pattern (Quarterly)",
                    records=quarterly,
                    period_key="date",
                    rows=_SHAREHOLDING_ROWS,
                    rich=rich,
                )
            )
        if yearly:
            renderables.append(
                self._render_matrix_section(
                    title="Shareholding Pattern (Yearly)",
                    records=yearly,
                    period_key="date",
                    rows=_SHAREHOLDING_ROWS,
                    rich=rich,
                )
            )
        if not renderables:
            return self._render_empty_panel("Shareholding Pattern", rich)
        return Group(*renderables)

    def _render_matrix_section(
        self,
        *,
        title: str,
        records: list[dict[str, object]],
        period_key: str,
        rows: list[tuple[str, str]],
        rich: dict[str, object],
    ):
        Panel = rich["Panel"]
        Table = rich["Table"]

        if not records:
            return self._render_empty_panel(title, rich)

        table = Table(expand=True, header_style="bold white")
        table.add_column("Metric", style="bold", no_wrap=True)
        periods = [self._stringify(record.get(period_key)) for record in records]
        for period in periods:
            table.add_column(period, justify="right")

        for key, label in rows:
            if not any(key in record for record in records):
                continue
            table.add_row(label, *[self._format_display_value(key, record.get(key)) for record in records])
        return Panel(table, title=title, border_style="blue")

    def _render_list_panel(self, title: str, items: object, rich: dict[str, object], *, border_style: str):
        Panel = rich["Panel"]
        Text = rich["Text"]

        body = Text()
        if isinstance(items, list) and items:
            for index, item in enumerate(items):
                if index:
                    body.append("\n")
                body.append("• ", style=border_style)
                body.append(str(item))
        else:
            body.append("No data", style="dim")
        return Panel(body, title=title, border_style=border_style)

    def _render_rule(self, title: str, rich: dict[str, object]):
        return rich["Rule"](title, style="grey35")

    def _render_empty_panel(self, title: str, rich: dict[str, object]):
        return rich["Panel"]("No data", title=title, border_style="grey50")

    def _profit_loss_highlights(self, records: list[dict[str, object]]) -> list[tuple[str, str]]:
        filtered = [record for record in records if str(record.get("year")) != "TTM"]
        highlights = [
            ("Compounded Sales Growth", self._format_percent(self._compute_cagr(filtered, "sales"))),
            ("Compounded Profit Growth", self._format_percent(self._compute_cagr(filtered, "net_profit"))),
            ("Stock Price CAGR", "N/A"),
        ]
        roe = None
        summary = self._load_helper_section("summary", allow_missing=True)
        if isinstance(summary, dict) and isinstance(summary.get("ratios"), dict):
            roe = summary["ratios"].get("roe_percent")
        highlights.append(("Return On Equity", self._format_percent(roe)))
        return highlights

    def _compute_cagr(self, records: list[dict[str, object]], key: str) -> float | None:
        values = [record.get(key) for record in records if isinstance(record.get(key), (int, float)) and record.get(key) not in {0}]
        if len(values) < 2:
            return None
        start = float(values[0])
        end = float(values[-1])
        periods = len(values) - 1
        if start <= 0 or end <= 0 or periods <= 0:
            return None
        return ((end / start) ** (1 / periods) - 1) * 100

    def _format_display_value(self, key: str, value: object) -> str:
        if key == "high_low" and isinstance(value, dict):
            high = self._format_currency(value.get("high"))
            low = self._format_currency(value.get("low"))
            return f"{high} / {low}"
        if key in _PERCENT_KEYS:
            return self._format_percent(value)
        if key in _CURRENCY_KEYS:
            return self._format_currency(value)
        if isinstance(value, (int, float)):
            return self._format_number(value)
        return self._stringify(value)

    def _format_number(self, value: object) -> str:
        if not isinstance(value, (int, float)):
            return self._stringify(value)
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, int):
            return f"{value:,}"
        return f"{value:,.2f}".rstrip("0").rstrip(".")

    def _format_percent(self, value: object) -> str:
        if value is None:
            return "N/A"
        return f"{self._format_number(value)}%"

    def _format_currency(self, value: object) -> str:
        if value is None:
            return "N/A"
        return f"₹{self._format_number(value)}"

    def _print_formatted_section(self, name: str, payload: object) -> None:
        print(self._format_title(name))
        for line in self._format_value(payload):
            print(line)

    def _format_value(self, value: object, *, indent: int = 1) -> list[str]:
        if value is None:
            return [self._indent(indent) + "No data"]
        if isinstance(value, dict):
            return self._format_dict(value, indent=indent)
        if isinstance(value, list):
            if not value:
                return [self._indent(indent) + "No data"]
            if all(isinstance(item, dict) for item in value):
                return self._format_list_of_dicts(value, indent=indent)
            if all(isinstance(item, str) for item in value):
                return self._format_list_of_strings(value, indent=indent)
        return [self._indent(indent) + self._stringify(value)]

    def _format_dict(self, payload: dict[str, object], *, indent: int = 1) -> list[str]:
        if not payload:
            return [self._indent(indent) + "No data"]

        lines: list[str] = []
        for key, value in payload.items():
            prefix = self._indent(indent)
            label = self._format_title(key)
            if isinstance(value, dict):
                lines.append(f"{prefix}{label}:")
                lines.extend(self._format_dict(value, indent=indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{label}:")
                if value and all(isinstance(item, dict) for item in value):
                    lines.extend(self._format_list_of_dicts(value, indent=indent + 1))
                elif value and all(isinstance(item, str) for item in value):
                    lines.extend(self._format_list_of_strings(value, indent=indent + 1))
                else:
                    lines.extend(self._format_value(value or None, indent=indent + 1))
            else:
                lines.append(f"{prefix}{label}: {self._stringify(value)}")
        return lines

    def _format_list_of_dicts(self, rows: list[dict[str, object]], *, indent: int = 1) -> list[str]:
        if not rows:
            return [self._indent(indent) + "No data"]

        columns: list[str] = []
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(key)

        headers = {column: self._format_title(column) for column in columns}
        widths = {column: len(headers[column]) for column in columns}
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            normalized_row: dict[str, str] = {}
            for column in columns:
                normalized_row[column] = self._stringify(row.get(column))
                widths[column] = max(widths[column], len(normalized_row[column]))
            normalized_rows.append(normalized_row)

        prefix = self._indent(indent)
        header = prefix + " | ".join(f"{headers[column]:<{widths[column]}}" for column in columns)
        divider = prefix + "-+-".join("-" * widths[column] for column in columns)
        lines = [header, divider]
        for row in normalized_rows:
            lines.append(prefix + " | ".join(f"{row[column]:<{widths[column]}}" for column in columns))
        return lines

    def _format_list_of_strings(self, items: list[str], *, indent: int = 1) -> list[str]:
        if not items:
            return [self._indent(indent) + "No data"]
        prefix = self._indent(indent)
        return [f"{prefix}- {item}" for item in items]

    def _format_title(self, value: str) -> str:
        return value.replace("-", " ").replace("_", " ").title()

    def _indent(self, level: int) -> str:
        return "  " * level

    def _stringify(self, value: object) -> str:
        if value is None:
            return "N/A"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _parse_constituent_page(self, *, page_number: int, page_size: int) -> dict[str, object]:
        html = self._get_constituent_page_html(page_number=page_number, page_size=page_size)
        return parse_constituents(html)

    def _get_constituent_page_html(self, *, page_number: int, page_size: int) -> str:
        if self._constituent_pages is None:
            self._constituent_pages = {}

        cache_key = (page_number, page_size)
        if cache_key in self._constituent_pages:
            return self._constituent_pages[cache_key]

        if page_number == 1 and page_size == 50 and self.page_type() == "index":
            fetch_constituent_pages = getattr(self.scraper, "fetch_constituent_pages", None)
            if callable(fetch_constituent_pages):
                html = fetch_constituent_pages(self.symbol, page_numbers=[1], page_size=page_size)[0]
            else:
                html = self._get_page_html()
        else:
            fetch_constituent_pages = getattr(self.scraper, "fetch_constituent_pages", None)
            if callable(fetch_constituent_pages):
                html = fetch_constituent_pages(self.symbol, page_numbers=[page_number], page_size=page_size)[0]
            else:
                html = self._get_page_html()

        self._constituent_pages[cache_key] = html
        return html

    def _detect_page_type(self, html: str) -> str:
        if any(marker in html for marker in _STOCK_PAGE_MARKERS):
            return "stock"
        if any(marker in html for marker in _INDEX_PAGE_MARKERS):
            return "index"
        return "unknown"

    def _get_page_html(self) -> str:
        if self.page_html is None:
            self.page_html = self.scraper.fetch_page(self.symbol)
        return self.page_html
