---
name: aftertone-off
description: Turn Aftertone spoken summary TTS off
---

## Agent rule

**No planning.** Run **only** the command below. Report stdout. No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone off
```
