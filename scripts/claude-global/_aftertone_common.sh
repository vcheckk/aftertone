# Shared helpers for Claude slash-command wrappers (source, do not execute).
_aftertone_resolve_install() {
  AFTERTONE_INSTALL="${AFTERTONE_INSTALL_DIR:-${HOME}/aftertone}"
  if [[ -f "${HOME}/.cursor/hooks/aftertone-install-dir" ]]; then
    AFTERTONE_INSTALL="$(tr -d '\n\r' <"${HOME}/.cursor/hooks/aftertone-install-dir")"
  fi
}

_aftertone_require_install() {
  _aftertone_resolve_install
  if [[ ! -f "${AFTERTONE_INSTALL}/py/speak_summary_prepare.py" ]]; then
    echo "aftertone: not installed. Run install.sh from github.com/omarelkhal/aftertone" >&2
    exit 1
  fi
  if ! command -v uv >/dev/null 2>&1; then
    echo "aftertone: uv not in PATH (re-run install.sh --install-uv)" >&2
    exit 1
  fi
}

_aftertone_uv() {
  (cd "${AFTERTONE_INSTALL}/py" && uv run python -m aftertone --repo-root .. "$@")
}
