#!/usr/bin/env bash
# Claude Code Stop hook: delegate to the Aftertone install speak_summary.sh (stdin preserved).
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
  log_claude "missing_install hint=run scripts/install.sh from github.com/omarelkhal/aftertone"
  exit 0
fi

TARGET="${AFTERTONE_INSTALL_DIR}/.cursor/hooks/speak_summary.sh"
if [[ ! -f "${TARGET}" ]]; then
  log_claude "missing ${TARGET}"
  exit 0
fi

exec bash "${TARGET}"
