---
name: aftertone-doctor
description: Run Aftertone diagnostics
---

## Agent rule

**No planning.** Run **only** the command below. Summarize the report briefly. No other edits unless doctor says repair is needed.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone doctor
```
