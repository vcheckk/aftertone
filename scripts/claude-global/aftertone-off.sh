#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_aftertone_common.sh"
_aftertone_require_install
_aftertone_uv off
echo "aftertone_off: spoken TTS is off. Run /aftertone_on to enable again."
