#!/usr/bin/env bash
# Publish docs/demo.mp4 for GitHub README inline playback.
#
# GitHub strips <video> tags and raw.githubusercontent.com URLs in README.
# Inline players need a bare URL on its own line, usually:
#   https://user-images.githubusercontent.com/.../....mp4
# from drag-and-drop in the github.com README editor, OR:
#   https://github.com/omarelkhal/aftertone/releases/download/demo-asset/demo.mp4
# (release asset; may work depending on GitHub rendering).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f docs/demo.mp4 ]]; then
  echo "Missing docs/demo.mp4" >&2
  exit 1
fi

echo "Publishing demo-asset release..."
gh release delete demo-asset -y 2>/dev/null || true
gh release create demo-asset docs/demo.mp4 \
  --title "README demo video" \
  --notes "Binary for README inline playback on github.com (not a product release)."

RELEASE_URL="https://github.com/omarelkhal/aftertone/releases/download/demo-asset/demo.mp4"
echo ""
echo "Release URL (paste as its own line in README if needed):"
echo "$RELEASE_URL"
echo ""
echo "For the most reliable GitHub README player, open the web editor and drag-and-drop:"
echo "  gh browse README.md"
echo "Then replace the demo URL line with the user-images or user-attachments URL GitHub inserts."
echo "See: https://stackoverflow.com/questions/4279611/how-to-embed-a-video-into-github-readme-md"
