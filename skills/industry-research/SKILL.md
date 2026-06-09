---
name: industry-research
description: >
  Industry, sector, theme, and value-chain research workflow. Use this skill when the user asks for an industry framework,
  sector map, value-chain map, market landscape, or deep industry report.
inputs:
  - Industry, sector, theme, or value-chain name
  - Optional market scope, company pool, user focus, or pasted materials
outputs:
  - Complete Markdown industry research report in the current conversation
  - Financial comparison table for representative listed companies when data is available
data_sources: ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
official: false
---

# Industry Research

## Trigger

Use this skill for prompts such as:

- `X 行业框架`
- `X 产业链地图`
- `X 行业全景`
- `研究 X 行业`
- `分析 X 赛道`

## Completion Standard

The task is complete when the assistant returns a complete Markdown industry report in the current conversation.

The public edition does not require external service upload or local report-file output.

## Source Discipline

Before qualitative conclusions, gather and synthesize:

1. Recent five-year broker / sell-side industry reports or theme reports.
2. Representative company filings and investor materials.
3. Structured industry, market, and financial data when available.
4. Chinese web search, broader web search, and user-provided materials.

Do not rely only on snippets, ratings, target prices, or forecast tables. If full reports cannot be found, state the gap.

## Workflow

1. Define the industry boundary and remove non-core concept names.
2. Map the value chain: upstream, midstream, downstream, equipment, materials, customers, and substitutes.
3. Identify representative listed companies and explain why they belong in or outside the core company pool.
4. Build a financial comparison table when data is available.
5. Analyze supply, demand, pricing, margins, competition, disputes, and tracking indicators.
6. Return the final Markdown report directly in the conversation.

## Report Format

Use this Markdown structure:

```markdown
# {行业名}行业研究报告

## 一、行业概览

## 二、行业增长分析

## 三、产业链结构

## 四、需求侧驱动

## 五、供给侧变化

## 六、价格与利润传导

## 七、重点公司和竞争力分析

### 7.1 代表公司财务对比表

### 7.2 市场份额与竞争地位

### 7.3 头部公司核心竞争力

## 八、当前市场争议点

## 九、最值得跟踪的行业指标

## 十、综合判断

## 仍需补的资料 / 资料缺口
```

## Company Table

When data is available, include a representative company table with:

- company name and ticker
- business exposure
- revenue and profit scale
- growth rate
- gross margin / net margin
- market cap and valuation
- consensus expectation where available
- key moat and key risk

If a data point is unavailable, write `not disclosed`, `not found`, or `not comparable`; do not force estimates.

## Quality Bar

- Separate industry facts, market consensus, and your own reasoning.
- Explain why each company is included or excluded.
- Make the value chain visible enough for a reader to understand profit pools and bargaining power.
- Do not provide personalized financial advice or unconditional buy/sell instructions.
