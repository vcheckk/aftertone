#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_aftertone_common.sh"
_aftertone_require_install
_aftertone_uv repair
echo "aftertone_repair: hooks and defaults refreshed; daemon restarted if needed."
