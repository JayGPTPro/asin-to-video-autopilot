#!/usr/bin/env python3
"""Build the final mix from MEASURED levels, and refuse to return a buried bed.

    mix_audio.py <picture.mp4> <vo.mp3> <music.mp3> <out.mp4>
                 [--under 6] [--ratio 2.5] [--sfx 1.0]

This script exists because the bed has been buried THREE times on real runs, and
twice it shipped. Every time the cause was the same shape: a guessed `volume=`
multiplier, a ratio-6 sidechain, and a verification that could not see the
failure. Prose rules did not stop it recurring, so the arithmetic and the check
now live in code and the build FAILS instead of shipping silent music.

Two things it does that a hand-written ffmpeg line does not:

1. **Derives the music gain from measurement.** It reads the mean volume of the
   VO and of the music (ffmpeg volumedetect) and solves for the gain that puts
   the bed `--under` dB below the voice. Measured failure it prevents: VO mean
   -19.6 dB, music mean -24.4 dB, and a hand-picked `volume=0.30` put the bed 15
   dB under instead of 9 — inaudible, and no single number in the finished mix
   revealed it.

2. **Verifies differentially.** It renders the same graph twice, once with the
   music muted, and compares per-half-second RMS. Only the DIFFERENCE between
   two renders can prove a bed is audible: the mix also contains the voice, so
   any absolute measurement of the mix towers over the SFX whether the music is
   there or not. That was the broken check that passed while the user heard no
   music at all.

Exit 1 if the mean music contribution is under MIN_CONTRIBUTION_DB.
"""
import argparse
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

# A shipped, user-approved mix measured +3.7 dB mean contribution; the buried one
# measured well under 1 dB. 2.0 sits between them with room on both sides.
MIN_CONTRIBUTION_DB = 2.0
# A near-continuous read (the norm: the script budget allows up to ~80% speech)
# turns a ratio-6 sidechain into a permanent mute. Gentle is the only setting
# that leaves a bed audible under a voice that never stops for long.
DEFAULT_RATIO = 2.5
# The doctrine's "8-10 dB under the voice" was written against a sparser read.
# Measured 17.8 with a read covering ~80% of the film: 9 dB under scored +2.0 dB
# contribution, sitting EXACTLY on the fail floor, while 6 dB under scored +3.7
# and was the mix the user accepted. Under a dense read, default to 6 and let the
# operator tighten it; the recurring failure here is burial, never loudness.
DEFAULT_UNDER_DB = 6.0


def mean_volume(path):
    """Mean volume in dBFS via ffmpeg volumedetect."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect",
                        "-f", "null", "/dev/null"], capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
    if not m:
        raise SystemExit(f"could not measure {path}")
    return float(m.group(1))


def build(picture, vo, music, out, music_gain, ratio, sfx_gain, vo_gain=1.45):
    graph = (
        f"[0:a]aformat=fltp:44100:stereo,volume={sfx_gain}[sfx];"
        f"[1:a]aformat=fltp:44100:stereo,volume={music_gain}[mus];"
        f"[2:a]aformat=fltp:44100:stereo,volume={vo_gain},apad[vo];"
        f"[vo]asplit=2[vomix][vokey];"
        f"[mus][vokey]sidechaincompress=threshold=0.14:ratio={ratio}:"
        f"attack=20:release=550:makeup=1[musd];"
        f"[sfx][musd][vomix]amix=inputs=3:duration=first:normalize=0[m];"
        f"[m]alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(picture), "-i", str(music),
                    "-i", str(vo), "-filter_complex", graph, "-map", "0:v", "-map", "[out]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
                   check=True)


def envelope(path, step=0.5):
    with tempfile.TemporaryDirectory() as td:
        w = Path(td) / "e.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path),
                        "-ar", "8000", "-ac", "1", str(w)], check=True)
        f = wave.open(str(w))
        a = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(float)
        f.close()
    k = int(8000 * step)
    return np.array([np.sqrt((a[i:i + k] ** 2).mean()) + 1e-9
                     for i in range(0, len(a) - k, k)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picture"); ap.add_argument("vo")
    ap.add_argument("music"); ap.add_argument("out")
    ap.add_argument("--under", type=float, default=DEFAULT_UNDER_DB,
                    help="dB the bed sits below the voice's mean (6 under a dense read)")
    ap.add_argument("--ratio", type=float, default=DEFAULT_RATIO)
    ap.add_argument("--sfx", type=float, default=1.0)
    a = ap.parse_args()

    vo_db, mus_db = mean_volume(a.vo), mean_volume(a.music)
    target = vo_db - a.under
    gain = 10 ** ((target - mus_db) / 20)
    print(f"measured: VO {vo_db:.1f} dB, music {mus_db:.1f} dB")
    print(f"target bed {target:.1f} dB ({a.under:.0f} dB under the voice) -> volume={gain:.3f}")

    build(a.picture, a.vo, a.music, a.out, gain, a.ratio, a.sfx)
    with tempfile.TemporaryDirectory() as td:
        muted = Path(td) / "muted.mp4"
        build(a.picture, a.vo, a.music, muted, 0.0001, a.ratio, a.sfx)
        w1, w0 = envelope(a.out), envelope(muted)
    n = min(len(w1), len(w0))
    delta = 20 * np.log10(w1[:n] / w0[:n])
    mean, peak = float(delta.mean()), float(delta.max())
    print(f"music contribution: mean {mean:+.1f} dB, peak {peak:+.1f} dB "
          f"(floor {MIN_CONTRIBUTION_DB:+.1f})")
    if mean < MIN_CONTRIBUTION_DB:
        print("FAIL: the bed is buried. Raise --under toward 6, or check that the "
              "music track itself has content (measure its own LUFS). Do NOT ship "
              "this: every absolute number in the mix will still look correct.")
        sys.exit(1)
    print("PASS: the bed is audible.")


if __name__ == "__main__":
    main()
