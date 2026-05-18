---
name: aftertone-toggle
description: Toggle Aftertone spoken summary TTS on or off
---

## Agent rule

**No planning.** Run **only** the command below. Report stdout (`on` or `off`). No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone toggle
```
