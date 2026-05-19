---
name: aftertone_off
description: Disable Aftertone spoken TTS. Use when the user types /aftertone_off or asks to turn speech off.
disable-model-invocation: true
allowed-tools: Bash(uv *)
---

# Aftertone off

**No planning.**

```bash
INSTALL="$(tr -d '\n\r' < "$HOME/.cursor/hooks/aftertone-install-dir" 2>/dev/null || echo "$HOME/aftertone")"
cd "$INSTALL/py" && uv run python -m aftertone off
```

Report that speech is disabled until `/aftertone_on`.
