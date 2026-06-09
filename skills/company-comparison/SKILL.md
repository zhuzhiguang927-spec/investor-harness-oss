---
name: company-comparison
description: >
  Company comparison workflow for two or more listed companies. Use this skill when the user asks for comparable-company analysis,
  A vs B, peer comparison, relative valuation, or "which company is better" style research.
inputs:
  - Two or more company names, stock codes, or tickers
  - Optional comparison dimensions, user focus, holding context, or pasted materials
outputs:
  - Complete Markdown company comparison report in the current conversation
data_sources: ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
official: false
---

# Company Comparison

## Trigger

Use this skill for prompts such as:

- `A 和 B 对比`
- `比较 A 和 B`
- `A vs B`
- `谁更好`
- `相对估值`
- `同业对比`
- `可比公司分析`

## Completion Standard

The task is complete when the assistant returns a complete Markdown comparison report in the current conversation.

The public edition does not require external service upload or local report-file output.

## Source Discipline

Before conclusions, gather and compare:

1. Company identity, ticker, exchange, and comparability boundary.
2. Recent five-year company research reports where available.
3. Relevant industry research reports.
4. Company filings, announcements, and official materials.
5. Structured financial, valuation, shareholder, and market data where available.
6. Chinese web search, broader web search, and user-provided materials.

Do not compare companies on different accounting periods, currencies, or business boundaries without flagging the mismatch.

## Workflow

1. Confirm each company and whether it is truly comparable.
2. Normalize market, reporting period, currency, accounting standard, and business-segment differences.
3. Compare fundamentals, growth drivers, margins, cash flow, capital intensity, valuation, expectations, and risks.
4. Explain which company is stronger under which assumptions, time horizon, and risk-return profile.
5. Return the final Markdown report directly in the conversation.

## Report Format

Use this Markdown structure:

```markdown
# {公司A} vs {公司B} 公司对比分析报告

## 一、结论先行

## 二、标的识别与可比性边界

## 三、业务模式与产业链位置对比

## 四、收入结构与增长驱动对比

## 五、利润率、费用率与经营质量对比

## 六、资产负债表、现金流与资本开支对比

## 七、竞争壁垒、客户结构、技术路线与供给格局对比

## 八、估值、市场预期与预期差对比

## 九、催化剂、风险和验证节点

## 十、综合判断：谁更适合什么风险收益画像

## 仍需补的资料 / 资料缺口
```

## Required Tables

Include comparison tables where data is available:

- market cap, revenue, net profit, revenue growth, profit growth
- gross margin, net margin, ROE / ROIC, operating cash flow
- R&D, sales, and management expense ratios
- business mix, key customers, downstream exposure, and industry position
- valuation metrics appropriate for the sector
- next three to six months of verification indicators

## Evidence Labels

Use concise labels for important facts and assumptions:

- `公开事实`
- `财报披露`
- `市场共识`
- `合理推演`
- `待核验假设`

## Quality Bar

- Do not simply paste two standalone company reports together.
- Keep all companies under the same comparison framework.
- Explain uncertainty and missing data.
- Do not provide personalized financial advice or unconditional buy/sell instructions.
