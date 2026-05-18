---
name: aftertone-speed
description: Set Aftertone TTS playback speed
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user gave a number (e.g. `/aftertone-speed 1.1`).

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

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then run **only**:

```
uv run --directory py python -m aftertone set speed VALUE
```

Allowed range **0.5–2.0**. No daemon restart. Report stdout only.
