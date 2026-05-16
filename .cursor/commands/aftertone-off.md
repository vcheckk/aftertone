---
name: aftertone-off
description: Turn Aftertone spoken summary TTS off
---

Run **only** this from the **repository root**:

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_toggle.py off
```

Report stdout (`off`). No other edits.
