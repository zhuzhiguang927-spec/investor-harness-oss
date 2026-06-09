# Security

Investor Harness is a workflow repository. It may reference local tools, IMA notebooks, data-source adapters, and helper scripts, but credentials and private notebook IDs should stay outside Git.

## Credentials

Do not commit:

- IMA `client_id`
- IMA `api_key`
- IMA notebook folder IDs
- GitHub tokens
- API keys for market-data providers
- Browser cookies or session exports
- Private research files that are not meant for repository history

The IMA upload helper reads credentials and notebook IDs from a local config file at runtime. Copy `config/ima.example.json` to `config/ima.local.json`; do not commit the local file.

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
