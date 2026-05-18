#!/usr/bin/env bash
# One-shot dev setup: Python venv (uv), Hugging Face assets if missing, web npm deps.
# Usage (from repo root):
#   bash scripts/bootstrap.sh
# Options:
#   SKIP_WEB=1       — do not run npm install in web/
#   SKIP_ASSETS=1    — do not download models (expects assets/onnx/ already)
#   FORCE_ASSETS=1   — re-download assets even if onnx/tts.json exists

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PY="${ROOT}/py"
WEB="${ROOT}/web"

echo "==> bootstrap: repo root ${ROOT}"

if ! command -v uv >/dev/null 2>&1; then
  echo "bootstrap: 'uv' not found. Install: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

if [[ -f "${PY}/.python-version" ]]; then
  PY_VER="$(tr -d ' \n\r' <"${PY}/.python-version")"
  echo "==> bootstrap: ensuring Python ${PY_VER} (onnxruntime wheels)…"
  (cd "${PY}" && uv python install "${PY_VER}")
  echo "==> bootstrap: uv sync (Python deps + venv under py/)"
  (cd "${PY}" && uv sync --python "${PY_VER}")
else
  echo "==> bootstrap: uv sync (Python deps + venv under py/)"
  (cd "${PY}" && uv sync)
fi

if [[ "${SKIP_ASSETS:-}" != "1" ]]; then
  EXTRA=()
  if [[ "${FORCE_ASSETS:-}" == "1" ]]; then
    EXTRA=(--force)
  fi
  if [[ ! -f "${ROOT}/assets/onnx/tts.json" ]] || [[ "${FORCE_ASSETS:-}" == "1" ]]; then
    echo "==> bootstrap: fetching ONNX assets from Hugging Face (Supertone/supertonic-3)…"
    (cd "${PY}" && uv run --with huggingface_hub python fetch_assets.py "${EXTRA[@]}")
  else
    echo "==> bootstrap: assets/onnx/tts.json present; skip download (set FORCE_ASSETS=1 to re-fetch)"
  fi
else
  echo "==> bootstrap: SKIP_ASSETS=1 — not downloading models"
fi

if [[ "${SKIP_WEB:-}" != "1" ]] && [[ -f "${WEB}/package.json" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo "==> bootstrap: npm install (web/)"
    (cd "${WEB}" && npm install)
  else
    echo "bootstrap: npm not found; skipping web/ (install Node.js or set SKIP_WEB=1)" >&2
  fi
elif [[ "${SKIP_WEB:-}" == "1" ]]; then
  echo "==> bootstrap: SKIP_WEB=1 — skipping npm in web/"
else
  echo "==> bootstrap: no web/package.json — skipping web"
fi

echo "==> bootstrap: done."
echo "    Python: cd py && uv run python example_onnx.py"
echo "    Web:    cd web && npm run dev"
echo "    TTS hook smoke: bash py/test_speak_summary_pipeline.sh"
