---
description: Set Aftertone spoken-summary language (TOML + rule sync). Use when the user runs /aftertone_lang.
---

## Agent rule

**No planning.** Do not explain or run shell first unless the user gave a language code in this message (e.g. `/aftertone_lang fr`).

If no code was given, your **first** tool call must be **AskQuestion** (`allow_multiple: false`):

| id | label |
|----|-------|
| en | English (en) |
| fr | French (fr) |
| de | German (de) |
| es | Spanish (es) |
| it | Italian (it) |
| pt | Portuguese (pt) |
| ja | Japanese (ja) |
| ko | Korean (ko) |
| ar | Arabic (ar) |
| hi | Hindi (hi) |
| ru | Russian (ru) |
| nl | Dutch (nl) |
| pl | Polish (pl) |
| tr | Turkish (tr) |
| vi | Vietnamese (vi) |

If they need another code, ask once, then validate with the command below (invalid codes error from the CLI).

## Apply (one command only)

Read install root from `~/.cursor/hooks/aftertone-install-dir` (first line), then run **only**:

```
uv run --directory INSTALL/py python -m aftertone set lang CODE
```

Replace `INSTALL` with that path and `CODE` with the pick or user value. No hand-editing TOML. No daemon restart. Report stdout only.
