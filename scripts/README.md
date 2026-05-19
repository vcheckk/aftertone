# `scripts/`

| Script | Platform | Role |
|--------|----------|------|
| **`install.sh`** | Linux / macOS | One-line install (clone or update, bootstrap, global hooks). [README](../README.md#linux--macos--one-line-install) |
| **`install.ps1`** | Windows | Same flow in PowerShell. [README](../README.md#windows--one-line-install) |
| **`uninstall.sh`** | Linux | Stop daemon, remove global Cursor hooks, optionally delete install tree. [README](../README.md#uninstall-linux) |
| **`uninstall.ps1`** | Windows | Stop daemon, remove global Cursor hooks, optionally delete install tree. [README](../README.md#uninstall) |
| **`bootstrap.sh`** | Linux / macOS | `uv sync` in `py/`, download `Supertone/supertonic-3` into `assets/` when missing |
| **`bootstrap.ps1`** | Windows | Same as `bootstrap.sh` (no bash required) |
| **`repair-windows-hooks.ps1`** | Windows | Re-register global hooks, enable TTS, remove clashing project `hooks.json` |
| **`aftertone-root.sh`** | all (bash) | Resolve install path; copied to `~/.cursor/hooks/` by install |
| **`aftertone_on`** | Linux / macOS | Start Claude Code with the Aftertone plugin (`~/.local/bin/aftertone_on` after install) |
| **`cursor-global/`** | all | Templates for `install_global_hooks.py` (`.cmd` + `hooks.windows.json`) |

## Aftertone v2 CLI

From install root (`~/aftertone` or `%USERPROFILE%\aftertone`):

```bash
uv run --directory py python -m aftertone on|off|toggle|status|restart|repair|apply-defaults|doctor|speak "hello"
```

- **`summary_mode = "tag_only"`** (default): only `<spoken_summary>` is spoken. Use **`auto`** for fallback extraction when the tag is missing.
- Optional MCP template: [`cursor-global/mcp.aftertone.json`](cursor-global/mcp.aftertone.json) — control only, not the speech trigger.

Hook replay: `bash py/diagnose_speak_hooks.sh [hook.json]`

Python **3.13** is pinned in `py/.python-version` (onnxruntime wheels; avoid system Python 3.14+ on Windows).

## `install.sh` / `install.ps1` options

| `install.sh` | `install.ps1` | Meaning |
|--------------|---------------|---------|
| `--dir PATH` | `-InstallDir PATH` | Clone location (default `~/aftertone` or `%USERPROFILE%\aftertone`) |
| `--global` | (default) | Register user hooks in `.cursor/` |
| `--no-global` | `-NoGlobal` | Skip `.cursor/hooks.json` registration |
| `--into PATH` | — | **Legacy (bash only):** copy hooks + `py/` into another repo |
| `--branch NAME` | `-Branch NAME` | Git branch (default `main`) |
| `--skip-assets` | `-SkipAssets` | Skip model download |
| `--start-daemon` | (default on Windows) | Run `tts_daemon_ctl.py start` after bootstrap |
| `--install-uv` | (default on Windows) | Install [uv](https://docs.astral.sh/uv/) if missing |
| — | `-NoStartDaemon` | Skip daemon start (Windows only) |
| — | `-NoEnableTts` | Leave `enabled=false` in TOML (Windows only) |

Env: `AFTERTONE_INSTALL_DIR`, `AFTERTONE_REPO_URL`, `AFTERTONE_BRANCH`.

`bootstrap.sh` / `bootstrap.ps1` env: `SKIP_ASSETS=1`, `SKIP_WEB=1`, `FORCE_ASSETS=1`.

## `uninstall.sh` / `uninstall.ps1` options

| `uninstall.sh` | `uninstall.ps1` | Meaning |
|----------------|-----------------|---------|
| `--dir PATH` | `-InstallDir PATH` | Install root (default: marker file, then `~/aftertone` or `%USERPROFILE%\aftertone`) |
| `--keep-dir` | `-KeepDir` | Remove hooks only; keep clone and `assets/` |
| `--no-global` | `-NoGlobal` | Skip user `.cursor` cleanup (daemon stop + delete install dir only) |
| `--yes` | `-Yes` | Do not prompt before deleting install directory |
| `--dry-run` | `-DryRun` | Print planned actions |

Env: `AFTERTONE_INSTALL_DIR`, `AFTERTONE_UNINSTALL_RAW_BASE` (override raw GitHub URL prefix for hook scripts when the install tree is already gone).

## Windows prerequisites

- [Git for Windows](https://git-scm.com/download/win) — `git` and **Git Bash** (`bash.exe`) for Cursor hook scripts
- [uv](https://docs.astral.sh/uv/) — or pass `-InstallUv` on `install.ps1`

User hooks on Windows use `.\hooks\aftertone-speak_summary.cmd`, which calls Git Bash and the real `speak_summary.sh` under your install dir.
