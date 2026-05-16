---
name: aftertone-on
description: Turn Aftertone spoken summary TTS on
---

Run **only** this from the **repository root**:

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_toggle.py on
```

Report stdout (`on`). No other edits.
