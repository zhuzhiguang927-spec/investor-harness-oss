---
name: event-driven-opportunity
description: >
  Event-driven opportunity workflow. Use this skill when the user provides news, policy, earnings, announcements,
  industry data, price changes, product launches, orders, technology breakthroughs, or other marginal changes
  and asks which companies may benefit, suffer, or deserve further research.
inputs:
  - Event, news, policy, announcement, earnings result, industry data, or pasted material
  - Optional market scope, time horizon, risk preference, or initial candidate companies
outputs:
  - Complete Markdown event-driven opportunity report in the current conversation
  - Candidate company A/B/C tiers and exclusion list
data_sources: ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
official: false
---

# Event-Driven Opportunity

## Trigger

Use this skill for prompts such as:

- `这件事对 X 有啥影响`
- `这件事对哪些公司利好`
- `这个业绩怎么看`
- `这段变化哪些公司受益`
- `这段信息怎么选股`
- `哪些公司值得优先研究`

Use `company-analysis` for a full single-company deep dive, `company-comparison` for comparing top candidates, and `industry-research` when the event is really a long-term industry framework question.

## Completion Standard

The task is complete when the assistant returns a complete Markdown event-driven report in the current conversation.

The public edition does not require external service upload or local report-file output.

## Source Discipline

User-provided material is a lead, not the only evidence. Before conclusions, check:

1. The original event source if available.
2. Relevant company announcements, financial reports, and official disclosures.
3. Relevant industry and company research reports.
4. Structured market, financial, price, capacity, inventory, order, and industry data where available.
5. Chinese web search, broader web search, and user-provided materials.

If source quality is weak or the event cannot be verified, state that clearly.

## Workflow

1. Classify the event: policy, regulation, order, price, cost, capacity, inventory, product, technology, earnings, management commentary, geopolitics, or other.
2. Identify affected variables: demand, supply, price, cost, market share, capex, inventory, channel, valuation anchor, or risk appetite.
3. Map the value-chain transmission path.
4. Build candidate companies and separate direct beneficiaries, second-order beneficiaries, harmed companies, and weakly related concept names.
5. Score candidates and explain why each is A, B, C, or excluded.
6. Return the final Markdown report directly in the conversation.

## Report Format

Use this Markdown structure:

```markdown
# 事件驱动投资机会分析：{事件或变化主题}

## 一、结论先行

| 分层 | 公司 | 代码 | 市场 | 方向 | 分数 | 核心理由 | 最大疑问 | 下一步 |
|---|---|---|---|---|---:|---|---|---|

## 二、事件拆解

## 三、影响路径

## 四、产业链受益 / 受损地图

## 五、候选公司分层分析

## 六、排除清单

## 七、验证节奏

## 八、反方与风险

## 九、后续工作流

## 仍需补的资料 / 资料缺口
```

## Scoring Framework

Score each candidate from 0 to 100:

| Dimension | Weight | What To Check |
|---|---:|---|
| Event relevance | 25 | Direct business, customer, cost, supply-chain, or product exposure |
| Earnings sensitivity | 20 | Impact on revenue, margin, profit, cash flow, or valuation anchor |
| Evidence strength | 15 | Announcements, filings, structured data, research reports, or cross-verified sources |
| Expectation gap | 15 | Whether the market has already priced it in |
| Valuation and crowding | 10 | Whether valuation or trading is already stretched |
| Risk adjustment | 15 | Policy, reversal, customer concentration, technology substitution, liquidity, and reflexivity |

## Quality Bar

- Do not output only a list of stock names.
- Separate direct beneficiaries from concept names.
- Include an exclusion list.
- Give verification indicators for one week, one month, and one quarter when relevant.
- Do not provide personalized financial advice or unconditional buy/sell instructions.
