#!/usr/bin/env bash
# Print Aftertone install root (for slash commands / shell).
set -euo pipefail
if [[ -n "${AFTERTONE_REPO:-}" ]] && [[ -f "${AFTERTONE_REPO}/py/speak_summary_prepare.py" ]]; then
  echo "${AFTERTONE_REPO}"
  exit 0
fi
if [[ -n "${AFTERTONE_INSTALL_DIR:-}" ]] && [[ -f "${AFTERTONE_INSTALL_DIR}/py/speak_summary_prepare.py" ]]; then
  echo "${AFTERTONE_INSTALL_DIR}"
  exit 0
fi
if [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
  root="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
  if [[ -f "${root}/py/speak_summary_prepare.py" ]]; then
    echo "${root}"
    exit 0
  fi
fi
default="${HOME}/aftertone"
if [[ -f "${default}/py/speak_summary_prepare.py" ]]; then
  echo "${default}"
  exit 0
fi
echo "aftertone-root: install not found (run install.sh)" >&2
exit 1
