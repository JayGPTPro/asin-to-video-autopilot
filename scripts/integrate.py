#!/usr/bin/env python3
"""Integration pass: make the type belong to the plate.

Two commands:

  integrate.py measure <film.mp4>
      Prints the plate's numbers, once per shot/film (never per frame):
        ink_cap   — 99.5th-percentile luma. Type must never be brighter than
                    the plate's own brightest highlight (measured: pure #FFF
                    was 55% brighter than the plate and read as a sticker).
        grain     — noise sigma from the flattest decile of a high-passed
                    frame, scaled by 0.85 (the estimator reads ~20% high on
                    textured plates).
      Feed ink_cap into the overlay's ink colors BEFORE rendering.

  integrate.py grain <composite.mp4> <out.mp4> --sigma N [--seed 42]
      Applies matched temporal grain AFTER the composite, over everything —
      grain on the film but not the type is the loudest amateur tell, and the
      type must not stay suspiciously clean.

The sub-pixel soften (real lenses never resolve a perfect edge) lives in the
overlay CSS, not here: the template puts filter: blur(0.3px) on supers.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def sample_frames(video, n=6):
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())
    frames = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = dur * (i + 0.5) / n
            fp = Path(td) / f"f{i}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}",
                            "-i", str(video), "-frames:v", "1", str(fp)], check=True)
            frames.append(np.asarray(Image.open(fp).convert("RGB"), dtype=float))
    return frames


def measure(video):
    frames = sample_frames(video)
    lumas = [(.2126 * f[:, :, 0] + .7152 * f[:, :, 1] + .0722 * f[:, :, 2])
             for f in frames]
    ink_cap = float(np.median([np.percentile(l, 99.5) for l in lumas]))

    sigmas = []
    for l in lumas:
        # high-pass: pixel minus 3x3 box mean, measured in the flattest decile
        k = np.ones((3, 3)) / 9.0
        pad = np.pad(l, 1, mode="edge")
        box = sum(pad[y:y + l.shape[0], x:x + l.shape[1]] * k[y, x]
                  for y in range(3) for x in range(3))
        hp = l - box
        # flatness proxy: local variance of the box mean, take the lowest decile
        flat = np.abs(box - np.median(box)) < np.percentile(np.abs(box - np.median(box)), 10)
        if flat.sum() > 500:
            sigmas.append(hp[flat].std())
    grain = round(float(np.median(sigmas)) * 0.85, 1) if sigmas else 4.0

    cap_hex = "#{0:02X}{0:02X}{0:02X}".format(int(round(ink_cap)))
    print(f"ink_cap_luma={ink_cap:.1f}")
    print(f"ink_cap_hex={cap_hex}")
    print(f"grain_sigma={grain}")
    print(f"note=scale your theme's ink_light so its luma <= {ink_cap:.0f}; "
          f"apply grain with: integrate.py grain <in> <out> --sigma {grain}")


def apply_grain(src, out, sigma, seed):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-vf", f"noise=alls={sigma}:allf=t+u:all_seed={seed}",
         "-c:v", "libx264", "-crf", "17", "-c:a", "copy", str(out)], check=True)
    print(f"grain sigma={sigma} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure"); m.add_argument("film")
    g = sub.add_parser("grain")
    g.add_argument("src"); g.add_argument("out")
    g.add_argument("--sigma", type=float, required=True)
    g.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    if a.cmd == "measure":
        measure(a.film)
    else:
        apply_grain(a.src, a.out, a.sigma, a.seed)


if __name__ == "__main__":
    main()
