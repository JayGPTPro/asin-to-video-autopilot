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

# THE ARITHMETIC, so nobody re-derives this wrong again. Adding a bed of level M
# under a foreground of level V raises the mix by 10*log10(1 + (M/V)^2):
#   bed 10 dB under the foreground -> +0.4 dB    bed 6 dB under -> +1.0 dB
#   bed  3 dB under                -> +1.8 dB    bed level with it -> +3.0 dB
# So a contribution floor of 2.0 dB, measured UNDER A VOICE, demands a bed louder
# than the voice. The old 2.0 only ever passed because it was averaged over the
# whole film, and the tail (where nothing competes, so the music IS the mix and
# scores +15 dB and up) carried it. Measured 18.8: a mix that averaged +3.2 dB
# scored +0.7 dB under the voice, and the user heard music only at the end.
# 1.0 dB = the bed sits about 6 dB under the foreground while the voice is
# talking, which is an assertive ad bed, not wallpaper.
MIN_CONTRIBUTION_DB = 1.0
# How much quieter the bed itself is allowed to be under the voice than in the
# gaps. This is the number that produces "the music only arrives at the end";
# the mix-level jump is not, because in a silent tail the music IS the mix.
MAX_DUCK_SWING_DB = 3.0
# A bed whose four quarters all sit at the same level is wallpaper by construction,
# and no mix setting rescues it. Measured 18.8: the bed the user called boring
# scored 0.7 dB between its loudest and quietest quarter; the three replacements
# briefed with a named structural event scored 7.9, 8.6 and 8.2.
MIN_TRACK_ARC_DB = 3.0
# A near-continuous read (the norm: the script budget allows up to ~80% speech)
# turns a ratio-6 sidechain into a permanent mute. Gentle is the only setting
# that leaves a bed audible under a voice that never stops for long.
DEFAULT_RATIO = 1.6
# The release has to fit the GAPS in the read, not the sound of one duck. Measured
# 18.8: a continuous VO whose longest internal gap was 0.47s, against release=550ms,
# never let the bed recover once — it sat 4.2 dB under for the whole 17s of speech
# and then jumped back to full the moment the read ended. The user's report was
# exactly that shape: "you barely hear the music, at the end you do". 220ms
# recovers inside a normal breath; with ratio 1.6 the same read costs 1.7 dB.
DEFAULT_RELEASE_MS = 220

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


def build(picture, vo, music, out, music_gain, ratio, sfx_gain, vo_gain=1.45,
          release=DEFAULT_RELEASE_MS):
    graph = (
        f"[0:a]aformat=fltp:44100:stereo,volume={sfx_gain}[sfx];"
        f"[1:a]aformat=fltp:44100:stereo,volume={music_gain}[mus];"
        f"[2:a]aformat=fltp:44100:stereo,volume={vo_gain},apad[vo];"
        f"[vo]asplit=2[vomix][vokey];"
        f"[mus][vokey]sidechaincompress=threshold=0.14:ratio={ratio}:"
        f"attack=20:release={release}:makeup=1[musd];"
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


def track_arc(path):
    """dB between the loudest and quietest quarter of the bed. Structure, measured."""
    e = envelope(path, step=0.25)
    q = [e[i * len(e) // 4:(i + 1) * len(e) // 4].mean() for i in range(4)]
    return 20 * np.log10(max(q) / min(q))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picture"); ap.add_argument("vo")
    ap.add_argument("music"); ap.add_argument("out")
    ap.add_argument("--under", type=float, default=DEFAULT_UNDER_DB,
                    help="dB the bed sits below the voice's mean (6 under a dense read)")
    ap.add_argument("--ratio", type=float, default=DEFAULT_RATIO)
    ap.add_argument("--sfx", type=float, default=1.0)
    ap.add_argument("--release", type=float, default=DEFAULT_RELEASE_MS,
                    help="sidechain release in ms; must be shorter than the read's gaps")
    a = ap.parse_args()

    arc = track_arc(a.music)
    print(f"bed structure: {arc:.1f} dB between its loudest and quietest quarter "
          f"(min {MIN_TRACK_ARC_DB:.1f})")
    if arc < MIN_TRACK_ARC_DB:
        print("WARN: this bed is flat. It will read as wallpaper at ANY level — "
              "re-brief it with one named structural event (a drop, a stop, a bloom) "
              "on a specific second, not just instruments and a mood.")

    vo_db, mus_db = mean_volume(a.vo), mean_volume(a.music)
    target = vo_db - a.under
    gain = 10 ** ((target - mus_db) / 20)
    print(f"measured: VO {vo_db:.1f} dB, music {mus_db:.1f} dB")
    print(f"target bed {target:.1f} dB ({a.under:.0f} dB under the voice) -> volume={gain:.3f}")

    build(a.picture, a.vo, a.music, a.out, gain, a.ratio, a.sfx, release=a.release)
    with tempfile.TemporaryDirectory() as td:
        muted = Path(td) / "muted.mp4"
        build(a.picture, a.vo, a.music, muted, 0.0001, a.ratio, a.sfx, release=a.release)
        # the bed ALONE, through the same duck, so its swing can be measured
        bed = Path(td) / "bed.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(a.music), "-i", str(a.vo),
             "-filter_complex",
             f"[0:a]aformat=fltp:44100:stereo,volume={gain}[mus];"
             f"[1:a]aformat=fltp:44100:stereo,volume=1.45,apad[vo];"
             f"[mus][vo]sidechaincompress=threshold=0.14:ratio={a.ratio}:attack=20:"
             f"release={a.release}:makeup=1[o]",
             "-map", "[o]", str(bed)], check=True)
        w1, w0 = envelope(a.out), envelope(muted)
        vo_env, bed_env = envelope(a.vo), envelope(bed)

    n = min(len(w1), len(w0), len(vo_env), len(bed_env))
    delta = 20 * np.log10(w1[:n] / w0[:n])
    speech = vo_env[:n] > vo_env[:n].max() * 0.08
    if not speech.any() or speech.all():
        speech = np.ones(n, dtype=bool)

    spoken = float(delta[speech].mean())
    swing = (20 * np.log10(bed_env[~speech].mean() / bed_env[speech].mean())
             if (~speech).any() else 0.0)
    print(f"music contribution under the voice: {spoken:+.1f} dB "
          f"(floor {MIN_CONTRIBUTION_DB:+.1f})")
    print(f"bed swing speech -> gaps: {swing:+.1f} dB (max {MAX_DUCK_SWING_DB:.1f})")
    if swing > MAX_DUCK_SWING_DB:
        print(f"WARN: the bed lifts {swing:.1f} dB the moment the read stops — that is "
              f"heard as music arriving only at the end. Shorten --release below the "
              f"read's shortest gap, or lower --ratio.")
    if spoken < MIN_CONTRIBUTION_DB:
        print("FAIL: the bed is buried under the voice. Lower --under, drop --ratio, "
              "trim --sfx (the diegetic kitchen sound is usually the real masker), or "
              "check that the music track itself has content. Do NOT ship this: every "
              "absolute number in the mix looks correct.")
        sys.exit(1)
    print("PASS: the bed is audible under the voice.")


if __name__ == "__main__":
    main()
