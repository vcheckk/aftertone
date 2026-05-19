#!/usr/bin/env bash
# User-level Claude Code Stop / SubagentStop hook (~/.claude/settings.json).
# Delegates to the global Aftertone install (same pipeline as Cursor).
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
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") aftertone-claude-stop: missing ${TARGET}" \
    >>"${HOME}/.cursor/hooks/state/speak_summary-hook.log" 2>/dev/null || true
  exit 0
fi
exec bash "${TARGET}"
