# shellcheck shell=bash
# Resolve Aftertone install root for Claude plugin bin scripts.

resolve_aftertone_install() {
  local install=""

  if [[ -n "${CLAUDE_PLUGIN_OPTION_install_dir:-}" ]]; then
    install="${CLAUDE_PLUGIN_OPTION_install_dir}"
  fi
  if [[ -z "${install}" ]] && [[ -n "${AFTERTONE_INSTALL_DIR:-}" ]]; then
    install="${AFTERTONE_INSTALL_DIR}"
  fi
  if [[ -z "${install}" ]] && [[ -n "${AFTERTONE_REPO:-}" ]] \
    && [[ -f "${AFTERTONE_REPO}/py/speak_summary_prepare.py" ]]; then
    install="${AFTERTONE_REPO}"
  fi
  if [[ -z "${install}" ]] && [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
    install="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
  fi
  if [[ -z "${install}" ]]; then
    install="${HOME}/aftertone"
  fi

  # Expand leading ~ from userConfig defaults.
  if [[ "${install}" == "~/"* ]]; then
    install="${HOME}/${install#~/}"
  elif [[ "${install}" == "~" ]]; then
    install="${HOME}"
  fi

  if [[ ! -f "${install}/py/speak_summary_prepare.py" ]]; then
    return 1
  fi

  REPO="$(cd "${install}" && pwd)"
  export AFTERTONE_REPO="${REPO}"
  export AFTERTONE_INSTALL_DIR="${REPO}"
  export SUPERTONIC_REPO="${REPO}"
  return 0
}
