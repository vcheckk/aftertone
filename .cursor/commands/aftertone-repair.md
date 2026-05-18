---
name: aftertone-repair
description: Re-register hooks, apply defaults, restart daemon
---

## Agent rule

**No planning.** Run **only** the command below. Report stdout/stderr. No hand-editing TOML or hooks unless repair fails.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone repair
```
