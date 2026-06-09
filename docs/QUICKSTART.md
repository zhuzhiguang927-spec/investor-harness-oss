# Quickstart

This guide gets Investor Harness working inside an agent environment such as Codex, Claude Code, OpenCode, or OpenClaw.

## 1. Put The Repository In A Stable Path

Use a stable local skill path so the agent can read `core/`, `skills/`, and `setup/`.

Recommended locations:

```text
~/.codex/skills/investor-harness
~/.claude/skills/investor-harness
~/skills/investor-harness
```

## 2. Run Onboarding From The Agent

Ask the agent:

```text
跑一下 investor-harness onboarding
```

The agent should read [ONBOARDING.md](../ONBOARDING.md), show the route table, and wait for explicit confirmation before writing any entry file.

## 3. Bootstrap A Research Workspace

A research workspace is not ready until it has the expected folders and state files:

```text
coverage/
themes/
briefings/
.task-pulse
active-tasks.md
```

If they are missing, use the bootstrap flow in [setup/README.md](../setup/README.md).

## 4. Use Natural Triggers

Examples:

| Prompt | Expected route |
|---|---|
| `分析英伟达` | `ZZG` |
| `PCB 行业框架` | `ZZG1` |
| `宁德时代和比亚迪谁更好` | `ZZG2` |
| `这次政策对哪些公司利好` | `ZZG3` |
| `给 PM 一页纸` | `sm-pm-brief` |
| `看一下今天为什么涨跌` | `sm-close-recap` |

## 5. Completion Standards

For ZZG-family research, a task is not complete until the full Markdown report has been written locally and uploaded to the required IMA notebook.

| Route | Required notebook |
|---|---|
| Company / stock research | `Company Analysis` |
| Industry research | `Industry Analysis` |
| Company comparison | `Comparison Analysis` |
| Event-driven opportunity analysis | `Event Driven Analysis` |

If upload fails or no success confirmation is available, the agent should report the task as unfinished.

## 6. Useful Files

- [../README.md](../README.md): project overview
- [../manifest.yaml](../manifest.yaml): skill inventory
- [../setup/keyword-routes.md](../setup/keyword-routes.md): keyword routing table
- [../core/adapters.md](../core/adapters.md): data-source priority
- [../core/preamble.md](../core/preamble.md): preflight discipline
- [../core/postamble.md](../core/postamble.md): completion discipline
