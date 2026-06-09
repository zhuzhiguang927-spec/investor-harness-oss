---
name: company-analysis
description: >
  Company / individual-stock research workflow for A-share, Hong Kong, and US-listed companies.
  Use this skill when the user asks to analyze, research, compare the fundamentals of, or start coverage on a specific company or stock.
inputs:
  - Company name, stock code, or ticker
  - Optional user focus, investment horizon, existing notes, or pasted materials
outputs:
  - Complete Markdown company research report in the current conversation
data_sources: ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
official: false
---

# Company Analysis

## Trigger

Use this skill for prompts such as:

- `分析 X 公司`
- `研究 X`
- `看下 X`
- `X 深度报告`
- `起 X 的 coverage`
- `X 股票怎么样`

Do not replace this workflow with a generic company summary. The point is to produce a complete, evidence-grounded company analysis report.

## Completion Standard

The task is complete when the assistant returns a complete Markdown report in the current conversation.

The public edition does not require:

- uploading the report to an external service
- writing the final report to a local folder
- returning local file paths as proof of completion

Keep the report format complete. Do not shrink the output into a short answer just because it is delivered in chat.

## Source Discipline

Before qualitative conclusions, gather and synthesize:

1. Recent five-year broker / sell-side research report text or PDF for the target company.
2. Recent five-year broker / sell-side research report text or PDF for the relevant industry.
3. Company announcements, annual reports, quarterly reports, and other official disclosures.
4. Structured market and financial data when available.
5. Chinese web search, broader web search, and user-provided materials.

Do not rely only on snippets, ratings, target prices, PE tables, or earnings forecast summaries. If full report text cannot be found, state the gap briefly in the report.

## Workflow

1. Identify the company, ticker, exchange, market, and comparable industry.
2. Collect market and financial data. If a local runtime is available, `data_agent.py` can be used as a helper; otherwise summarize the same fields from public sources.
3. Read the company and industry research materials before writing qualitative sections.
4. Build the report around the fixed 11-dimension structure below.
5. Return the final Markdown report directly in the conversation.

## Data Block

When enough data is available, the report should include a concise data block covering:

- market data: price, market cap, valuation, recent performance
- annual financials: revenue, net profit, margins, ROE, cash flow
- quarterly trends: recent revenue and profit cadence
- product / segment split
- geography / customer / channel split where disclosed

If a field is unavailable, write `not disclosed` or `not found`; do not invent numbers.

## Report Format

Use this Markdown structure:

```markdown
# {公司名}（{代码或ticker}）公司分析报告

## 一、市场数据

## 二、财务数据

## 三、行业分析

## 四、竞争格局

## 五、商业模式与护城河

## 六、产品、客户与收入结构

## 七、成长路径

## 八、管理层、治理与资本配置

## 九、风险因素

## 十、共识与分歧

## 十一、综合评价

## 仍需补的资料 / 资料缺口
```

## Evidence Labels

Mark important facts and assumptions using short labels:

- `公开事实`
- `财报披露`
- `市场共识`
- `合理推演`
- `待核验假设`

Use labels to clarify evidence quality, not to clutter every sentence.

## Quality Bar

- The report must be a full research note, not a short company summary.
- Include tables where they make comparison easier.
- Separate facts, market consensus, and your own reasoning.
- State uncertainty and missing data directly.
- Do not provide personalized financial advice or unconditional buy/sell instructions.
