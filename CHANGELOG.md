# Changelog

## 0.9.3

- Added local public checks for route, manifest, Python, and onboarding validation.
- Added `scripts/check_routes.py` to catch route drift, missing skill directories, legacy private skill names, and private-edition completion text.
- Added `scripts/smoke_onboarding.py` to verify the public route block and workspace bootstrap flow.
- Added golden-template-style synthetic demos for A-share-style company and industry research.
- Updated `setup/bootstrap.sh` so smoke workspaces include `coverage/`, `themes/`, and `briefings/`.
- Cleaned public setup/update generated text so core reports default to complete Markdown in the current conversation.

## 0.9.2

- Added `company-analysis` as the default company / individual-stock research entry.
- Added `industry-research` as the default industry research entry.
- Added `company-comparison` as the default company comparison entry.
- Added `event-driven-opportunity` as the default event-driven investment opportunity entry.
- Updated the public completion model so core reports are returned as complete Markdown in the current conversation.
- Strengthened broker-report-first research discipline for A-share, Hong Kong stock, and US stock workflows.
- Added data-agent and validation helpers for company reports.
- Added public-safe synthetic examples for all four core research routes.
- Added OpenAI OSS support notes for maintainers and grant applications.
- Updated keyword routing so common Chinese research prompts map to the correct skill automatically.
- Added `sm-industry-database` for industry and company database construction.
- Improved source and口径 tracking for structured research outputs.
- Expanded setup and bootstrap workflows.

## 0.9.1

- Added onboarding flow that can install managed route blocks after explicit user confirmation.
- Added workspace audit for `coverage/`, `themes/`, `briefings/`, `.task-pulse`, and `active-tasks.md`.

## 0.9.0

- Added Librarian mode skills for daily feed, question lists, health checks, Q&A archive, and people watch.
- Improved cross-session research memory and task continuation structure.

## Earlier

- Added deck generation, tape review, catalyst monitoring, PM brief, red-team review, stock screening, and company-deep-dive workflows.
