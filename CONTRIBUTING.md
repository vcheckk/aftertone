# Contributing to Aftertone

Thanks for helping make **local, private “hear the gist”** work across more than one tool.

## Community

- This project follows the **[Code of Conduct](CODE_OF_CONDUCT.md)**. By participating, you agree to uphold it.
- **Issues:** use [GitHub Issues](https://github.com/omarelkhal/aftertone/issues) and pick a template (**Bug report**, **Feature or idea**, **Adapter research**) so we can triage quickly.

## What we’re building

| Area | Status | Help wanted |
|------|--------|-------------|
| **Cursor** `afterAgentResponse` + `tts_daemon` | Shipped | Bugfixes, docs, Windows audio edge cases |
| **Claude Code** (or Claude Desktop hooks) | Not shipped | [Contributor todos — Claude](#claude-code-contributor-todos) |
| **OpenAI Codex** (CLI / IDE) | Not shipped | [Contributor todos — Codex](#openai-codex-contributor-todos) |
| **OpenCode**, **GitHub Copilot**, **Windsurf**, **JetBrains AI**, **Zed**, **Cline**, **Continue** | Not shipped | Same pattern: final assistant text → `speak_summary_prepare.py` or `POST /say` |
| **Core** daemon + ONNX pipeline | Shipped | Performance, GPU docs, packaging |

Optional **MCP control plane** (on/off, status, `set`, restart) lives in `py/aftertone/mcp_server.py` and [`scripts/cursor-global/mcp.aftertone.json`](scripts/cursor-global/mcp.aftertone.json). It delegates to `python -m aftertone` — **not** the post-reply speech trigger. Cursor uses **slash commands** for control; Claude/Codex adapters should reuse the same CLI and optionally expose MCP where the host supports it.

## Claude Code — contributor todos

Speech (required for “Aftertone works here”):

- [ ] **Research** — Document Claude Code / Claude Desktop hook or event APIs for “assistant turn finished” (links in an issue or `docs/adapters/claude.md`).
- [ ] **Payload** — Pipe final assistant text (or equivalent JSON) into `speak_summary_prepare.py` stdin, or `POST` prepared text to `tts_daemon` `/say` with the same fields the Cursor hook uses.
- [ ] **Install path** — Thin shell/script under a repo or user config dir; resolve install root like Cursor (`AFTERTONE_INSTALL_DIR` / install-dir marker file).
- [ ] **Config** — Read `speak_summary.toml` from the install’s `.cursor/hooks/` (shared layout today) or document an adapter-specific path if Claude requires it.
- [ ] **Model guidance** — Document `<spoken_summary>` + `summary_mode` / `lang` for agents (mirror [`.cursor/rules/spoken-summary.mdc`](.cursor/rules/spoken-summary.mdc)).
- [ ] **Smoke test** — Script or doc steps: daemon up → hook fires → audio (reuse `py/test_speak_summary_pipeline.sh` patterns where possible).

Control (optional; same CLI as Cursor slash commands):

- [ ] **MCP** — Register `aftertone.mcp_server` in Claude’s MCP config; point `uv run --directory <install>/py` at the global install root (see template JSON above).
- [ ] **MCP parity** — Extend `mcp_server.py` tools to match `python -m aftertone` (`restart`, `repair`, `set lang|speed|mode|voice`, …) or generate tools from CLI subparsers so MCP and slash commands do not drift.
- [ ] **Do not** rely on MCP alone for post-reply speech — hooks (or equivalent lifecycle) must run every turn; agents may skip MCP tools.

Docs / PR:

- [ ] README adapter row + short “Claude setup” section when the hook path is proven.
- [ ] First PR can be **docs-only** (design + links); follow-up PR ships the adapter script.

## OpenAI Codex — contributor todos

Speech (required):

- [ ] **Research** — Codex CLI / IDE “response complete” lifecycle, stdin/stdout hooks, or extension points; capture findings in an issue or `docs/adapters/codex.md`.
- [ ] **Payload** — Same contract as Cursor: prepared line → daemon (`speak_summary_prepare.py` or direct `/say` with compatible JSON).
- [ ] **Install path** — Wrapper or config snippet that works on **Windows and Linux** (no bash-only assumptions unless documented).
- [ ] **Config** — Shared `speak_summary.toml` under install `.cursor/hooks/`.
- [ ] **Model guidance** — Spoken-summary tag / `summary_mode` docs for Codex agents.
- [ ] **Smoke test** — Document or automate daemon + hook + audio check.

Control (optional):

- [ ] **MCP** — Ship Codex MCP config snippet (install-root `py`, `python -m aftertone.mcp_server`) alongside speech adapter docs.
- [ ] **MCP parity** — Same as Claude: full CLI surface via MCP tools; speech still via hook only.
- [ ] **Do not** use MCP as the only way to speak after each reply.

Docs / PR:

- [ ] README adapter row + “Codex setup” when hook path is proven.
- [ ] Docs-only research PR welcome first.

## Principles

- **Privacy first:** default path stays localhost; no cloud TTS in core.
- **Thin adapters:** keep IDE/CLI glue small; reuse `py/speak_summary_prepare.py` and `tts_daemon.py`.
- **One speakable line:** prefer `<spoken_summary>` in model output (see `.cursor/rules/spoken-summary.mdc` for Cursor; mirror the idea elsewhere).

## Dev setup

```bash
bash scripts/bootstrap.sh
cd py && uv run python tts_daemon_ctl.py start --repo-root ..
bash py/test_speak_summary_pipeline.sh   # needs ./assets/onnx + audio
```

## Pull requests

- One logical change per PR when possible.
- Run the smoke script above before claiming audio/hook fixes.
- For new adapters, add a short **doc section** in README + a row in the table above.

## Questions

Open a **Discussion** or **Issue** with the tool you’re targeting (Claude / Codex / other) and a link to any public hook or event API you’ve found — maintainers will triage.

## Starter work

Look for labels **`good first issue`** and **`help wanted`**. Suggested titles and bodies (if you want to open a fresh issue yourself) live in **[.github/STARTER_ISSUES.md](.github/STARTER_ISSUES.md)**.
