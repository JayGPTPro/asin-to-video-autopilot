#!/usr/bin/env bash
# asin-to-video-autopilot environment check.
# Run once after install. Every requirement prints OK or MISSING with the fix.
# Exit code 0 = ready to run. Anything else = fix the MISSING lines first.

PASS=0
FAIL=0

ok()   { printf "  OK       %s\n" "$1"; PASS=$((PASS+1)); }
miss() { printf "  MISSING  %s\n           fix: %s\n" "$1" "$2"; FAIL=$((FAIL+1)); }
warn() { printf "  OPTIONAL %s\n           note: %s\n" "$1" "$2"; }

echo "asin-to-video-autopilot: environment check"
echo

# 1. ffmpeg — cuts, QA measurements, final conform
if command -v ffmpeg >/dev/null 2>&1; then
  ok "ffmpeg ($(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}'))"
else
  miss "ffmpeg" "macOS: brew install ffmpeg | Windows: winget install ffmpeg | Linux: apt install ffmpeg"
fi

# 2. python3 + PIL + numpy — reference prep and QA measurements
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import PIL, numpy" >/dev/null 2>&1; then
    ok "python3 with PIL + numpy ($(python3 -V 2>&1 | awk '{print $2}'))"
  else
    miss "python3 packages PIL + numpy" "python3 -m pip install pillow numpy"
  fi
else
  miss "python3" "macOS: brew install python3 | Windows: winget install Python.Python.3.12"
fi

# 3. Node 18+ with npx — HyperFrames text overlays (required)
if command -v node >/dev/null 2>&1; then
  NODE_MAJOR=$(node -e 'process.stdout.write(String(process.versions.node.split(".")[0]))' 2>/dev/null)
  if [ "${NODE_MAJOR:-0}" -ge 18 ] 2>/dev/null; then
    ok "node $(node -v) with npx"
  else
    miss "node 18 or newer (found $(node -v))" "install from nodejs.org or: brew install node"
  fi
else
  miss "node 18+ (for the animated text overlays)" "install from nodejs.org or: brew install node"
fi

# 4. whisper-cli + model — measured VO timing (the audio QA depends on it)
if command -v whisper-cli >/dev/null 2>&1; then
  if ls "$HOME"/.cache/whisper/ggml-base.en.bin >/dev/null 2>&1 || ls ./ggml-base.en.bin >/dev/null 2>&1 || [ -n "$WHISPER_MODEL" ]; then
    ok "whisper-cli with a base.en model"
  else
    miss "whisper model ggml-base.en.bin" "curl -L -o ~/.cache/whisper/ggml-base.en.bin --create-dirs https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin (then: export WHISPER_MODEL=~/.cache/whisper/ggml-base.en.bin)"
  fi
else
  miss "whisper-cli (voiceover timing QA)" "macOS: brew install whisper-cpp | then download the model: curl -L -o ~/.cache/whisper/ggml-base.en.bin --create-dirs https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
fi

# 5. Genrupt MCP — checked at run time from inside the agent, not from bash.
warn "Genrupt MCP connection + credits" "verified on every run via get_credit_balance_and_costs; connect Genrupt in your MCP settings before the first run"

# 6. Genrupt CLI — only needed if you feed LOCAL image/video files as references
if command -v genrupt >/dev/null 2>&1; then
  ok "genrupt CLI (local file uploads available)"
else
  warn "genrupt CLI not found" "only needed for local reference files; ASIN scraping works without it"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "READY: $PASS checks passed. Create config.json from setup/config.template.json and run your first ASIN."
  exit 0
else
  echo "NOT READY: $FAIL missing. Fix the lines above, then run this again."
  exit 1
fi
