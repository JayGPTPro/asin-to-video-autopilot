#!/usr/bin/env python3
"""Word timestamps for the placed voiceover, in the exact shape overlay_qa reads.

    python3 transcribe.py <placed_vo.wav> [out.json]     # default: words.json beside it

Why this ships instead of being improvised per run: the overlay VO-sync gate needs
one file, `words.json`, and every part of producing it was previously left to the
agent — finding the whisper model, calling whisper-cli with the right flags, and
converting its output. That worked on the machine where the model happened to sit
in the expected folder, and it produced a TypeError on the first attempt anywhere
else, because whisper-cli writes `{"transcription": [...]}` and overlay_qa reads
`{"words": [...]}`. Both facts now live in code.

Model resolution, in order: $WHISPER_MODEL, ~/.cache/whisper/ggml-base.en.bin,
./ggml-base.en.bin, and the Homebrew whisper-cpp share folder. If none exists the
script prints the one download line that fixes it and exits 2 — it never guesses.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MODEL_NAME = "ggml-base.en.bin"
MODEL_URL = ("https://huggingface.co/ggerganov/whisper.cpp/resolve/main/" + MODEL_NAME)


def find_model():
    candidates = []
    if os.environ.get("WHISPER_MODEL"):
        candidates.append(Path(os.environ["WHISPER_MODEL"]).expanduser())
    candidates += [
        Path.home() / ".cache" / "whisper" / MODEL_NAME,
        Path.cwd() / MODEL_NAME,
        Path("/opt/homebrew/share/whisper-cpp") / MODEL_NAME,
        Path("/usr/local/share/whisper-cpp") / MODEL_NAME,
        Path("/usr/share/whisper.cpp") / MODEL_NAME,
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(2)
    vo = Path(sys.argv[1])
    if not vo.is_file():
        print(f"no such audio file: {vo}")
        sys.exit(2)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else vo.with_name("words.json")

    if not shutil.which("whisper-cli"):
        print("whisper-cli is not installed.\n"
              "  macOS:    brew install whisper-cpp\n"
              "  Linux:    build whisper.cpp, or install the whisper-cpp package\n"
              "  Windows:  winget install ggerganov.whisper.cpp  (or use WSL)")
        sys.exit(2)

    model = find_model()
    if model is None:
        print(f"no {MODEL_NAME} found. Download it once:\n"
              f"  curl -L -o ~/.cache/whisper/{MODEL_NAME} --create-dirs {MODEL_URL}\n"
              f"or point $WHISPER_MODEL at a copy you already have.")
        sys.exit(2)

    # -ml 1 = one token per segment, which is what gives per-word times.
    stem = out.with_suffix("")
    r = subprocess.run(["whisper-cli", "-m", str(model), "-f", str(vo),
                        "-np", "-ml", "1", "-oj", "-of", str(stem)],
                       capture_output=True, text=True)
    raw = Path(str(stem) + ".json")
    if r.returncode != 0 or not raw.is_file():
        print("whisper-cli failed:\n" + (r.stderr or r.stdout)[-800:])
        sys.exit(1)

    segs = json.loads(raw.read_text()).get("transcription", [])
    words = []
    for s in segs:
        w = s.get("text", "").strip().strip(",.\"'?!")
        if not w:
            continue
        words.append({"word": w.lower(),
                      "start": s["offsets"]["from"] / 1000.0,
                      "end": s["offsets"]["to"] / 1000.0})
    # overlay_qa.py reads ["words"]; whisper writes ["transcription"]. This line is
    # the whole reason the script exists.
    out.write_text(json.dumps({"words": words}, indent=1))
    if raw != out:
        raw.unlink(missing_ok=True)

    spoken = " ".join(w["word"] for w in words)
    print(f"{len(words)} words -> {out}")
    print(f"first at {words[0]['start']:.2f}s, last at {words[-1]['start']:.2f}s")
    print(f"transcript: {spoken[:300]}")


if __name__ == "__main__":
    main()
