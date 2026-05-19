# Claude Code adapter

Aftertone speaks after each agent turn via **global user hooks** in `~/.claude/settings.json` and the shared **`tts_daemon`** install.

## Layout

| Path | Purpose |
|------|---------|
| `~/aftertone` (default) | Runtime from [`scripts/install.sh`](../../scripts/install.sh) — ONNX, daemon, `speak_summary.toml` |
| `~/.claude/settings.json` | **Stop** / **SubagentStop** hooks (installed on global setup) |
| `~/.claude/commands/aftertone_*.md` | Slash commands (see table below) |
| `~/.claude/rules/spoken-summary.md` | **Session rule** — loaded every turn (like Cursor’s always-on rule) |
| `~/.claude/skills/spoken-summary/` | Optional skill copy (rules are what make tags appear reliably) |
| [`claude-plugin/aftertone/`](../../claude-plugin/aftertone/) | Optional plugin (same hooks + skills if you prefer `--plugin-dir`) |

## Install

1. **Runtime + global hooks + slash commands** (one time):

   ```bash
   curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --install-uv --start-daemon
   ```

   This registers Claude **Stop** hooks in `~/.claude/settings.json` (like global Cursor hooks). You do **not** need `--plugin-dir` or a shell launcher.

2. **Daily use:**

   ```bash
   claude
   ```

   Inside the session:

   ```text
   /aftertone_on
   ```

   That starts the daemon (if needed) and sets `enabled = true`. Hooks were already registered at install; until you run `/aftertone_on`, Stop hooks run but stay silent.

3. Turn off: `/aftertone_off`

### Why `/aftertone_on` is not like `/model`

Built-in commands such as **`/model`**, **`/effort`**, and **`/fast`** are implemented **inside the Claude Code CLI**. They flip settings in the UI with **no model turn** and no token spend.

**`/aftertone_on`** and **`/aftertone_off`** are **custom skills** (markdown under `~/.claude/commands/`). Claude Code does not offer a public API for third parties to register instant native commands. The install copies those skill files and registers **Stop** hooks; toggling TTS still goes through a **small skill invocation** so you may see a brief assistant line (much smaller than a full task).

The commands use **shell preprocessing** (`!`…`` in the skill file) so the activate script runs **before** Claude reads the prompt — you are not waiting for the model to “decide” to run Bash. The `!` line must use a **literal path** (e.g. `~/.cursor/hooks/...`); Claude’s permission checker rejects `${HOME}` / `$VAR` expansion in that block. Global install also merges **`permissions.allow`** rules for those two scripts into `~/.claude/settings.json` so `/aftertone_on` does not stop on “requires approval” while `disable-model-invocation` is set. If you installed before that change, re-run install or add the allow rules manually under `/permissions`.

**Instant toggle without chat tokens** (terminal, any time):

```bash
bash ~/.cursor/hooks/aftertone-activate.sh   # on
bash ~/.cursor/hooks/aftertone-off.sh        # off
```

## Hook events

See the [Claude hooks reference](https://code.claude.com/docs/en/hooks).

| Field | Role |
|--------|------|
| `last_assistant_message` | Preferred text source |
| `transcript_path` | Fallback JSONL |
| `hook_event_name` | `Stop` or `SubagentStop` |

Hooks use **`async: true`** so TTS does not block the turn.

### Compared to [claude-code-hooks](https://github.com/shanraisshan/claude-code-hooks)

That repo plays **short MP3 cues** on many events via project `.claude/settings.json`. Aftertone is **one spoken summary per turn** on Stop, using Supertonic and `<spoken_summary>`.

## Spoken text

With default `only_speak_spoken_summary = true`, end substantive replies with:

```xml
<spoken_summary>
…
</spoken_summary>
```

Match **`lang`** in `speak_summary.toml`.

## Slash commands (global install)

Claude uses **underscores** (`/aftertone_on`). Cursor uses hyphens (`/aftertone-on`). Same behavior.

| Slash (Claude) | What it does | Instant (`!`bash) |
|----------------|--------------|---------------------|
| `/aftertone_on` | Enable TTS, start daemon if needed | Yes |
| `/aftertone_off` | Disable TTS in TOML | Yes |
| `/aftertone_toggle` | Flip `enabled` | Yes |
| `/aftertone_status` | JSON config + daemon | Yes |
| `/aftertone_restart` | Restart daemon (voice, port, GPU) | Yes |
| `/aftertone_doctor` | Full diagnostics JSON | Yes |
| `/aftertone_repair` | Re-register hooks + defaults + restart | Yes |
| `/aftertone_lang` | Set language (+ rule sync) | Picker or arg |
| `/aftertone_speed` | Set playback speed | Picker or arg |
| `/aftertone_mode` | `queue` / `interrupt` | Picker or arg |
| `/aftertone_voice` | Voice preset + daemon restart | Picker or arg |
| `/aftertone_expression` | `expression_mode` | Picker or arg |

**Instant** commands use shell preprocessing and `disable-model-invocation` (no model turn). **Picker** commands match Cursor: **AskQuestion** first when no value in the message, then one `uv run … set …` command.

Install pre-approves the instant wrapper scripts in `~/.claude/settings.json` `permissions.allow`.

## Control (CLI)

- **CLI:** `cd ~/aftertone/py && uv run python -m aftertone {on|off|toggle|status|doctor|repair|restart}`

## LLM backends

Aftertone does not choose your model. Claude Code may use Anthropic, [Ollama](https://docs.ollama.com/integrations/claude-code), or a proxy.

## Status

Global Claude hooks ship with `install.sh`. Optional plugin remains for teams that prefer `--plugin-dir`.
