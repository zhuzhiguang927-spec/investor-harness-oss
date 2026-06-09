---
name: sm-industry-map
description: Compatibility entry. Industry framework, value-chain map, and industry landscape tasks should use `industry-research`.
inputs:
  - Industry / sector / theme name
outputs:
  - Redirect to `industry-research`
data_sources: ../../core/adapters.md
markets: [CN-A, HK, US, GLOBAL]
---

# SM Industry Map Compatibility Entry

This skill is kept for backward compatibility. For industry research, load:

`{HARNESS_ROOT}\skills\industry-research\SKILL.md`

The public edition completes the task by returning the full Markdown industry report in the current conversation. It does not require local report-file output or external service upload.
