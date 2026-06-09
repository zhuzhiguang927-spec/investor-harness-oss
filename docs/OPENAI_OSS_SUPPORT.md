# OpenAI OSS Support Notes

This document summarizes why Investor Harness is a good fit for OpenAI OSS support and gives maintainers copy-ready language for grant or credit applications.

## Project Summary

Investor Harness is an open-source Markdown workflow and skill-routing system for AI-assisted investment research, especially optimized for China A-share research. It turns complex research requests into named agent skills with source discipline, evidence labels, route tables, quality gates, and complete Markdown outputs.

Many AI investing tools and examples are US-equity-first. Investor Harness starts from A-share research practice: Chinese sell-side reports, company announcements, financial statements, industry-chain analysis, comparable listed companies, and event-driven market changes. The maintainer has senior practitioner experience in A-share investment research, and the project is shaped by those workflows.

## Why It Matters

Agent systems are increasingly used for high-context knowledge work, but many examples still rely on informal prompts and vague outputs. Investor Harness contributes a reusable pattern for domain-specific agents:

- natural-language routing into explicit skills
- source-priority rules before qualitative claims
- evidence labels for facts, disclosures, consensus, reasoning, and assumptions
- complete Markdown reports instead of shallow chat summaries
- public-safe examples for company, industry, comparison, and event-driven research

The project is early, but it targets a real OSS gap: practical, auditable workflow scaffolding for agentic research.

It is also differentiated by market focus: the strongest design target is not generic equity screening, but Chinese A-share company, industry, comparison, and event-driven research.

## Maintainer Role

The maintainer is the primary maintainer of the public repository and is responsible for:

- route-table updates
- skill documentation
- examples and onboarding material
- issue triage
- release notes
- public-safe sanitization and security review

## How API Credits Would Help

API credits would be used to improve and maintain the project, especially:

1. Generate and review route-consistency tests across `setup/keyword-routes.md`, `manifest.yaml`, and skill frontmatter.
2. Build public-safe synthetic examples for each research route.
3. Improve documentation for Codex, Claude Code, OpenCode, and generic agent environments.
4. Triage issues and draft pull-request reviews for community contributions.
5. Create a lightweight evaluation suite for hallucination resistance, evidence labeling, and report completeness.

## 90-Day Maintenance Plan

| Timeframe | Goal |
|---|---|
| 0-30 days | Add route consistency checks, expand examples, publish first release |
| 31-60 days | Add smoke tests for onboarding and skill discovery |
| 61-90 days | Build a small benchmark suite for evidence discipline and output completeness |

## Suggested Application Text

```text
Investor Harness is an open-source workflow and skill-routing system for AI-assisted investment research, especially optimized for China A-share workflows. It helps agents produce auditable Markdown reports by enforcing source discipline, evidence labels, task routing, and structured outputs. The project is early but targets a broad OSS need: reusable workflow scaffolding for domain-specific agent systems, with a differentiated focus on Chinese market research.
```

```text
I would use OpenAI API credits to maintain the project by generating route consistency tests, improving public examples, reviewing skill changes, triaging issues, and building a lightweight evaluation suite for hallucination resistance and report completeness.
```
