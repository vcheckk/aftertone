---
name: aftertone-mode
description: Set Aftertone TTS queue mode (queue or interrupt)
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user said `queue` or `interrupt`.

If no mode was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| queue | queue — wait for current speech |
| interrupt | interrupt — stop and speak new line |

## Apply (one command only)

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then run **only**:

```
uv run --directory py python -m aftertone set mode MODE
```

No daemon restart. Report stdout only.
