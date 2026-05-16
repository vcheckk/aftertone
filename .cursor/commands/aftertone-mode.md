---
name: aftertone-mode
description: Pick Aftertone TTS queue mode (queue or interrupt)
---

## Speed rule (required)

**Do not** plan or run shell first (unless the user said `queue` or `interrupt`).

Your **first** tool call must be **AskQuestion**:

| id | label |
|----|-------|
| queue | queue — wait for current speech |
| interrupt | interrupt — stop and speak new line |

## Apply

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_config.py set mode MODE
```

No daemon restart. Report stdout only.
