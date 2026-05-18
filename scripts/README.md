# `scripts/`

| Script | Platform | Role |
|--------|----------|------|
| **`install.sh`** | Linux / macOS | One-line install (clone or update, bootstrap, global hooks). [README](../README.md#linux--macos--one-line-install) |
| **`install.ps1`** | Windows | Same flow in PowerShell. [README](../README.md#windows--one-line-install) |
| **`bootstrap.sh`** | Linux / macOS | `uv sync` in `py/`, download `Supertone/supertonic-3` into `assets/` when missing |
| **`bootstrap.ps1`** | Windows | Same as `bootstrap.sh` (no bash required) |

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
| `--start-daemon` | `-StartDaemon` | Run `tts_daemon_ctl.py start` after bootstrap |
| `--install-uv` | `-InstallUv` | Install [uv](https://docs.astral.sh/uv/) if missing |

Env: `AFTERTONE_INSTALL_DIR`, `AFTERTONE_REPO_URL`, `AFTERTONE_BRANCH`.

`bootstrap.sh` / `bootstrap.ps1` env: `SKIP_ASSETS=1`, `SKIP_WEB=1`, `FORCE_ASSETS=1`.

## Windows prerequisites

- [Git for Windows](https://git-scm.com/download/win) — `git` and **Git Bash** (`bash.exe`) for Cursor hook scripts
- [uv](https://docs.astral.sh/uv/) — or pass `-InstallUv` on `install.ps1`

User hooks on Windows use `.\hooks\aftertone-speak_summary.cmd`, which calls Git Bash and the real `speak_summary.sh` under your install dir.
