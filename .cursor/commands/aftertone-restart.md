---
name: aftertone-restart
description: Restart Aftertone TTS daemon
---

## Agent rule

**No planning.** Run **only** the command below. Report success or stderr. No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone restart
```
