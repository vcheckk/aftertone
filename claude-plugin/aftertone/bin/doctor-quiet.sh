#!/usr/bin/env bash
# SessionStart: log if Aftertone daemon is down; never block the session.
set -uo pipefail

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=resolve-install.sh
source "${BIN_DIR}/resolve-install.sh"

LOG_DIR="${HOME}/.cursor/hooks/state"
LOG="${LOG_DIR}/speak_summary-hook.log"

log_claude() {
  mkdir -p "${LOG_DIR}" 2>/dev/null || true
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") claude-plugin: $*" >>"${LOG}" 2>/dev/null || true
}

if ! resolve_aftertone_install; then
  log_claude "session_start install_missing hint=bash scripts/install.sh --install-uv --start-daemon"
  exit 0
fi

PORT=8765
TOML="${AFTERTONE_INSTALL_DIR}/.cursor/hooks/speak_summary.toml"
PORT_FILE="${AFTERTONE_INSTALL_DIR}/.cursor/hooks/state/tts-daemon.port"
if [[ -f "${PORT_FILE}" ]]; then
  PORT="$(tr -d ' \n\r' <"${PORT_FILE}")"
elif [[ -f "${TOML}" ]]; then
  PORT="$(grep -E '^[[:space:]]*port[[:space:]]*=' "${TOML}" | head -1 | sed -E 's/.*=[[:space:]]*//' | tr -d ' \"')"
fi

if curl -fsS -m 0.5 "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
  exit 0
fi

log_claude "session_start daemon_down port=${PORT} hint=cd \"${AFTERTONE_INSTALL_DIR}/py\" && uv run python tts_daemon_ctl.py start --repo-root .."
exit 0
