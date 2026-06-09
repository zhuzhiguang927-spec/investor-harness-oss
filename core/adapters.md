# Data Adapters

This file defines public data-source priority for Investor Harness qualitative research. Individual skills may maintain their own helper scripts for structured data, but final claims should follow this source discipline.

## General Priority

1. **Broker / sell-side research reports**: recent five-year report text, PDF, or public reposts.
2. **Official disclosures**: annual reports, quarterly reports, exchange filings, company announcements, investor relations materials, SEC / HKEX / exchange filings where relevant.
3. **Structured market and financial data**: prices, valuation, financial statements, shareholder data, events, industry indicators, and comparable-company data from configured local tools or public sources.
4. **Chinese web search and broader web search**: used to fill gaps, find reposted report text, and verify recent developments.
5. **User-provided materials**: pasted documents, notes, models, transcripts, or screenshots.

Do not rely only on snippets, ratings, target prices, PE tables, or earnings forecast summaries. Read the report body or source disclosure when available.

## Market Branches

### A Shares

- Prefer Eastmoney / dfcfw broker report text or PDF when available.
- Use official announcements and financial reports as factual anchors.
- Use configured structured-data tools only when available; otherwise state the gap.
- Use `cn-web-search` and broader web search for missing report text, recent news, and context.

### Hong Kong Stocks

- Prefer official HKEX disclosures, company IR materials, and public broker reports.
- Use structured global-stock or market-data tools when available.
- Flag accounting, currency, and reporting-period differences in cross-market comparisons.

### US Stocks

- Prefer SEC filings, company IR materials, and public broker / industry reports.
- Use structured global-stock or market-data tools when available.
- Treat analyst ratings and price targets as market views, not facts.

### Global Themes / Industries

- Combine industry reports, representative company disclosures, public industry data, and web search.
- Explain market boundaries before selecting companies.

## Evidence Handling

Use evidence labels where helpful:

- `公开事实`
- `财报披露`
- `市场共识`
- `合理推演`
- `待核验假设`

Only mention source weakness in the final report when it affects the conclusion.
