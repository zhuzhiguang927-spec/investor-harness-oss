---
name: sm-catalyst-monitor
description: 事件催化与财报前瞻 skill。用于跟踪政策、财报、价格、订单、产品发布、产业数据等催化剂，判断其对收入、利润、估值或情绪的影响，并输出短中期跟踪清单。若用户要求从具体事件/变化/业绩材料判断“这件事对某家公司有啥影响、这件事对哪些公司利好、这个业绩怎么看、哪些公司受益、哪些票值得看、哪些公司值得投资”，必须改用 `ZZG3`。
inputs:
  - 事件 / 新闻 / 政策 / 产业数据
  - 可选：相关公司或板块清单
outputs:
  - 事件影响判断 + 短中期跟踪清单
data_sources: 见 ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
---

# SM Catalyst Monitor

这个 skill 用于事件驱动研究和财报前瞻，不是简单新闻摘要。

如果用户的目标是“从事件推导投资候选公司”，或问“这件事对 X 有啥影响 / 这件事对哪些公司利好 / 这个业绩怎么看”，不要继续使用本 skill，改用 `ZZG3`。本 skill 保留给纯催化跟踪、事件影响点评和后续跟踪清单。

## 强制流程（v0.3 硬约束）

> ⛔ **任何分析输出之前**，必须严格执行 [`../../core/preamble.md`](../../core/preamble.md) 的 5 步开始前流程
>
> ⛔ **任何输出完成之前**，必须严格执行 [`../../core/postamble.md`](../../core/postamble.md) 的 6 步结束后流程
>
> 输出归档按 [`../../core/output-archive.md`](../../core/output-archive.md) 命名规范
> 输出验收按 [`../../core/acceptance.md`](../../core/acceptance.md) 清单逐条自检
>
> **跳过任何一环视为未完成任务。**

Catalyst Monitor 特别注意：事件跟踪需要交叉多源（政策 + 公告 + 行业媒体），preamble Step 4 的 [Preflight] 必须列出至少 2 个独立信源。

## 核心任务

- 判断事件影响方向
- 区分一次性扰动和趋势性变化
- 判断影响收入、利润、估值还是风险偏好
- 给出跟踪节奏

## 输出格式

- `事件概述`
- `为什么重要`
- `影响路径`
- `最相关的公司 / 板块`
- `对盈利 / 估值 / 情绪的影响`
- `接下来一周到一个季度的跟踪清单`

## 典型适用任务

- 财报前瞻
- 政策点评
- 产业价格周跟踪
- 新品发布影响分析
- 订单 / 渠道 / 出货节奏变化跟踪

## 参考

- [../../core/evidence.md](../../core/evidence.md)
- [../../core/templates.md](../../core/templates.md)
- [../../core/compliance.md](../../core/compliance.md)
- [../../core/adapters.md](../../core/adapters.md)
