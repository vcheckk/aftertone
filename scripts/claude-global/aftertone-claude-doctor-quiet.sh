#!/usr/bin/env bash
# Claude Code SessionStart (startup): log if daemon is down; never block.
set -uo pipefail
INSTALL="${AFTERTONE_INSTALL_DIR:-${HOME}/aftertone}"
if [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
  INSTALL="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
fi
LOG_DIR="${HOME}/.cursor/hooks/state"
LOG="${LOG_DIR}/speak_summary-hook.log"
log_line() {
  mkdir -p "${LOG_DIR}" 2>/dev/null || true
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") aftertone-claude: $*" >>"${LOG}" 2>/dev/null || true
}
if [[ ! -f "${INSTALL}/py/speak_summary_prepare.py" ]]; then
  log_line "session_start install_missing hint=run scripts/install.sh"
  exit 0
fi
PORT=8765
PORT_FILE="${INSTALL}/.cursor/hooks/state/tts-daemon.port"
TOML="${INSTALL}/.cursor/hooks/speak_summary.toml"
if [[ -f "${PORT_FILE}" ]]; then
  PORT="$(tr -d ' \n\r' <"${PORT_FILE}")"
elif [[ -f "${TOML}" ]]; then
  PORT="$(grep -E '^[[:space:]]*port[[:space:]]*=' "${TOML}" | head -1 | sed -E 's/.*=[[:space:]]*//' | tr -d ' \"')"
fi
if curl -fsS -m 0.5 "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
  exit 0
fi
log_line "session_start daemon_down port=${PORT} hint=run /aftertone_on in Claude"
exit 0
