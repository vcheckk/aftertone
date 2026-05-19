---
description: >-
  End substantive Claude Code replies with a short <spoken_summary> line for
  Aftertone local TTS. Use on every implementation, debug, or multi-sentence answer
  when the Aftertone plugin is enabled.
---

# Spoken summary (Aftertone)

The **Aftertone** plugin runs a **Stop** hook after each turn and speaks only the text inside `<spoken_summary>...</spoken_summary>` when `only_speak_spoken_summary` is true (default).

## Language

Read `lang` in the install’s `.cursor/hooks/speak_summary.toml` (default install: `~/aftertone/.cursor/hooks/speak_summary.toml`). Write **only** the inner tag text in that language. The hook does not translate.

## What to put in the tag

- One or two short sentences (capped by `spoken_summary_max_chars`, default 360).
- Plain language: no markdown, bullets, code, file paths, or URLs in the tag.
- Lead with **state** (what happened), then significance or a next move when useful.
- Calm pair-programmer tone — not a changelog or filler.

Put the block at the **very end** of the message:

```
<spoken_summary>
Your line here.
</spoken_summary>
```

Do not use `state="..."` on the opening tag or Supertonic inline tags like `<sigh>` in the body.

## Lively delivery

End **each sentence** in the tag with `!!`, `??`, `?!`, or `!?` (vary them). Default to a lively pair for vibe-coding briefings.

## When to skip

Skip the tag for trivial replies (single word, pure ack, emoji-only). Silence is fine.

## Test requests

If the user says **test** or asks to check speech, end with a short distinctive `<spoken_summary>` in the configured language, for example: “Aftertone check: if you hear this, the hook and daemon are working!!”
