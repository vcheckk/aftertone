#!/usr/bin/env bash
# User-level Cursor hook (~/.cursor/hooks/). Delegates to the global Aftertone install.
set -uo pipefail
INSTALL="${AFTERTONE_INSTALL_DIR:-${HOME}/aftertone}"
if [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
  INSTALL="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
fi
export AFTERTONE_REPO="${INSTALL}"
export AFTERTONE_INSTALL_DIR="${INSTALL}"
TARGET="${INSTALL}/.cursor/hooks/speak_summary.sh"
if [[ ! -f "${TARGET}" ]]; then
  mkdir -p "${HOME}/.cursor/hooks/state"
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") aftertone-speak_summary: missing ${TARGET}" \
    >>"${HOME}/.cursor/hooks/state/speak_summary-hook.log" 2>/dev/null || true
  exit 0
fi
exec bash "${TARGET}"
