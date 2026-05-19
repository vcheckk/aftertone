#!/usr/bin/env bash
# Enable Aftertone for the current machine: daemon up + enabled in speak_summary.toml.
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=resolve-install.sh
source "${PLUGIN_ROOT}/bin/resolve-install.sh"

if ! resolve_aftertone_install; then
  echo "aftertone_on: install not found (set plugin install_dir or run scripts/install.sh)" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "aftertone_on: uv not in PATH (re-run install.sh --install-uv)" >&2
  exit 1
fi

port=8765
port_file="${REPO}/.cursor/hooks/state/tts-daemon.port"
if [[ -f "${port_file}" ]]; then
  port="$(tr -d ' \n\r' <"${port_file}")"
fi

if ! curl -fsS -m 0.5 "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; then
  echo "aftertone_on: starting TTS daemon…"
  (cd "${REPO}/py" && uv run python tts_daemon_ctl.py start --repo-root ..)
fi

(cd "${REPO}/py" && uv run python -m aftertone --repo-root .. on)
(cd "${REPO}/py" && uv run python -m aftertone --repo-root .. doctor)

echo "aftertone_on: TTS enabled (install: ${REPO}). Speech runs on Stop when the plugin is loaded and replies include <spoken_summary>."
