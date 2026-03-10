from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


_SECTIONS = {
    "top": """
<section id="top">
  <h1>Tata Consultancy Services Ltd</h1>
  <div class="font-size-18">
    <span>₹2,527</span>
    <span>1.2%</span>
  </div>
  <div class="font-size-11">Mar 10, 2026 - close price</div>
  <div class="about">Large-cap IT services company.</div>
  <div class="commentary">Strong cash generation and high returns on capital.</div>
  <a href="https://www.tcs.com">TCS</a>
  <a href="https://www.bseindia.com">BSE: 532540</a>
  <a href="https://www.nseindia.com">NSE: TCS</a>
  <ul id="top-ratios">
    <li><span class="name">Market Cap</span><span class="value">914,418</span></li>
    <li><span class="name">Current Price</span><span class="value">₹2,527</span></li>
    <li><span class="name">High / Low</span><span class="value">₹3,710 / ₹2,505</span></li>
    <li><span class="name">Stock P/E</span><span class="value">18.7</span></li>
    <li><span class="name">Book Value</span><span class="value">₹234.0</span></li>
    <li><span class="name">Dividend Yield</span><span class="value">1.2%</span></li>
    <li><span class="name">ROCE</span><span class="value">78%</span></li>
    <li><span class="name">ROE</span><span class="value">65%</span></li>
    <li><span class="name">Face Value</span><span class="value">₹1</span></li>
  </ul>
</section>
""".strip(),
    "analysis": """
<section id="analysis">
  <div class="pros">
    <ul>
      <li>Company has a good return on equity (ROE) track record: 3 Years ROE 58.9%</li>
      <li>Company has been maintaining a healthy dividend payout.</li>
    </ul>
  </div>
  <div class="cons">
    <ul>
      <li>Stock is trading at 10.8 times its book value</li>
    </ul>
  </div>
</section>
""".strip(),
    "peers": """
<section id="peers">
  <div id="benchmarks">
    <a>Nifty 50</a>
    <a>Nifty IT</a>
  </div>
  <table class="data-table">
    <tr>
      <th>S.No</th>
      <th>Name</th>
      <th>CMP</th>
      <th>P/E</th>
      <th>Mar Cap</th>
      <th>Div Yld</th>
      <th>NP Qtr</th>
      <th>Qtr Profit Var</th>
      <th>Sales Qtr</th>
      <th>Qtr Sales Var</th>
      <th>ROCE</th>
    </tr>
    <tr>
      <td>1</td>
      <td>TCS</td>
      <td>2527.4</td>
      <td>18.7</td>
      <td>914418</td>
      <td>1.2</td>
      <td>10190</td>
      <td>9.8</td>
      <td>55567</td>
      <td>6.1</td>
      <td>78</td>
    </tr>
  </table>
</section>
""".strip(),
    "quarters": """
<section id="quarters">
  <table class="data-table">
    <thead>
      <tr><th>Metric</th><th>Dec 2022</th><th>Mar 2025</th><th>Dec 2025</th></tr>
    </thead>
    <tbody>
      <tr><td>Sales +</td><td>48,000</td><td>54,300</td><td>55,567</td></tr>
      <tr><td>Expenses +</td><td>35,000</td><td>39,000</td><td>39,950</td></tr>
      <tr><td>Operating Profit</td><td>13,000</td><td>15,300</td><td>15,617</td></tr>
      <tr><td>OPM %</td><td>27.1</td><td>28.2</td><td>28.1</td></tr>
      <tr><td>Other Income</td><td>900</td><td>1,000</td><td>1,050</td></tr>
      <tr><td>Interest</td><td>40</td><td>38</td><td>35</td></tr>
      <tr><td>Depreciation</td><td>500</td><td>540</td><td>560</td></tr>
      <tr><td>Profit Before Tax</td><td>13,360</td><td>15,722</td><td>16,072</td></tr>
      <tr><td>Tax %</td><td>24</td><td>24.5</td><td>24.6</td></tr>
      <tr><td>Net Profit +</td><td>8,100</td><td>9,880</td><td>10,190</td></tr>
      <tr><td>EPS in Rs</td><td>40</td><td>49</td><td>51</td></tr>
    </tbody>
  </table>
</section>
""".strip(),
    "profit-loss": """
<section id="profit-loss">
  <table class="data-table">
    <thead>
      <tr><th>Metric</th><th>Mar 2023</th><th>Mar 2025</th><th>TTM</th></tr>
    </thead>
    <tbody>
      <tr><td>Sales +</td><td>100,000</td><td>121,000</td><td>130,000</td></tr>
      <tr><td>Expenses +</td><td>72,000</td><td>85,000</td><td>90,000</td></tr>
      <tr><td>Operating Profit</td><td>28,000</td><td>36,000</td><td>40,000</td></tr>
      <tr><td>OPM %</td><td>28</td><td>29.8</td><td>30.8</td></tr>
      <tr><td>Other Income</td><td>1,800</td><td>2,200</td><td>2,300</td></tr>
      <tr><td>Interest</td><td>80</td><td>75</td><td>70</td></tr>
      <tr><td>Depreciation</td><td>900</td><td>980</td><td>1,000</td></tr>
      <tr><td>Profit Before Tax</td><td>28,820</td><td>37,145</td><td>41,230</td></tr>
      <tr><td>Tax %</td><td>24</td><td>24.2</td><td>24.1</td></tr>
      <tr><td>Net Profit +</td><td>21,900</td><td>28,500</td><td>31,200</td></tr>
      <tr><td>EPS in Rs</td><td>108</td><td>141</td><td>154</td></tr>
      <tr><td>Dividend Payout</td><td>42</td><td>45</td><td>--</td></tr>
    </tbody>
  </table>
</section>
""".strip(),
    "balance-sheet": """
<section id="balance-sheet">
  <table class="data-table">
    <thead>
      <tr><th>Metric</th><th>Mar 2023</th><th>Sep 2025</th></tr>
    </thead>
    <tbody>
      <tr><td>Equity Capital</td><td>366</td><td>366</td></tr>
      <tr><td>Reserves</td><td>55,000</td><td>64,000</td></tr>
      <tr><td>Borrowings +</td><td>0</td><td>0</td></tr>
      <tr><td>Other Liabilities +</td><td>17,500</td><td>18,200</td></tr>
      <tr><td>Total Liabilities</td><td>72,866</td><td>82,566</td></tr>
      <tr><td>Fixed Assets +</td><td>8,000</td><td>8,600</td></tr>
      <tr><td>CWIP</td><td>500</td><td>600</td></tr>
      <tr><td>Investments</td><td>31,000</td><td>36,000</td></tr>
      <tr><td>Other Assets +</td><td>33,366</td><td>37,366</td></tr>
      <tr><td>Total Assets</td><td>72,866</td><td>82,566</td></tr>
    </tbody>
  </table>
</section>
""".strip(),
    "cash-flow": """
<section id="cash-flow">
  <table class="data-table">
    <thead>
      <tr><th>Metric</th><th>Mar 2023</th><th>Mar 2025</th></tr>
    </thead>
    <tbody>
      <tr><td>Cash From Operating Activity +</td><td>25,000</td><td>31,000</td></tr>
      <tr><td>Cash From Investing Activity +</td><td>(5,000)</td><td>(6,000)</td></tr>
      <tr><td>Cash From Financing Activity +</td><td>(10,000)</td><td>(12,000)</td></tr>
      <tr><td>Net Cash Flow</td><td>10,000</td><td>13,000</td></tr>
    </tbody>
  </table>
</section>
""".strip(),
    "ratios": """
<section id="ratios">
  <table class="data-table">
    <thead>
      <tr><th>Metric</th><th>Mar 2023</th><th>Mar 2025</th></tr>
    </thead>
    <tbody>
      <tr><td>Debtor Days</td><td>90</td><td>88</td></tr>
      <tr><td>Inventory Days</td><td>2</td><td>1</td></tr>
      <tr><td>Days Payable</td><td>18</td><td>17</td></tr>
      <tr><td>Cash Conversion Cycle</td><td>72</td><td>71</td></tr>
      <tr><td>Working Capital Days</td><td>45</td><td>43</td></tr>
      <tr><td>ROCE %</td><td>74</td><td>78</td></tr>
    </tbody>
  </table>
</section>
""".strip(),
    "shareholding": """
<section id="shareholding">
  <section id="quarterly-shp">
    <table class="data-table">
      <thead>
        <tr><th>Metric</th><th>Dec 2024</th><th>Dec 2025</th></tr>
      </thead>
      <tbody>
        <tr><td>Promoters +</td><td>71.80</td><td>71.77</td></tr>
        <tr><td>FIIs +</td><td>12.2</td><td>12.5</td></tr>
        <tr><td>DIIs +</td><td>8.1</td><td>8.4</td></tr>
        <tr><td>Government</td><td>0</td><td>0</td></tr>
        <tr><td>Public +</td><td>7.9</td><td>7.33</td></tr>
        <tr><td>No. of Shareholders</td><td>1000000</td><td>1010000</td></tr>
      </tbody>
    </table>
  </section>
  <section id="yearly-shp">
    <table class="data-table">
      <thead>
        <tr><th>Metric</th><th>Dec 2024</th><th>Dec 2025</th></tr>
      </thead>
      <tbody>
        <tr><td>Promoters +</td><td>71.80</td><td>71.77</td></tr>
        <tr><td>FIIs +</td><td>12.2</td><td>12.5</td></tr>
        <tr><td>DIIs +</td><td>8.1</td><td>8.4</td></tr>
        <tr><td>Government</td><td>0</td><td>0</td></tr>
        <tr><td>Public +</td><td>7.9</td><td>7.33</td></tr>
        <tr><td>No. of Shareholders</td><td>1000000</td><td>1010000</td></tr>
      </tbody>
    </table>
  </section>
</section>
""".strip(),
}


