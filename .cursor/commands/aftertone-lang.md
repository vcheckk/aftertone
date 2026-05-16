---
name: aftertone-lang
description: Pick Aftertone spoken-summary language and sync the agent rule
---

## Speed rule (required)

**Do not** plan, explain, or run shell before the user picks (unless they gave a code in this message, e.g. `/aftertone-lang fr`).

Your **first** tool call must be **AskQuestion**.

## Picker options (first tool call)

`allow_multiple: false`. Options:

- en — English (en)
- fr — French (fr)
- de — German (de)
- es — Spanish (es)
- it — Italian (it)
- pt — Portuguese (pt)
- ja — Japanese (ja)
- ko — Korean (ko)
- ar — Arabic (ar)
- hi — Hindi (hi)
- ru — Russian (ru)
- nl — Dutch (nl)
- pl — Polish (pl)
- tr — Turkish (tr)
- vi — Vietnamese (vi)
- other — Other language (type the code next)

If they pick **other**, ask once for a code, then validate with `speak_summary_config.py langs`.

## Apply (after pick)

```bash
AFTERTONE_ROOT="$(bash "${HOME}/.cursor/hooks/aftertone-root.sh")"
uv run --directory "${AFTERTONE_ROOT}/py" python speak_summary_config.py set lang CODE
```

One-line reminder: `<spoken_summary>` should use that language.
