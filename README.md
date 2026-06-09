# Investor Harness

> 投研场景下的 AI 任务执行规范与 skill 路由系统。

Investor Harness 是一套面向二级市场研究工作的 agent harness。它把“怎么看公司、怎么看行业、怎么做对比、怎么从事件里找候选公司”沉淀成可执行的 Markdown skill、关键词路由、质量闸门和数据源优先级，让 AI 不只是回答问题，而是按投研流程完成任务。

The public edition focuses on four readable research entry skills: `company-analysis`, `industry-research`, `company-comparison`, and `event-driven-opportunity`. Reports are designed to be returned as complete Markdown in the current conversation.

## What It Does

Investor Harness 解决四类常见问题：

| 问题 | Harness 的处理方式 |
|---|---|
| 幻觉和编数据 | 强制区分公开事实、财报披露、市场共识、合理推演和待核验假设 |
| 没有流程 | 用 skill 固化公司、行业、对比、事件、催化、盘面、路演等工作流 |
| 输出太散 | 按固定 Markdown 结构输出完整报告，便于复制、审阅和二次整理 |
| 上下文丢失 | 通过 `core/` 协议、`.task-pulse`、checkpoint 和归档文件支持续跑 |

## Main Entry Skills

| 用户意图 | 默认 skill | 输出 |
|---|---|---|
| 分析公司 / 看下个股 / 起 coverage | `company-analysis` | 11 维公司分析报告 |
| 行业框架 / 产业链地图 / 行业全景 | `industry-research` | 10 段行业报告 + 财务对比表 |
| A vs B / 同业对比 / 谁更好 | `company-comparison` | 横向比较报告 |
| 事件影响 / 哪些公司受益 / 事件驱动选股 | `event-driven-opportunity` | 公司影响判断与候选分层 |

此外，仓库还保留并增强了 `sm-thesis`、`sm-consensus-watch`、`sm-catalyst-monitor`、`sm-stock-screen`、`sm-tape-review`、`sm-deck-builder`、`sm-daily-feed` 等投研辅助 skill。

完整路由表见 [setup/keyword-routes.md](setup/keyword-routes.md)。

## Repository Layout

```text
core/        Shared execution rules, source priority, evidence labels, archive rules
skills/      Individual research workflows and triggerable skills
setup/       Onboarding, keyword routing, workspace bootstrap templates
docs/        Quickstart, publishing notes, decks and supporting docs
install/     Installation helpers
manifest.yaml  Machine-readable skill inventory
```

## Quick Start

Clone or copy the repository into your agent skill directory, then ask the agent to run onboarding:

```text
跑一下 investor-harness onboarding
```

The onboarding flow will:

1. Show available skills and keyword routes.
2. Ask for explicit confirmation before writing any agent entry file.
3. Detect the active harness type, such as Codex, Claude Code, OpenCode, or OpenClaw.
4. Add the managed route block to the correct entry file.
5. Check whether the target workspace has `coverage/`, `themes/`, `briefings/`, `.task-pulse`, and `active-tasks.md`.

More detail: [docs/QUICKSTART.md](docs/QUICKSTART.md).

## Research Source Discipline

For A-share, Hong Kong stock, and US stock company or industry research, the harness expects the following source order:

1. Recent five-year broker / sell-side research report text or PDF.
2. Company announcements and financial reports.
3. Structured market, financial, shareholder, event, news, and industry-indicator data.
4. Chinese web search and broader web search.
5. User-provided materials.

Conclusions should be traceable to those materials, and weak evidence should be labeled instead of silently blended into the argument.

## Output Model

Investor Harness returns complete Markdown reports in the current agent conversation. The public edition does not require writing report files to local folders and does not require uploading results to an external service.

Security notes: [SECURITY.md](SECURITY.md).

## Installation Notes

The repository is Markdown-first. Most workflows run inside an agent that can read files and execute local helper scripts.

Common local requirements:

- Git
- Python, for data and validation helpers
- Optional data-source skills or MCP tools configured in the user environment

Useful entry points:

- [ONBOARDING.md](ONBOARDING.md)
- [INSTALL-PROMPT.md](INSTALL-PROMPT.md)
- [setup/README.md](setup/README.md)
- [docs/QUICKSTART.md](docs/QUICKSTART.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [ROADMAP.md](ROADMAP.md)

## Version

Current local version: `0.9.2`.

See [CHANGELOG.md](CHANGELOG.md) for the public-facing change summary.

## Disclaimer

This project is a workflow and documentation harness for investment research. It is not a licensed investment adviser, does not provide personalized financial advice, and should not be treated as a buy/sell recommendation system.

## License

MIT. See [LICENSE](LICENSE).
