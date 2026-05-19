---
description: >-
  Show Aftertone TTS daemon and hook health (install dir, port, enabled). Use when
  the user asks if Aftertone works, why there is no speech, or to check the daemon.
disable-model-invocation: true
---

# Aftertone status

Run diagnostics against the user’s Aftertone install (from plugin **install_dir**, default `~/aftertone`).

1. Resolve install root: `CLAUDE_PLUGIN_OPTION_install_dir`, `AFTERTONE_INSTALL_DIR`, or `~/aftertone`.
2. Run:

```bash
cd "<install>/py" && uv run python -m aftertone doctor --repo-root ..
```

3. If the daemon is down, suggest:

```bash
cd "<install>/py" && uv run python tts_daemon_ctl.py start --repo-root ..
```

4. Mention `tail` on `<install>/.cursor/hooks/state/speak_summary-hook.log` for hook skips.

Do not tell the user to hand-edit `speak_summary.toml`; prefer `python -m aftertone set …` or MCP tools if configured.
