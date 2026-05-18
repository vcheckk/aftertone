---
name: aftertone-status
description: Show Aftertone config and daemon status
---

## Agent rule

**No planning.** Run **only** the command below. Report the JSON. No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone status
```
