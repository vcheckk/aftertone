#!/usr/bin/env bash
# Aftertone / Cursor hook: speak a short summary via tts_daemon (afterAgentResponse preferred — has inline `text`;
# `stop` often lacks transcript_path). See speak_summary_prepare.py / aftertone.hook_run.
# Never fails the hook: always exits 0.
#
# If nothing speaks, check:
#   tail -50 .cursor/hooks/state/speak_summary-hook.log
#   tail -50 .cursor/hooks/state/speak_summary-prepare.stderr.log
# Run once: cd py && uv sync   (creates py/.venv so hooks work without `uv` on GUI PATH)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=resolve_aftertone_repo.sh
source "${SCRIPT_DIR}/resolve_aftertone_repo.sh"
# shellcheck source=venv_python.sh
source "${SCRIPT_DIR}/venv_python.sh"
REPO=""
if ! resolve_aftertone_repo "${SCRIPT_DIR}"; then
  mkdir -p "${SCRIPT_DIR}/state"
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") speak_summary: could not find Aftertone install (set AFTERTONE_INSTALL_DIR or run install.sh --global)" >>"${SCRIPT_DIR}/state/speak_summary-hook.log" || true
  exit 0
fi
export AFTERTONE_REPO="${REPO}"
export SUPERTONIC_REPO="${REPO}" # legacy alias for scripts / forks
PY="${REPO}/py"
PORT_FILE="${REPO}/.cursor/hooks/state/tts-daemon.port"
STATE_DIR="${REPO}/.cursor/hooks/state"
LOG="${STATE_DIR}/speak_summary-hook.log"
PREP_ERR="${STATE_DIR}/speak_summary-prepare.stderr.log"
mkdir -p "${STATE_DIR}"

export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:/opt/homebrew/bin:${PATH}"

log() {
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") $*" >>"${LOG}"
}

HOOK_STDIN="$(mktemp "${STATE_DIR}/hook_stdin.XXXXXX.json")"
cat >"${HOOK_STDIN}" || true
HOOK_BYTES="$(wc -c <"${HOOK_STDIN}" | tr -d ' \n\r')"
log "hook_invoked hook_json_bytes=${HOOK_BYTES}"

# Optional debug trace (off by default — each extra Python spawn costs seconds on Windows).
if [[ "${AFTERTONE_HOOK_TRACE:-}" == "1" ]]; then
  if VENV_PY="$(aftertone_venv_python "${PY}")"; then
    "${VENV_PY}" "${PY}/hook_stdin_normalize.py" "${HOOK_STDIN}" 2>/dev/null || true
    <"${HOOK_STDIN}" "${VENV_PY}" "${PY}/hook_payload_trace.py" "${STATE_DIR}/hook_payload_trace.jsonl" 2>/dev/null || true
  fi
fi

read_port() {
  local toml="${REPO}/.cursor/hooks/speak_summary.toml"
  local toml_port=""
  if [[ -f "${toml}" ]]; then
    toml_port="$(grep -E '^[[:space:]]*port[[:space:]]*=' "${toml}" | head -1 | sed -E 's/.*=[[:space:]]*//' | tr -d ' \"')"
  fi
  if [[ -f "${PORT_FILE}" ]]; then
    local file_port
    file_port="$(tr -d ' \n\r' <"${PORT_FILE}")"
    if [[ -n "${toml_port}" ]] && [[ -n "${file_port}" ]] && [[ "${toml_port}" != "${file_port}" ]] &&
      [[ "${toml_port}" =~ ^[0-9]+$ ]] && [[ "${file_port}" =~ ^[0-9]+$ ]]; then
      log "port_mismatch toml_port=${toml_port} state_file_port=${file_port} hint=restart_daemon"
    fi
    echo "${file_port}"
    return
  fi
  if [[ -n "${toml_port}" ]] && [[ "${toml_port}" =~ ^[0-9]+$ ]]; then
    echo "${toml_port}"
    return
  fi
  echo "8765"
}

