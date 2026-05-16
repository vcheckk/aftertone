---
name: aftertone-speed
description: Pick Aftertone TTS playback speed
---

## Speed rule (required)

**Do not** plan or run shell first (unless the user gave a number, e.g. `/aftertone-speed 1.1`).

Your **first** tool call must be **AskQuestion** with:

| id | label |
|----|-------|
| 0.9 | Slower (0.9) |
| 1.0 | Normal (1.0) |
| 1.05 | Default (1.05) |
| 1.1 | Slightly faster (1.1) |
| 1.2 | Faster (1.2) |
| 1.5 | Fast (1.5) |

## Apply

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_config.py set speed VALUE
```

Allowed range **0.5–2.0** (recommended **0.9–1.5**). No daemon restart. Report stdout only.
