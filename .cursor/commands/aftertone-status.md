---
name: aftertone-status
description: Show Aftertone spoken TTS and speak_summary.toml settings
---

Resolve the **global install** (default `~/aftertone`; see `~/.cursor/hooks/aftertone-install-dir`), then run:

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_config.py status
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_toggle.py status
cd "${AFTERTONE_ROOT}/py" && uv run python tts_daemon_ctl.py status --repo-root ..
```

Do not change files unless the user asked for a change. Explain whether spoken TTS is on, current `lang` / `speed` / `mode` / voice, and whether the daemon is running.
