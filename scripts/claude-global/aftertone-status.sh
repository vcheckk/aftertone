#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=_aftertone_common.sh
source "$(dirname "$0")/_aftertone_common.sh"
_aftertone_require_install
_aftertone_uv status
