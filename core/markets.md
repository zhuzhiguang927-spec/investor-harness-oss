# Markets

Investor Harness covers public-market research workflows.

## Supported Markets

| Label | Market | Recognition Hints | Primary Public Sources |
|---|---|---|---|
| `CN-A` | A shares | 6-digit tickers, Chinese company names, Shanghai / Shenzhen / Beijing exchanges | broker reports, exchange filings, company announcements, financial reports, structured data, Chinese web search |
| `CN-FUND` | China public funds | 6-digit fund codes, fund names | fund disclosures, fund manager materials, structured fund data, Chinese web search |
| `HK` | Hong Kong stocks | 4-5 digit tickers, HKEX, H-share references | HKEX disclosures, company IR, broker reports, structured global-stock data, web search |
| `US` | US stocks | letter tickers, NYSE / NASDAQ, SEC filings | SEC filings, company IR, broker reports, structured global-stock data, web search |
| `GLOBAL` | Global themes | industry, macro, or cross-market themes | mixed public sources across relevant markets |

## Recognition Rules

1. If the user specifies a market, use it.
2. If the user gives a ticker, infer from ticker format.
3. If the user gives a Chinese company name, default to `CN-A` unless HK / H-share context is present.
4. If the user gives an English company name or ticker, default to `US` unless otherwise specified.
5. If the user asks for an industry or theme, use `GLOBAL` and define the relevant market scope.

## Cross-Market Caution

When comparing across markets, explicitly handle:

- currency
- accounting standards
- fiscal year and reporting period
- disclosure frequency
- liquidity and valuation convention
