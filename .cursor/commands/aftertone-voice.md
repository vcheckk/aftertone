---
name: aftertone-voice
description: Set Aftertone voice preset, update TOML, restart daemon
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user named a preset (e.g. `/aftertone-voice F4`, `Sara`).

If no preset was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| F1 | Elena (female) |
| F2 | Mia (female) |
| F3 | Claire (female) |
| F4 | Sara (female) |
| F5 | Lily (female) |
| M1 | James (male) |
| M2 | Marcus (male) |
| M3 | David (male) |
| M4 | Noah (male) |
| M5 | Owen (male) |

## Apply (one command only)

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then run **only**:

```
uv run --directory py python -m aftertone set voice PRESET --ensure
```

Use the chosen **id** (e.g. `F4`), not the display name. The CLI updates TOML and **restarts the daemon** by default. Report stdout only.