def load_sections() -> dict[str, str]:
    return dict(_SECTIONS)


def load_full_html() -> str:
    from openscreener.parsers._helpers import build_fixture_page

    return build_fixture_page(load_sections())


def load_index_html(*, page: int = 1, page_size: int = 50, total_companies: int = 75) -> str:
    total_pages = max(1, math.ceil(total_companies / page_size))
    start = ((page - 1) * page_size) + 1
    end = min(total_companies, page * page_size)

    rows = []
    for index in range(start, end + 1):
        rows.append(
            f"""
        <tr data-row-company-id="{1000 + index}">
          <td class="text">{index}.</td>
          <td class="text"><a href="/company/COMP{index}/" target="_blank">Company {index}</a></td>
          <td>{1000 + index}.0</td>
          <td>{20 + (index % 10)}</td>
          <td>{50000 + index}</td>
          <td>{1 + (index % 5) / 10:.2f}</td>
          <td>{200 + index}</td>
          <td>{5 + (index % 7):.2f}</td>
          <td>{500 + index}</td>
          <td>{4 + (index % 6):.2f}</td>
          <td>{10 + (index % 9):.2f}</td>
        </tr>
""".rstrip()
        )

    return f"""
<html>
  <body>
    <section id="top">
      <h1>Nifty 50</h1>
      <div class="font-size-18">
        <span>₹24,262</span>
        <span>0.07%</span>
      </div>
      <div class="font-size-11">Mar 10, 2026 - close price</div>
      <div class="about">Benchmark Indian stock market index covering 50 large NSE companies.</div>
      <ul id="top-ratios">
        <li><span class="name">Market Cap</span><span class="value">1,93,99,980</span></li>
        <li><span class="name">Current Price</span><span class="value">₹24,262</span></li>
        <li><span class="name">High / Low</span><span class="value">₹26,373 / ₹21,744</span></li>
        <li><span class="name">P/E</span><span class="value">21.2</span></li>
        <li><span class="name">Price to Book value</span><span class="value">3.30</span></li>
        <li><span class="name">Dividend Yield</span><span class="value">1.29%</span></li>
        <li><span class="name">CAGR 1Yr</span><span class="value">7.51%</span></li>
        <li><span class="name">CAGR 5Yr</span><span class="value">9.83%</span></li>
        <li><span class="name">CAGR 10Yr</span><span class="value">12.4%</span></li>
      </ul>
    </section>
    <section id="constituents">
      <h2>Companies in Nifty 50</h2>
      <div class="sub">{total_companies} results found: Showing page {page} of {total_pages}</div>
      <table class="data-table">
        <tbody>
          <tr>
            <th>S.No.</th>
            <th>Name</th>
            <th>CMP Rs.</th>
            <th>P/E</th>
            <th>Mar Cap Rs.Cr.</th>
            <th>Div Yld %</th>
            <th>NP Qtr Rs.Cr.</th>
            <th>Qtr Profit Var %</th>
            <th>Sales Qtr Rs.Cr.</th>
            <th>Qtr Sales Var %</th>
            <th>ROCE %</th>
          </tr>
          {''.join(rows)}
        </tbody>
        <tfoot>
          <tr>
            <td></td>
            <td>Median: {total_companies} Co.</td>
            <td>1314.65</td>
            <td>29.63</td>
            <td>287277.48</td>
            <td>0.85</td>
            <td>2896.38</td>
            <td>9.62</td>
            <td>24187.69</td>
            <td>10.91</td>
            <td>14.64</td>
          </tr>
        </tfoot>
      </table>
    </section>
  </body>
</html>
""".strip()


