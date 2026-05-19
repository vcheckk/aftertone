---
name: aftertone-off
description: Turn Aftertone spoken TTS off for this chat only
---

## Agent rule

**No planning.** Run **only** the command below. Report stdout. No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone off
```

Disables spoken TTS **for this chat only** (next hook removes it from the allowlist). Other chats are unchanged.
