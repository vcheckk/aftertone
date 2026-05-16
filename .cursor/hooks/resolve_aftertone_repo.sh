# shellcheck shell=bash
# Resolve Aftertone install root for hook scripts (global install or in-repo).
# Sets REPO on success; returns 1 if not found.

resolve_aftertone_repo() {
  local script_dir="$1"
  local repo="" install=""

  if [[ -n "${AFTERTONE_REPO:-}" ]] && [[ -f "${AFTERTONE_REPO}/py/speak_summary_prepare.py" ]]; then
    REPO="$(cd "${AFTERTONE_REPO}" && pwd)"
    return 0
  fi

  install="${AFTERTONE_INSTALL_DIR:-}"
  if [[ -z "${install}" ]] && [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
    install="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
  fi
  if [[ -n "${install}" ]] && [[ -f "${install}/py/speak_summary_prepare.py" ]]; then
    REPO="$(cd "${install}" && pwd)"
    return 0
  fi

  repo="${script_dir}"
  while [[ "${repo}" != "/" ]]; do
    if [[ -f "${repo}/py/speak_summary_prepare.py" ]]; then
      REPO="${repo}"
      return 0
    fi
    repo="$(dirname "${repo}")"
  done
  return 1
}
