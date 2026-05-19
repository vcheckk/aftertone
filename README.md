# Aftertone

<p align="center">
  <img src="img/aftertone-logo.png" alt="Aftertone — local text-to-speech for AI coding agents and Cursor hooks" width="480">
</p>

**Hear a short spoken line after your coding agent answers** — on-device **[Supertonic](https://github.com/supertone-inc/supertonic) ONNX** through a tiny **local HTTP daemon** (models stay loaded; hooks stay fast).

### Free to use — nothing to pay for speech

| | Aftertone (this repo) |
|---|---|
| **Cost** | **$0** — open source (MIT). No paid tier for TTS. |
| **API keys** | **None** — synthesis runs on **localhost** only; your reply text never goes to a cloud TTS API. |
| **Subscription** | **None** for Aftertone — install once, use in every project. |
| **Setup** | **One install command** (below) — downloads free ONNX weights from Hugging Face; no account required for the models. |
| **Languages** | **Many locales** supported by Supertonic — set voice/language with `/aftertone-lang`; write `<spoken_summary>` in that language (the hook does not auto-translate). |

> **Note:** Your **coding agent** (Cursor, Claude, etc.) may have its own plan or API keys — that is separate from Aftertone, which only adds **local** speech after each reply.

One daemon, thin adapters per tool — **Cursor** and **Claude Code** ship today; **Codex** and **OpenCode** are on the roadmap. Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md) and the **Adapter research** issue template.

<p align="center">
  <a href="https://buymeacoffee.com/elkhalomar"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy me a coffee" width="217" height="60" /></a>
</p>

## Works with

<p align="center">
  <strong>AI coding agents &amp; IDEs</strong><br>
  <sub>Same local <code>tts_daemon</code> — each adapter wires “reply finished” → short spoken line</sub>
</p>

<div align="center">
  <table>
    <tr>
      <td align="center" width="140">
        <a href="https://cursor.com" title="Cursor"><img src="https://cdn.simpleicons.org/cursor/1a1714" alt="Cursor" height="44" /></a><br>
        <strong>Cursor</strong><br>
        <sub>✅ Available</sub>
      </td>
      <td align="center" width="140">
        <a href="https://docs.anthropic.com/en/docs/claude-code" title="Claude Code"><img src="img/adapters/claude.svg" alt="Claude Code" height="44" /></a><br>
        <strong>Claude Code</strong><br>
        <sub>✅ Available</sub>
      </td>
      <td align="center" width="140">
        <a href="https://developers.openai.com/codex" title="OpenAI Codex"><img src="img/adapters/codex.svg" alt="Codex" height="44" style="opacity:0.55" /></a><br>
        <strong>Codex</strong><br>
        <sub>Coming soon</sub>
      </td>
      <td align="center" width="140">
        <a href="https://opencode.ai" title="OpenCode"><img src="img/adapters/opencode.svg" alt="OpenCode" height="44" style="opacity:0.55" /></a><br>
        <strong>OpenCode</strong><br>
        <sub>Coming soon</sub>
      </td>
    </tr>
  </table>
</div>

<p align="center">
  <sub>Missing your stack? Open an <a href="https://github.com/omarelkhal/aftertone/issues/new?template=adapter_research.md">adapter research</a> issue — tracked in <a href="CONTRIBUTING.md#what-were-building">CONTRIBUTING</a>.</sub>
</p>

## Discovery

If you are searching for **free local text-to-speech**, **no API key** TTS, **on-device** assistants, **AI coding agent** tooling, **agentic coding** workflows, or **Cursor IDE** **hooks** that do not send your thread to a cloud API — Aftertone is a small **open source** **developer tool**: **ONNX Runtime** + **Supertonic** for optional **voice** feedback after the model answers, **offline**-friendly and **privacy**-minded. **Install once** — no Aftertone subscription.

