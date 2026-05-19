---
name: aftertone_on
description: Enable Aftertone spoken TTS. Use when the user types /aftertone_on or asks to turn speech on inside Claude Code.
disable-model-invocation: true
allowed-tools: Bash(*)
---

# Aftertone on

**No planning.** Run once:

```bash
bash ~/.cursor/hooks/aftertone-activate.sh
```

Hooks are already in `~/.claude/settings.json` from install — this only starts the daemon and sets `enabled = true`. No plugin or special `claude` flags required.
