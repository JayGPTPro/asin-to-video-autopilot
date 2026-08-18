#!/usr/bin/env bash
# asin-to-video-autopilot: the free rehearsal.
#
# Runs the entire unpaid half of the pipeline against the worked example that ships
# with the skill. Nothing here touches Genrupt and nothing here costs a cent. If this
# passes, your machine can do everything the pipeline asks of it, and the only thing
# left to prove on your first real run is the Genrupt connection.
#
# Do this BEFORE your first paid run. A toolchain that breaks at minute forty of a
# paid run costs money; the same break here costs two minutes.
#
# Usage:  bash setup/rehearse.sh

set -uo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
step() { printf "\n[%s] %s\n" "$1" "$2"; }
ok()   { printf "  OK       %s\n" "$1"; }
bad()  { printf "  FAILED   %s\n" "$1"; FAIL=$((FAIL+1)); }
note() { printf "           %s\n" "$1"; }

echo "asin-to-video-autopilot: free rehearsal (no credits are spent)"

# ── 1. The environment ───────────────────────────────────────────────────────
step 1/4 "Environment"
if bash "$SRC/setup/check-env.sh" >/tmp/atv-env.txt 2>&1; then
  ok "every requirement present"
else
  bad "environment incomplete"
  sed 's/^/           /' /tmp/atv-env.txt
fi

# ── 2. The compiler, against a known-good answer ─────────────────────────────
# The example ships with the compile result it is supposed to produce. If your
# python produces a different one, the difference is your machine, not the brief.
step 2/4 "Compiler (examples/dry-run)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp "$SRC/examples/dry-run/brief.json" "$SRC/examples/dry-run/shotplan.json" "$WORK/"

if python3 "$SRC/scripts/compose.py" "$WORK" >/tmp/atv-compose.txt 2>&1; then
  EXPECT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prompt_chars'])" \
             "$SRC/examples/dry-run/compile-result.json" 2>/dev/null)
  GOT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prompt_chars'])" \
          "$WORK/compile-result.json" 2>/dev/null)
  if [ -n "$GOT" ] && [ "$GOT" = "$EXPECT" ]; then
    ok "master prompt rebuilt byte-identical ($GOT chars)"
  else
    bad "compiler produced ${GOT:-nothing} chars, the example says $EXPECT"
    note "the shipped example is the reference; a mismatch is a local problem"
  fi
else
  bad "compose.py did not run"
  sed 's/^/           /' /tmp/atv-compose.txt
fi

# ── 3. The gate that stands between a brief and your money ───────────────────
step 3/4 "Lint gate"
if python3 "$SRC/scripts/lint.py" "$WORK" >/tmp/atv-lint.txt 2>&1; then
  ok "the worked example passes its own gate"
else
  bad "lint rejected the shipped example"
  sed 's/^/           /' /tmp/atv-lint.txt
fi

# ── 4. The overlay renderer ──────────────────────────────────────────────────
# The most common local break, and the one that hurts most: it surfaces late, after
# the film is already paid for. npx fetches HyperFrames the first time, so this step
# is slow once and instant after.
step 4/4 "Overlay renderer (npx hyperframes)"
if command -v npx >/dev/null 2>&1; then
  if npx --yes hyperframes --version >/tmp/atv-hf.txt 2>&1; then
    ok "hyperframes reachable ($(head -1 /tmp/atv-hf.txt | tr -d '\r'))"
  else
    bad "npx could not fetch hyperframes"
    note "check your network, then: npx --yes hyperframes --version"
    sed 's/^/           /' /tmp/atv-hf.txt | head -5
  fi
else
  bad "npx not found"
  note "install Node 18+ from nodejs.org, or: brew install node"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  cat <<'DONE'
REHEARSAL PASSED. Your machine can run the whole pipeline.

One thing is still unproven, because only a real run can prove it: the Genrupt
connection and your credit balance. Your first run checks that before it spends
anything, and stops rather than crossing the cap you set.

Next:  /asin-to-video-autopilot B0XXXXXXXXX
DONE
  exit 0
else
  echo "REHEARSAL FAILED: $FAIL step(s) above. Fix them before spending anything."
  exit 1
fi
