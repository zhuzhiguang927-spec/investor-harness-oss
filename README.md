# Investor Harness

> 投研场景下的 AI 任务执行规范与 skill 路由系统。

Investor Harness 是一套面向二级市场研究工作的 agent harness。它把“怎么看公司、怎么看行业、怎么做对比、怎么从事件里找候选公司”沉淀成可执行的 Markdown skill、关键词路由、归档规则、质量闸门和数据源优先级，让 AI 不只是回答问题，而是按投研流程完成任务。

本仓库是基于原始 `investor-harness` 的增强版，重点加入了 `ZZG` / `ZZG1` / `ZZG2` / `ZZG3` 四个投研主入口，并强化了 IMA 笔记上传、卖方研报先行、iFind / 妙想 / 中文搜索校验等工作要求。

This public-ready edition removes hard-coded local paths and private notebook identifiers. Runtime integrations are configured through local files such as [config/ima.example.json](config/ima.example.json).

## What It Does

Investor Harness 解决四类常见问题：

| 问题 | Harness 的处理方式 |
|---|---|
| 幻觉和编数据 | 强制区分公开事实、财报披露、市场共识、合理推演和待核验假设 |
| 没有流程 | 用 skill 固化公司、行业、对比、事件、催化、盘面、路演等工作流 |
| 没有归档 | 输出必须落到固定目录，并在需要时上传到 IMA 笔记本 |
| 上下文丢失 | 通过 `core/` 协议、`.task-pulse`、checkpoint 和归档文件支持续跑 |

## Main Entry Skills

| 用户意图 | 默认 skill | 输出 |
|---|---|---|
| 分析公司 / 看下个股 / 起 coverage | `ZZG` | 11 维公司分析报告 + IMA `Company Analysis` |
| 行业框架 / 产业链地图 / 行业全景 | `ZZG1` | 10 段行业报告 + 财务对比表 + IMA `Industry Analysis` |
| A vs B / 同业对比 / 谁更好 | `ZZG2` | 横向比较报告 + IMA `Comparison Analysis` |
| 事件影响 / 哪些公司受益 / 事件驱动选股 | `ZZG3` | 公司影响判断与候选分层 + IMA `Event Driven Analysis` |

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

## IMA Upload Gate

The ZZG family treats IMA upload as part of task completion:

| Skill | Notebook |
|---|---|
| `ZZG` | `Company Analysis` |
| `ZZG1` | `Industry Analysis` |
| `ZZG2` | `Comparison Analysis` |
| `ZZG3` | `Event Driven Analysis` |

The upload helper reads IMA credentials from the local user config directory. Credentials are not stored in this repository.
Copy `config/ima.example.json` to `config/ima.local.json` and fill local values before using IMA upload. `config/*.local.json` is ignored by Git.

Security notes: [SECURITY.md](SECURITY.md).

## Installation Notes

The repository is Markdown-first. Most workflows run inside an agent that can read files and execute local helper scripts.

Common local requirements:

- Git
- Node.js, for IMA upload helper scripts
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

Current local version: `0.9.2` plus ZZG workflow extensions.

See [CHANGELOG.md](CHANGELOG.md) for the public-facing change summary.

## Disclaimer

This project is a workflow and documentation harness for investment research. It is not a licensed investment adviser, does not provide personalized financial advice, and should not be treated as a buy/sell recommendation system.

## License

MIT. See [LICENSE](LICENSE).
