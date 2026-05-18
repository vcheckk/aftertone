---
name: aftertone-expression
description: Set Aftertone expression_mode in TOML
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user gave a mode (e.g. `/aftertone-expression subtle`).

If no mode was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| off | Off — plain speech only |
| subtle | Subtle — sigh on blocked |
| expressive | Expressive — sigh and breath on more states |
| passthrough | Passthrough — keep one inline tag you write |

## Apply (one command only)

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then run **only**:

```
uv run --directory py python -m aftertone set expression MODE
```

No daemon restart. Report stdout only.
