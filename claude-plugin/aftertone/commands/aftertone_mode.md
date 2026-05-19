---
description: Set Aftertone TTS queue mode (queue or interrupt). Use when the user runs /aftertone_mode.
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user said `queue` or `interrupt`.

If no mode was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| queue | queue — wait for current speech |
| interrupt | interrupt — stop and speak new line |

## Apply (one command only)

Read install root from `~/.cursor/hooks/aftertone-install-dir`, then run **only**:

```
uv run --directory INSTALL/py python -m aftertone set mode MODE
```

No daemon restart. Report stdout only.
