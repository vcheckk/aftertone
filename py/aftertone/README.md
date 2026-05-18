# Aftertone v2 runtime

Modular package for post-reply TTS. The hook calls `aftertone.prepare`; control plane is `python -m aftertone`.

| Module | Role |
|--------|------|
| `config.py` | TOML load, `summary_mode` (`tag_only` default / `auto` / `heuristic`) |
| `defaults.py` | Install defaults: `tag_only`, `total_step = 8` |
| `hook_json.py` | UTF-16 stdin, Windows JSON path escapes |
| `extract.py` | Hook + transcript text resolution |
| `summary.py` | Tag vs auto-extract router |
| `prepare.py` | Build `/say` JSON from hook stdin |
| `cli.py` | Cross-platform `aftertone` commands |
| `doctor.py` | Install / hook / daemon diagnostics |
| `mcp_server.py` | Optional MCP control tools (not speech trigger) |

Audit notes: [`docs/V2_AUDIT.md`](../../docs/V2_AUDIT.md).