ensure_daemon() {
  local port="$1"
  if curl -fsS -m 0.35 "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; then
    return 0
  fi
  log "daemon_bootstrap port=${port}"
  local vpy=""
  if vpy="$(aftertone_venv_python "${PY}")"; then
    "${vpy}" "${PY}/tts_daemon_ctl.py" start --repo-root "${REPO}" >>"${STATE_DIR}/tts-daemon-bootstrap.log" 2>&1 || true
  elif command -v uv >/dev/null 2>&1; then
    (cd "${PY}" && uv run python tts_daemon_ctl.py start --repo-root "${REPO}") >>"${STATE_DIR}/tts-daemon-bootstrap.log" 2>&1 || true
  else
    log "daemon_bootstrap_failed no_uv_no_venv"
  fi
  sleep 0.5
}

PORT="$(read_port)"
ensure_daemon "${PORT}"
PORT="$(read_port)"

PAYLOAD=""
: >"${PREP_ERR}"
export PYTHONPATH="${PY}${PYTHONPATH:+:${PYTHONPATH}}"
if vpy="$(aftertone_venv_python "${PY}")"; then
  PAYLOAD="$("${vpy}" -m aftertone.hook_run "${HOOK_STDIN}" 2>>"${PREP_ERR}" || true)"
elif command -v uv >/dev/null 2>&1; then
  PAYLOAD="$(cd "${PY}" && uv run python -m aftertone.hook_run "${HOOK_STDIN}" 2>>"${PREP_ERR}" || true)"
fi
# Fallback if hook_run failed (e.g. import error): legacy prepare + post.
if [[ "${PAYLOAD}" != "{"* ]] && vpy="$(aftertone_venv_python "${PY}")"; then
  PAYLOAD="$(<"${HOOK_STDIN}" "${vpy}" "${PY}/speak_summary_prepare.py" --post 2>>"${PREP_ERR}" || true)"
fi

PAYLOAD="$(echo "${PAYLOAD}" | tr -d '\n\r' | head -c 8000)"
if [[ "${PAYLOAD}" != "{"* ]]; then
  log "prepare_bad_output first_bytes=${PAYLOAD:0:120}"
  PAYLOAD='{}'
fi
if [[ "${PAYLOAD}" == "{}" ]] || [[ -z "${PAYLOAD}" ]]; then
  if [[ -s "${PREP_ERR}" ]]; then
    log "prepare_stderr_tail $(tail -c 400 "${PREP_ERR}" | tr '\n' ' ')"
  elif [[ "${HOOK_BYTES:-0}" -le 2 ]]; then
    log "prepare_skip empty_stdin (Cursor did not pass hook JSON?)"
  else
    cp "${HOOK_STDIN}" "${STATE_DIR}/last-hook-skipped.json" 2>/dev/null || true
    skip_detail=""
    if vpy="$(aftertone_venv_python "${PY}")"; then
      skip_detail="$("${vpy}" "${PY}/hook_skip_diag.py" "${HOOK_STDIN}" 2>/dev/null || true)"
    fi
    if [[ -n "${skip_detail}" ]]; then
      log "prepare_skip no_text ${skip_detail}"
    else
      log "prepare_skip no_text (check speak_summary.toml: enabled, summary_mode, quiet_hours)"
    fi
  fi
  rm -f "${HOOK_STDIN}"
  exit 0
fi

log "prepare_ok payload_chars=${#PAYLOAD}"
if grep -q '^hook_metrics ' "${PREP_ERR}" 2>/dev/null; then
  log "$(grep '^hook_metrics ' "${PREP_ERR}" | tail -1 | tr -d '\r')"
fi
if grep -qE '^hook_metrics .*http=(202|200)' "${PREP_ERR}" 2>/dev/null; then
  log "post_say_done port=${PORT} via=hook_run"
else
  log "post_say_failed port=${PORT}"
fi

rm -f "${HOOK_STDIN}"
exit 0
