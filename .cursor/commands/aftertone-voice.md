---
name: aftertone-voice
description: Pick an Aftertone voice preset, apply it, and restart the TTS daemon
---

## Speed rule (required)

**Do not** plan, explain, or run shell before the user picks a voice.

Your **first** tool call must be **AskQuestion** (unless the user already named a preset or person, e.g. `/aftertone-voice F4`, `/aftertone-voice Sara`, `James`).

## Picker (first tool call)

One question, `allow_multiple: false`. Use these options (`id` = TOML preset, `label` = human name):

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

Prompt example: `Choose a voice (daemon restarts after apply).`

(Optional check: run `voice-picker` under the global install — see `aftertone-status`.)

## Apply (only after the user picks)

`PRESET` = chosen **id** (e.g. `F4`), not the display name:

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_config.py set voice PRESET --restart --ensure
```

You may also pass a first name (e.g. `Sara`) — the script resolves it to the preset id.

Report stdout briefly. Do not hand-edit TOML.