**Related GitHub topics:** [ai-agents](https://github.com/topics/ai-agents) · [coding-agent](https://github.com/topics/coding-agent) · [cursor](https://github.com/topics/cursor) · [text-to-speech](https://github.com/topics/text-to-speech) · [onnx](https://github.com/topics/onnx) · [local-first](https://github.com/topics/local-first) · [developer-tools](https://github.com/topics/developer-tools) · [open-source](https://github.com/topics/open-source)

## Features (today)

- **Cursor:** `afterAgentResponse` → optional TTS from inline reply text (prefers the **last** `<spoken_summary>…</spoken_summary>` at the end of the reply).
- **Claude Code:** global **Stop** hook + `~/.claude/commands/aftertone_*.md` slash commands (underscores, e.g. `/aftertone_on`). See [docs/adapters/claude.md](docs/adapters/claude.md).
- **Flow briefings:** agents write a short listening line (state, why it matters, optional next move) — see [spoken-summary rule](.cursor/rules/spoken-summary.mdc). Repo default: **`summary_mode = "tag_only"`** (only the tag is spoken; set **`auto`** in TOML for heuristic fallback when the model omits the tag).
- **Livelier delivery:** end each sentence in the tag with `!!`, `??`, `?!`, or `!?` (Supertonic prosody); **`expression_mode = "off"`** by default (inline `<sigh>` tags are optional via `/aftertone-expression`).
- **Slash commands** in Cursor (`/aftertone-lang`, …) and Claude Code (`/aftertone_lang`, …) — each runs **one** `python -m aftertone …` call (writes TOML; restarts the daemon when needed). No hand-editing TOML for everyday changes.
- **v2 CLI:** `cd py && uv run python -m aftertone {on|off|toggle|status|restart|repair|doctor|set …}` — same contract as slash commands; install root from `aftertone-install-dir` or `AFTERTONE_INSTALL_DIR`.
- `speak_summary_prepare.py` → JSON for `POST /say`; `tts_daemon.py` → localhost server.
- Optional `stop` hook trace for debugging.
- `bash scripts/bootstrap.sh` or `scripts/bootstrap.ps1` (Windows) — `uv sync`, Hugging Face assets if `assets/onnx/` is missing.

## Requirements

- **Linux / macOS:** [uv](https://docs.astral.sh/uv/getting-started/installation/) (or use `--install-uv` on the one-liner).
- **Windows:** [Git for Windows](https://git-scm.com/download/win) only — the one-liner installs **uv**, Python **3.13**, models, hooks, and the daemon for you.
- **Cursor (current adapter):** Hooks on, **trusted** workspace, `.cursor/hooks.json` with `"version": 1`.
- ONNX weights under `./assets` (`Supertone/supertonic-3` — bootstrap downloads them).

## Quick start

Install **once** to a fixed folder (`~/aftertone` or `%USERPROFILE%\aftertone`), register **user-level Cursor hooks**, then use spoken TTS in **every project** you open.

### Linux / macOS — one-line install

Requires **git** and **bash**.

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --install-uv --start-daemon
```

Options (pass after `bash -s --`):

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --dir ~/code/aftertone
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --no-global   # skip ~/.cursor hooks
```

### Windows — one-line install

Requires **git** and **Git Bash** ([Git for Windows](https://git-scm.com/download/win)). Run in **PowerShell** — one command installs everything to the right places:

```powershell
irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1 | iex
```

That clones/updates **`%USERPROFILE%\aftertone`**, installs **uv** + Python **3.13**, downloads ONNX assets, registers **`%USERPROFILE%\.cursor\hooks.json`**, starts **`tts_daemon`**, and turns spoken TTS **on** in config. Re-runs reset a dirty clone to `origin/main` automatically.

After install:

- **Cursor:** enable **Hooks** in Settings and **trust** your workspace(s).
- **Claude Code:** run `claude`, then `/aftertone_on` in chat (hooks are already in `~/.claude/settings.json`; the command enables TTS and starts the daemon if needed). Full guide: [docs/adapters/claude.md](docs/adapters/claude.md).

Optional flags (download script first, then invoke): `-NoStartDaemon`, `-NoGlobal`, `-SkipAssets`, `-NoEnableTts`.

**Legacy:** copy hooks + `py/` into one repo (`--into .` on Linux, or `--no-global` on Windows) — only if you cannot use global hooks.

See [`scripts/install.sh`](scripts/install.sh), [`scripts/install.ps1`](scripts/install.ps1), and [`scripts/README.md`](scripts/README.md).

### Uninstall

Stops the daemon, removes **global** Cursor hooks and slash commands, and deletes the install directory (including large ONNX assets) unless you opt out.

**Linux / macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/uninstall.sh | bash
```

Options (pass after `bash -s --`):

```bash
curl -fsSL .../uninstall.sh | bash -s -- --keep-dir    # hooks only; keep ~/aftertone
curl -fsSL .../uninstall.sh | bash -s -- --dir ~/code/aftertone --yes
```

From an existing clone: `bash scripts/uninstall.sh` (same flags).

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/uninstall.ps1 | iex
```

Options:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -KeepDir
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -InstallDir D:\aftertone -Yes
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -DryRun
```

From an existing clone: `powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1` (same flags).

**Mute without uninstalling:** `/aftertone-off` in Agent chat (or `speak_summary_toggle.py off`) — hooks stay registered; no speech when `only_speak_spoken_summary = true`.

**Per-project / legacy:** if you used `install.sh --no-global --into .`, remove `afterAgentResponse` from that repo’s `.cursor/hooks.json` and delete the copied `py/` tree yourself; global uninstall does not edit other projects.

### Manual clone

**Linux / macOS:**

```bash
git clone https://github.com/omarelkhal/aftertone.git
cd aftertone
bash scripts/bootstrap.sh
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/omarelkhal/aftertone.git
cd aftertone
powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1
```

**Cursor:** enable **Hooks** in Settings and **trust** each workspace where you want TTS. After a global install, hooks live in your user **`.cursor/hooks.json`** (not in every project). Slash commands are copied to **`.cursor/commands/`**; config still reads **`<install-dir>/.cursor/hooks/speak_summary.toml`** (default install dir above).

- **Daemon:** `cd py && uv run python -m aftertone restart` (or `tts_daemon_ctl.py start --repo-root ..` then `status`)
- **Smoke (needs assets + audio):** `bash py/test_speak_summary_pipeline.sh` (Git Bash on Windows)
- **Diagnostics:** `uv run --directory py python -m aftertone doctor` or `bash py/diagnose_speak_hooks.sh` (Git Bash on Windows). Replay a saved hook payload: `bash py/diagnose_speak_hooks.sh path/to/hook.json`

### Repo root env (any adapter)

Hooks and Python resolve the install root via **`AFTERTONE_REPO`** (preferred) or legacy **`SUPERTONIC_REPO`**.

### Global install layout

| Path (Linux / macOS) | Path (Windows) | Purpose |
|----------------------|----------------|---------|
| `~/aftertone/` | `%USERPROFILE%\aftertone\` | One clone: `py/`, `assets/`, config TOML, daemon |
| `~/.cursor/hooks.json` | `%USERPROFILE%\.cursor\hooks.json` | User hooks → speak_summary wrapper |
| `~/.cursor/hooks/aftertone-install-dir` | `%USERPROFILE%\.cursor\hooks\aftertone-install-dir` | Points at install dir |
| `~/.cursor/commands/aftertone-*.md` | `%USERPROFILE%\.cursor\commands\aftertone-*.md` | Cursor slash commands (hyphens) |
| `~/.claude/commands/aftertone_*.md` | — | Claude Code slash commands (underscores) |
| `~/.claude/settings.json` | — | Claude **Stop** hooks (from install) |
| `~/.claude/rules/spoken-summary.md` | — | Claude session rule for `<spoken_summary>` |

On **Linux / macOS**, the hook command is `bash ./hooks/aftertone-speak_summary.sh`. On **Windows**, it is `.\hooks\aftertone-speak_summary.cmd` (delegates to Git Bash + `speak_summary.sh`).

### Copy into another repo (legacy)

`install.sh --no-global --into .` duplicates hooks + `py/` in that repo. Prefer the global install above.

## Control (slash commands)

In **Agent** chat, type **`/`** and pick an **`aftertone-`** command (Cursor: hyphens; Claude Code: underscores — see [Claude adapter](docs/adapters/claude.md)). Available in any workspace after global install. That is the **supported** way to change spoken-TTS settings — do **not** hand-edit [`.cursor/hooks/speak_summary.toml`](.cursor/hooks/speak_summary.toml) for everyday changes.

### Cursor (`/aftertone-on`, …)

| Command | What it does | Daemon restart? |
|---------|----------------|-----------------|
| `/aftertone-toggle` | Flip spoken TTS on/off | No |
| `/aftertone-on` / `/aftertone-off` | Force on or off | No |
| `/aftertone-status` | Current settings + daemon health | No |
| `/aftertone-lang` | Pick language (syncs [spoken-summary rule](.cursor/rules/spoken-summary.mdc)) | No |
| `/aftertone-speed` | Pick playback speed | No |
| `/aftertone-mode` | Pick `queue` or `interrupt` | No |
| `/aftertone-expression` | Supertonic inline expression tags (`off` / `subtle` / …); repo default **`off`** | No |
| `/aftertone-voice` | Pick a voice (e.g. Sara (female), James (male)) | **Yes** (command restarts for you) |
| `/aftertone-restart` | Reload daemon after **port**, **voice**, **onnx_dir**, **use_gpu**, or **total_step** changes | **Yes** |
| `/aftertone-doctor` | Diagnostics (hooks, config, daemon, assets) | No |
| `/aftertone-repair` | Re-register global hooks, apply install defaults, restart daemon | **Yes** |

Command definitions: [`.cursor/commands/`](.cursor/commands/). Each command tells the agent to run **one** CLI invocation from the install root (no bash chains, no hand-edited TOML).

### Claude Code (`/aftertone_on`, …)

Same surface with **underscores** — e.g. `/aftertone_on`, `/aftertone_lang`, `/aftertone_status`. Copied to `~/.claude/commands/` on install; **Stop** hooks live in `~/.claude/settings.json`. Run **`/aftertone_on`** per session to enable speech (daemon start + `enabled = true`). Guide: [docs/adapters/claude.md](docs/adapters/claude.md). Command sources: [`claude-plugin/aftertone/commands/`](claude-plugin/aftertone/commands/).

**CLI (install root or `aftertone-install-dir`):**

```bash
cd "$(cat ~/.cursor/hooks/aftertone-install-dir)"   # or %USERPROFILE%\.cursor\hooks\aftertone-install-dir on Windows
uv run --directory py python -m aftertone status
uv run --directory py python -m aftertone set lang fr
uv run --directory py python -m aftertone set voice F4 --ensure
uv run --directory py python -m aftertone restart
```

**Lower level:** `cd py && uv run python tts_daemon_ctl.py {start|stop|status|restart} --repo-root ..` — see [`.cursor/hooks/README.md`](.cursor/hooks/README.md). Prefer **`/aftertone-restart`** or **`aftertone restart`** when voice or port changed. Turning TTS **off** via `/aftertone-off` does not unload models; use **stop** when you want silence and no GPU/RAM use.

### Spoken summaries (agents)

Put **one** `<spoken_summary>…</spoken_summary>` block at the **very end** of substantive replies (plain language, same language as TOML `lang`). The hook pairs the **last** closing tag with the nearest opening tag before it — so do not leave an unclosed `<spoken_summary>` mention in code or prose above your real tag.

For **vibe coding**, write a hybrid pair-programmer briefing: what happened, why it matters, optional next move. For livelier TTS, end **each sentence** in the tag with `!!`, `??`, `?!`, or `!?`. Full guidance: [`.cursor/rules/spoken-summary.mdc`](.cursor/rules/spoken-summary.mdc).

## Spoken summary latency (Windows vs Linux / macOS)

**Aftertone is not the whole story for “how long until I hear something?”** On **Linux and macOS**, the path from “agent finished typing” to “hook runs” is usually short. On **Windows**, many users see a **much longer gap** between the reply appearing in chat and the hook actually starting — even when Aftertone’s own hook script and daemon only take a few seconds once they run.

That delay is **outside Aftertone**: [Cursor runs `afterAgentResponse` hooks on Windows with high scheduling and process-startup overhead](https://forum.cursor.com/t/hook-execution-reports-8-seconds-delay-despite-actual-execution-taking-only-5ms/147584). Cursor staff have [acknowledged the issue](https://forum.cursor.com/t/hook-execution-reports-8-seconds-delay-despite-actual-execution-taking-only-5ms/147584) and described work to reduce shell/process launch cost; we hope that improves in future Cursor releases.

**What Aftertone controls:** preparing text, talking to `tts_daemon`, and ONNX synthesis/playback. **What we do not control:** when Cursor invokes the hook after the assistant message is done.

If timing feels wrong:

1. Run **`/aftertone-doctor`** or `uv run --directory py python -m aftertone doctor`.
2. Inspect **`speak_summary-hook.log`** and **`pipeline_trace.jsonl`** under `.cursor/hooks/state/` — look for `hook_minus_transcript_mtime_ms` (gap before our hook) vs `first_sound_since_hook_ms` (our side after the hook starts).
3. Compare on **Ubuntu or macOS** if you can — same project, same Cursor hooks.
4. **Update Cursor** — newer builds include hook performance work; see the forum thread above.

More detail: [docs — Windows hook latency](https://omarelkhal.github.io/aftertone/docs.html#windows-hook-latency).

## Configuration

| Doc / file | Role |
|------------|------|
| **[`.cursor/hooks/README.md`](.cursor/hooks/README.md)** | **Full TOML reference:** every `speak_summary.toml` key, valid `lang` codes, heuristics, `quiet_hours`, daemon **start / stop / status / restart**, logs, when changes need a restart. |
| [`.cursor/hooks/speak_summary.toml`](.cursor/hooks/speak_summary.toml) | On-disk config (updated by slash commands and install). |
| [`.cursor/rules/spoken-summary.mdc`](.cursor/rules/spoken-summary.mdc) | When/how agents emit `<spoken_summary>`; **match TOML `lang`**. |
| **[`AGENTS.md`](AGENTS.md)** | Agent-oriented digest (flow, verify hooks, caps, “nothing speaks”). |

## Support

<p align="center">
  <a href="https://buymeacoffee.com/elkhalomar"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy me a coffee" width="217" height="60" /></a>
</p>

If Aftertone saves you from reading every agent wall of text, tips help fund maintenance, docs, and adapters (Claude Code, Codex, OpenCode). Code contributions are always welcome too — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** and the **[Code of Conduct](CODE_OF_CONDUCT.md)**. **Issues:** [open one here](https://github.com/omarelkhal/aftertone/issues) — use a template (**Bug report**, **Feature or idea**, **Adapter research**). Starter ideas: [.github/STARTER_ISSUES.md](.github/STARTER_ISSUES.md).

## Website

**[aftertone on GitHub Pages](https://omarelkhal.github.io/aftertone/)** — home + **[docs](https://omarelkhal.github.io/aftertone/docs.html)** (one-line install, slash commands, daemon, troubleshooting). Built from [`docs/`](docs/).

## License

MIT — [LICENSE](LICENSE). Supertonic-derived code: [NOTICE](NOTICE).