class FakeScraper:
    def __init__(
        self,
        pages: dict[str, str] | None = None,
        constituent_pages: dict[str, dict[tuple[int, int], str]] | None = None,
    ) -> None:
        raw_pages = pages or {"TCS": load_full_html()}
        self.pages = {symbol.upper(): html for symbol, html in raw_pages.items()}
        self.constituent_pages = {
            symbol.upper(): dict(page_map) for symbol, page_map in (constituent_pages or {}).items()
        }
        self.fetch_page_calls = 0
        self.fetch_pages_calls = 0
        self.fetch_constituent_pages_calls = 0

    def fetch_page(self, symbol: str) -> str:
        self.fetch_page_calls += 1
        return self.pages[symbol.upper()]

    def fetch_pages(self, symbols: list[str]) -> dict[str, str]:
        self.fetch_pages_calls += 1
        return {symbol.upper(): self.pages[symbol.upper()] for symbol in symbols}

    def fetch_constituent_pages(self, symbol: str, *, page_numbers: list[int], page_size: int = 50) -> list[str]:
        self.fetch_constituent_pages_calls += 1
        symbol_key = symbol.upper()
        page_map = self.constituent_pages.get(symbol_key, {})
        fallback = self.pages[symbol_key]
        return [page_map.get((page_number, page_size), fallback) for page_number in page_numbers]
