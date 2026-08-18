#!/usr/bin/env python3
"""Where can type actually live, and how big can it be?

    deadspace.py <film.mp4> --from T0 --to T1 [--lines "A pour,|not a pill"]
                 [--tracking 6] [--samples 12]

Answers the question the overlay grammar's law 2 asks and that nobody could
answer without guessing: across a super's WHOLE window, which rectangle stays
free of every subject, product and hand — and what is the largest type size
that fits inside it.

Why this exists (measured on a liquid-supplement film): the theme asked for a 150px hero
and the film's roomiest window held 430x370px of clean background. Nobody
measured, so the super was placed on top of the subject and then "rescued" with
occlusion, which hid 63% of its glyphs and shipped the line as "ur, / a ill".
Both failures were the same missing number.

Busy = a hard edge in ANY sampled frame, or a pixel that changes a lot across
them. Defocused background that drifts gently is NOT busy: it is exactly where
type belongs. The output rectangle is the honest answer for the whole window,
not for one lucky frame.
"""
import argparse
import subprocess
import sys

import numpy as np

W, H = 1280, 720
SW, SH = 256, 144           # analysis scale
# Outfit-ish advance width as a fraction of font-size, measured off the theme's
# rendered supers. Good to a few percent, which is all a fit check needs.
CHAR_W = 0.49


def frames(video, t0, t1, n):
    out = []
    for t in np.linspace(t0, t1, n):
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
             "-frames:v", "1", "-vf", f"scale={SW}:{SH}", "-f", "rawvideo",
             "-pix_fmt", "gray", "-"], capture_output=True)
        if len(r.stdout) < SW * SH:
            continue
        out.append(np.frombuffer(r.stdout, dtype=np.uint8)[:SW * SH]
                   .reshape(SH, SW).astype(float))
    if not out:
        sys.exit("no frames could be read from that window")
    return np.stack(out)


# Calibrated on a real film against regions known to be good and known to be
# busy (a liquid-supplement film, the pour beat):
#   clean defocused background where type shipped fine:  grad p90 18, p99 29
#   the glass and the falling stream:                    grad p90 62
#   her torso and face:                                  grad p90 39
# So a hard edge starts around 32. Temporal variance barely separates anything
# here (27 clean vs 33 on a torso) because the CAMERA moves in every shot, so it
# only catches fast subjects and sits high. Defocused background that drifts is
# not busy — that is the whole point of the law.
GRAD_T, VAR_T, FRAC = 32.0, 45.0, 0.25


def busy_mask(st):
    hits = np.zeros((SH, SW), float)
    for f in st:
        gy, gx = np.gradient(f)
        hits += (np.hypot(gx, gy) > GRAD_T)
    # busy = a hard edge in a meaningful share of frames, not in one noisy frame
    return (hits >= FRAC * len(st)) | (st.std(axis=0) > VAR_T)


def largest_rect(mask):
    """Largest all-clear axis-aligned rectangle (classic histogram scan)."""
    best, heights = (0, None), [0] * SW
    for r in range(SH):
        for c in range(SW):
            heights[c] = 0 if mask[r, c] else heights[c] + 1
        stack = []
        for c in range(SW + 1):
            cur = heights[c] if c < SW else 0
            start = c
            while stack and stack[-1][1] > cur:
                s, h = stack.pop()
                area = h * (c - s)
                if area > best[0]:
                    best = (area, (s, r - h + 1, c, r + 1))
                start = s
            stack.append((start, cur))
    return best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("film")
    ap.add_argument("--from", dest="t0", type=float, required=True)
    ap.add_argument("--to", dest="t1", type=float, required=True)
    ap.add_argument("--lines", default="", help="the super's lines, pipe-separated")
    ap.add_argument("--tracking", type=float, default=6.0)
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--line-height", type=float, default=1.12)
    a = ap.parse_args()

    st = frames(a.film, a.t0, a.t1, a.samples)
    box = largest_rect(busy_mask(st))
    if box is None:
        sys.exit("no clean rectangle at all in that window — this beat cannot host type")
    sx, sy = W / SW, H / SH
    x1, y1, x2, y2 = int(box[0] * sx), int(box[1] * sy), int(box[2] * sx), int(box[3] * sy)
    bw, bh = x2 - x1, y2 - y1
    print(f"window {a.t0:.2f}-{a.t1:.2f}s over {len(st)} frames")
    print(f"largest clean rect: x{x1}-{x2}  y{y1}-{y2}   {bw} x {bh} px")
    print(f"suggested placement: left:{x1 + 8}px; top:{y1 + 8}px;")

    if a.lines:
        lines = [l for l in a.lines.split("|") if l]
        longest = max(len(l) for l in lines)
        # width  = chars * size * CHAR_W + tracking * (chars - 1)
        by_w = (bw - 16 - a.tracking * (longest - 1)) / (longest * CHAR_W)
        by_h = (bh - 16) / (len(lines) * a.line_height)
        fit = int(min(by_w, by_h))
        print(f"longest line {longest} chars over {len(lines)} line(s)")
        print(f"largest size that FITS this rect: {fit}px "
              f"(width-limited {int(by_w)}px, height-limited {int(by_h)}px)")
        if fit < 50:
            print("REFUSE: under Amazon's 50pt/720p floor. Shorten the line, split it "
                  "across more lines, or move the super to a beat with more room.")
            sys.exit(1)
        for tier in (150, 96, 90, 72, 58, 50):
            if tier <= fit:
                print(f"-> set the hero tier to {tier}px for this film "
                      "(hierarchy is size alone; a tight film gets a smaller hero)")
                break


if __name__ == "__main__":
    main()
