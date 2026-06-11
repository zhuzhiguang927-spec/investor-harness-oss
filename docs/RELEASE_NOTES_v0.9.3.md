# Investor Harness v0.9.3

v0.9.3 is a small public-maintenance release focused on repository activity, reproducibility, and public-safe demos.

## Highlights

- Added local public validation scripts.
- Added route consistency and public sanitization checks.
- Added onboarding smoke test.
- Added two golden-template-style synthetic demos:
  - `examples/golden-template-company-demo.md`
  - `examples/golden-template-industry-demo.md`
- Updated workspace bootstrap to create `coverage/`, `themes/`, and `briefings/`.
- Cleaned public setup/update generated text so core reports default to complete Markdown in the current conversation.

## Why This Release Matters

This release makes the public repository easier to review as an open-source project. It shows a repeatable maintenance loop: issues, checks, examples, release notes, and local validation scripts that protect the public edition from drifting back toward private local assumptions.

## Compatibility

No breaking skill changes are expected. The four public core routes remain:

- `company-analysis`
- `industry-research`
- `company-comparison`
- `event-driven-opportunity`

## Verification

Run from the repository root:

```bash
python -m compileall skills scripts -q
python scripts/check_routes.py
python scripts/smoke_onboarding.py
```
