# Contributing

Thanks for helping improve Investor Harness.

This project is a Markdown-first workflow harness for AI-assisted investment research. Contributions should improve reproducibility, source discipline, routing clarity, archival behavior, or maintainability.

## Good Contribution Areas

- New or improved skill workflows.
- Better evidence labels and source-quality checks.
- Safer onboarding and setup scripts.
- Public examples that do not include private research or credentials.
- CI checks for Markdown, Python helpers, JavaScript helpers, and secret patterns.
- Documentation that helps users run the harness in Codex, Claude Code, OpenCode, or OpenClaw.

## Before Opening A Pull Request

Run:

```powershell
git status --short --branch
git diff --check
python -m compileall skills -q
node --check skills/ZZG/upload_to_ima.cjs
```

Also scan for accidental private data:

```powershell
rg -n --hidden --glob '!*.git/**' --glob '!node_modules/**' -i "(api[_-]?key|secret|token|password|client_secret|private[_-]?key|C:\\\\Users\\\\|folder[0-9a-f]{8,}|note_id [0-9])"
```

## Pull Request Expectations

- Keep changes scoped.
- Avoid hard-coded local paths.
- Do not commit real credentials, notebook IDs, private research, or browser sessions.
- Prefer placeholders such as `{HARNESS_ROOT}`, `{OUTPUT_ROOT}`, and local config examples.
- Add or update documentation when changing routing behavior.

## Financial Disclaimer

This repository provides workflow tooling and research discipline. It does not provide investment advice.
