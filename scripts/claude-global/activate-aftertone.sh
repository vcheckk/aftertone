#!/usr/bin/env bash
# Enable Aftertone: daemon up + enabled in speak_summary.toml (used by /aftertone_on).
set -euo pipefail
source "$(dirname "$0")/_aftertone_common.sh"
_aftertone_require_install
port=8765
port_file="${AFTERTONE_INSTALL}/.cursor/hooks/state/tts-daemon.port"
if [[ -f "${port_file}" ]]; then
  port="$(tr -d ' \n\r' <"${port_file}")"
fi
if ! curl -fsS -m 0.5 "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; then
  echo "aftertone_on: starting TTS daemon…"
  (cd "${AFTERTONE_INSTALL}/py" && uv run python tts_daemon_ctl.py start --repo-root ..)
fi
_aftertone_uv on
echo "aftertone_on: spoken TTS is on!! Hooks are already in your Claude settings — speech runs after each reply when you use <spoken_summary>. Use /aftertone_doctor for diagnostics."
