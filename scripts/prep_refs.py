#!/usr/bin/env python3
"""Reference prep: crop marketing text and people OUT, pad ratios to legal.

Spec-driven so the agent decides the crops after LOOKING at every image:

    python3 prep_refs.py <spec.json>

spec.json:
{
  "out_dir": "plates",
  "plates": [
    {"src": "refs/a.jpg", "out": "plate-bottle.jpg", "crop": [x1, y1, x2, y2]}
  ]
}

Every output is padded onto a canvas to sit inside aspect ratio [0.5, 2.0] —
the provider rejects the DOWNLOAD outside [0.4, 2.5] and a failed download
BILLS credits, so the safety margin is deliberate. Pad color samples the
crop's corner pixel.
"""

import json
import sys
from pathlib import Path

from PIL import Image

RATIO_MIN, RATIO_MAX = 0.5, 2.0
# Measured 17.8: a 290x290 plate failed the render with "expected the width to be
# at least 300px". The provider rejects at DOWNLOAD time, i.e. after the job is
# priced — the same class of failure the ratio guard exists to prevent. 320 gives
# margin over the observed 300 floor.
MIN_DIM = 320


def upscale_to_min(img):
    w, h = img.size
    if min(w, h) >= MIN_DIM:
        return img
    k = MIN_DIM / min(w, h)
    return img.resize((round(w * k), round(h * k)), Image.LANCZOS)


def pad_to_legal(img):
    w, h = img.size
    ratio = w / h
    if RATIO_MIN <= ratio <= RATIO_MAX:
        return img
    bg = img.getpixel((2, 2))
    if ratio < RATIO_MIN:            # too tall -> widen
        new_w = int(h * RATIO_MIN) + 2
        canvas = Image.new("RGB", (new_w, h), bg)
        canvas.paste(img, ((new_w - w) // 2, 0))
    else:                            # too wide -> heighten
        new_h = int(w / RATIO_MAX) + 2
        canvas = Image.new("RGB", (w, new_h), bg)
        canvas.paste(img, (0, (new_h - h) // 2))
    return canvas


def main(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    base = Path(spec_path).parent
    out_dir = base / spec.get("out_dir", "plates")
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in spec["plates"]:
        img = Image.open(base / p["src"]).convert("RGB")
        if p.get("crop"):
            img = img.crop(tuple(p["crop"]))
        img = pad_to_legal(img)
        img = upscale_to_min(img)
        out = out_dir / p["out"]
        img.save(out, quality=92)
        w, h = img.size
        print(f"{out.name}: {w}x{h} ratio {w / h:.2f}"
              + ("  (upscaled to clear the 300px floor)" if min(w, h) == MIN_DIM else ""))


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(1)
    main(sys.argv[1])
