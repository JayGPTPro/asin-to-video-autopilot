#!/usr/bin/env bash
# Build the installable zip for asin-to-video-autopilot.
#
# Why this exists: the first two zips were built by hand, and on 18.8.2026 the live
# zip was a whole session behind the skill — it still shipped the occlude.py that let
# a hero super reach a customer as "ur, / a ill". A hand-built zip has no way to say
# which commit it is, so nobody can tell. This script refuses to build from a dirty
# tree and stamps the commit into VERSION, so "which build do you have" always has
# an answer.
#
# Usage:  bash build-zip.sh [DEST_DIR]
# Default DEST_DIR is the jaygptpro.com video-autopilot folder.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="asin-to-video-autopilot"
DEST="${1:-$HOME/Downloads/Claude/jaygptpro.com/video-autopilot}"

cd "$SRC"

# 1. The tree must be clean. A zip that does not correspond to a commit is a zip
#    nobody can reproduce or roll back to.
if [ -n "$(git status --porcelain)" ]; then
  echo "REFUSED: uncommitted changes. Commit them first, so the zip has a sha."
  git status --short
  exit 1
fi

SHA="$(git rev-parse --short HEAD)"
STAMP="$(date -u +%Y-%m-%dT%H:%MZ)"

# 2. Stage a clean copy. Building from the working folder would sweep in the
#    operator's own config.json, runs and rendered films.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/$NAME"

git archive HEAD | tar -x -C "$STAGE/$NAME"

# The buyer gets the skill, not the machinery that publishes it.
rm -f "$STAGE/$NAME/build-zip.sh" "$STAGE/$NAME/.gitignore"

printf '%s\ncommit %s\nbuilt %s\n' "$NAME" "$SHA" "$STAMP" > "$STAGE/$NAME/VERSION"

# 3. Zip it.
mkdir -p "$DEST"
OUT="$DEST/$NAME.zip"
rm -f "$OUT"
( cd "$STAGE" && zip -qr "$OUT" "$NAME" -x '*.DS_Store' '*__pycache__*' )

echo "built  $OUT"
echo "commit $SHA"
echo "files  $(unzip -l "$OUT" | tail -1 | awk '{print $2}')"
echo "sha256 $(shasum -a 256 "$OUT" | awk '{print $1}')"
echo
echo "Verify what is LIVE after deploying:"
echo "  curl -s https://jaygptpro.com/video-autopilot/$NAME.zip | shasum -a 256"
echo "  (must match the sha256 above, and the VERSION inside must read commit $SHA)"
