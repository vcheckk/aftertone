---
name: aftertone-on
description: Turn Aftertone spoken TTS on for this chat only
---

## Agent rule

**No planning.** Run **only** the command below. Report stdout. No other edits.

`cd` to the install root (first line of `~/.cursor/hooks/aftertone-install-dir`), then:

```
uv run --directory py python -m aftertone on
```

Enables spoken TTS **for this chat only**. Send any agent reply here to register the session. Run `/aftertone-on` again in **another** chat to enable speech there. Other chats stay silent.
