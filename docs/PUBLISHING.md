# Publishing Notes

This repository is maintained as a GitHub project for the customized Investor Harness workflow set.

## Recommended Visibility

This public-ready edition is intended for public repositories after the checks below pass. Keep private forks private if they contain real notebook IDs, local paths, private research, or organization-specific templates.

## Before Pushing

Run these checks from the repository root:

```powershell
git status --short --branch
git diff --check
rg -n --hidden --glob '!*.git/**' --glob '!node_modules/**' -i "(api[_-]?key|secret|token|password|client_secret|private[_-]?key|C:\\\\Users\\\\|folder[0-9a-f]{8,}|note_id [0-9])"
```

Expected result:

- `git status` shows only intended changes.
- `git diff --check` has no whitespace errors.
- Secret scan may find documentation references to credential paths, but it must not find actual credential values.

## GitHub Remote

Suggested remote layout:

```text
origin   upstream source repository
github   user-owned publish repository
```

That keeps the upstream project separate from the user-owned publishing target.

## Push

```powershell
git push github main
git push github --tags
```

## After Pushing

Verify:

```powershell
gh repo view <owner>/investor-harness --json name,visibility,url
gh repo view <owner>/investor-harness --web
```

## Public Release Checklist

Before making the repository public:

- Review `skills/ZZG*/SKILL.md` for local absolute paths.
- Review IMA notebook names and folder IDs.
- Review golden templates for proprietary research content.
- Confirm third-party data-source terms allow redistribution.
- Keep credential files outside the repository.
