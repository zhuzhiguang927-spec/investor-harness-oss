# Security

Investor Harness is a workflow repository. It may reference local tools, data-source adapters, and helper scripts, but credentials and private workspace identifiers should stay outside Git.

## Credentials

Do not commit:

- API keys
- access tokens
- private workspace paths
- private notebook or knowledge-base IDs
- GitHub tokens
- API keys for market-data providers
- Browser cookies or session exports
- Private research files that are not meant for repository history

The public edition should not require committed credentials or private notebook identifiers. Keep local credentials in your own environment-specific configuration files and exclude them from Git.

## Recommended Secret Scan

Before pushing:

```powershell
rg -n --hidden --glob '!*.git/**' --glob '!node_modules/**' -i "(api[_-]?key|secret|token|password|client_secret|private[_-]?key|C:\\\\Users\\\\|folder[0-9a-f]{8,}|note_id [0-9])"
```

Review every hit. Documentation may mention credential paths, but no actual secret value should appear.

## Repository Visibility

Before publishing a fork or release:

1. Review golden templates for redistribution.
2. Keep local paths and notebook identifiers generalized.
3. Confirm third-party data-source usage is compatible with public release.

## Reporting

If a secret is accidentally committed, rotate the credential first, then remove it from history.
