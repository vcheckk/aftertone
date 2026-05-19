# Aftertone — Claude Code plugin (optional)

Local **post-reply TTS** for [Claude Code](https://code.claude.com/). **Recommended path:** global install — run plain `claude`, then **`/aftertone_on`** in chat. See [docs/adapters/claude.md](../../docs/adapters/claude.md).

This plugin folder is **optional** if you already ran `install.sh` (hooks land in `~/.claude/settings.json`).

## Default flow (no plugin)

1. `install.sh --install-uv --start-daemon`
2. `claude`
3. `/aftertone_on`

## Optional: use this plugin instead

```bash
claude --plugin-dir /path/to/aftertone/claude-plugin/aftertone
```

Set **install_dir** to `~/aftertone` on first enable. `/reload-plugins` after edits.

## What ships here

| Piece | Role |
|--------|------|
| `hooks/hooks.json` | Same Stop hooks as global install (when plugin is loaded) |
| `commands/aftertone_*.md` | Copied to `~/.claude/commands/` on install (on, off, status, lang, …) |
| `skills/spoken-summary/` | `<spoken_summary>` guidance |
| `skills/aftertone_on/` | Plugin-namespaced `/aftertone:aftertone_on` |

## Troubleshooting

- No audio: `tail -30 ~/aftertone/.cursor/hooks/state/speak_summary-hook.log`
- Daemon: `cd ~/aftertone/py && uv run python tts_daemon_ctl.py status --repo-root ..`
