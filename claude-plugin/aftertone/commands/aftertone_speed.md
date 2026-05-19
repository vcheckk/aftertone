---
description: Set Aftertone TTS playback speed. Use when the user runs /aftertone_speed.
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user gave a number (e.g. `/aftertone_speed 1.1`).

If no value was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| 0.9 | Slower (0.9) |
| 1.0 | Normal (1.0) |
| 1.05 | Default (1.05) |
| 1.1 | Slightly faster (1.1) |
| 1.2 | Faster (1.2) |
| 1.5 | Fast (1.5) |

## Apply (one command only)

Read install root from `~/.cursor/hooks/aftertone-install-dir`, then run **only**:

```
uv run --directory INSTALL/py python -m aftertone set speed VALUE
```

Allowed range **0.5–2.0**. No daemon restart. Report stdout only.
