#!/usr/bin/env python3
"""Measured QA: the numbers, not opinions. Usage:

    python3 qa.py <video.mp4> <run_dir>            # full report
    python3 qa.py <video.mp4> <run_dir> --probe    # mood check only

Checks, all against the brief and shot plan:
- mean luminance + warmth (mean R minus mean B) per beat window, vs the brief's
  declared mood band; the close is weighted double and any close under ~25 lum
  is flagged hard
- MOTION per beat (mean absolute frame difference): a beat that measures
  near-static failed whatever the prompt said — the measured version of "it
  barely moves". The signature beat is held to a hard floor.
- true cut points via ffmpeg scene-detect, vs planned beat boundaries
- an end-state frame grab for every beat that declares one, clamped BEFORE the
  nearest detected cut (a grab after the cut photographs the next beat),
  written to <run_dir>/qa/ for the agent to LOOK at
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def frame_at(video, t, out_path):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(video),
                    "-frames:v", "1", str(out_path)], check=True)
    return out_path


def measure(img_path):
    a = np.asarray(Image.open(img_path).convert("RGB"), dtype=float)
    lum = (.2126 * a[:, :, 0] + .7152 * a[:, :, 1] + .0722 * a[:, :, 2]).mean()
    warmth = (a[:, :, 0] - a[:, :, 2]).mean()
    return round(lum, 1), round(warmth, 1)


def cut_points(video):
    r = subprocess.run(
        ["ffmpeg", "-i", str(video), "-vf", "select='gt(scene,0.25)',metadata=print",
         "-f", "null", "-"], capture_output=True, text=True)
    return [round(float(l.split("pts_time:")[1].split()[0]), 2)
            for l in r.stderr.splitlines() if "pts_time:" in l]


def motion_score(video, t0, t1, samples=5, gap=0.15):
    """INSTANTANEOUS motion: at each sample time, diff two frames `gap` apart.

    Long-gap differencing hides the failure this exists for — a slow drift
    accumulates plenty of pixel change over 0.8s while looking frozen to a
    viewer. Two frames 0.15s apart measure what the eye calls "moving NOW".
    Returns (mean, frozen_fraction): frozen = instantaneous diff under 1.2.
    The measured failure: a 5s bullet-time beat that read as "barely moves".
    """
    import tempfile
    diffs = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(samples):
            t = t0 + (t1 - t0 - gap) * i / max(samples - 1, 1)
            a = Path(td) / f"a{i}.jpg"
            b = Path(td) / f"b{i}.jpg"
            frame_at(video, t, a)
            frame_at(video, t + gap, b)
            fa = np.asarray(Image.open(a).convert("L"), dtype=float)
            fb = np.asarray(Image.open(b).convert("L"), dtype=float)
            diffs.append(np.abs(fb - fa).mean())
    frozen = sum(1 for d in diffs if d < 1.2) / len(diffs)
    return round(sum(diffs) / len(diffs), 2), round(frozen, 2)


def main():
    video = Path(sys.argv[1])
    run = Path(sys.argv[2])
    probe_only = "--probe" in sys.argv
    qa_dir = run / "qa"
    qa_dir.mkdir(exist_ok=True)
    brief = json.loads((run / "brief.json").read_text())
    # NEVER default silently. Measured: a brief carried its range under
    # 'target_luminance', the old [55,90] fallback measured a bright beach film
    # against the lamplit band, and QA reported a correct picture as broken.
    MOODS = {"BRIGHT_EVERYDAY": (90, 140), "WARM_LAMPLIT": (55, 90), "MOODY_NIGHT": (25, 55)}
    mood = brief.get("mood") or {}
    rng = mood.get("lum_range") or mood.get("target_luminance") or MOODS.get(mood.get("band"))
    if rng is None:
        print("QA REFUSED: brief.mood has no lum_range/target_luminance and no known "
              f"band ({mood.get('band')!r}). Declare the band; guessing a band judges "
              "the film against the wrong light.")
        sys.exit(2)
    lo, hi = rng
    findings = []

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())

    if probe_only:
        # one beat: sample three points, report against the band
        for i, t in enumerate([dur * .2, dur * .5, dur * .9]):
            f = frame_at(video, t, qa_dir / f"probe-{i}.jpg")
            lum, warm = measure(f)
            status = "OK" if lo * 0.8 <= lum <= hi * 1.3 else "OUT OF BAND"
            print(f"t={t:.1f}s lum={lum} warm={warm} band=[{lo},{hi}] {status}")
            if status != "OK":
                findings.append(f"probe t={t:.1f}: lum {lum} outside [{lo},{hi}]")
        sys.exit(1 if findings else 0)

    shots = json.loads((run / "shotplan.json").read_text())["shots"]
    print(f"duration: {dur:.2f}s  planned: {sum(s['seconds'] for s in shots)}s")

    cuts = cut_points(video)
    print("cuts:", cuts)

    # MEASURE THE BEATS WHERE THEY ACTUALLY ARE. This used to walk the PLANNED
    # seconds (0-4, 4-10, 10-14 …) while printing the detected cuts one line
    # above, so every number described the wrong seconds the moment the cut
    # moved. It always moves: stage 9's first free fix is a TRIM, and this
    # file's own advice is to take it. Measured (18.8): after a 1.17s trim the
    # planned windows reported the signature beat at motion 11.06 against a
    # median of 11.82 — "the wow shot is the film's sleepiest" — and the real
    # window, read off the detected cuts, measured 15.61 against a median of
    # 15.61. The tool was one free trim away from sending the run to pay for a
    # re-render of a beat that was already fine.
    bounds = None
    if len(cuts) == len(shots) - 1:
        bounds = [0.0] + list(cuts) + [dur]
    else:
        print(f"  note: {len(cuts)} cuts detected for {len(shots)} beats — falling "
              f"back to PLANNED windows; treat the per-beat numbers as approximate")

    signature_slot = ((brief.get("signature_shot") or {}).get("beat") or "hero")
    motions = {}
    clock = 0.0
    for i, s in enumerate(shots):
        if bounds:
            clock, end = bounds[i], bounds[i + 1]
        else:
            end = clock + s["seconds"]
        mid = frame_at(video, min(clock + (end - clock) / 2, dur - 0.1),
                       qa_dir / f"{s['id']}-mid.jpg")
        lum, warm = measure(mid)
        is_close = s.get("slot") == "close"
        band_lo, band_hi = (lo * 0.7, hi * 1.4) if not is_close else (max(25, lo * 0.7), hi * 1.4)
        flag = ""
        if not band_lo <= lum <= band_hi:
            flag = "  <-- OUT OF MOOD BAND" + (" (CLOSE, weighted double)" if is_close else "")
            findings.append(f"{s['id']}: lum {lum} outside [{band_lo:.0f},{band_hi:.0f}]{' CLOSE' if is_close else ''}")
        motion, frozen = motion_score(video, clock + 0.1, min(end - 0.1, dur - 0.1))
        # A freeze may hold ~1.5-2s of a beat (one sample of five); more than ~40%
        # frozen means the freeze ate the beat — the measured "barely moves".
        max_frozen = 0.4
        if frozen > max_frozen:
            flag += f"  <-- FROZEN {int(frozen * 100)}% of the beat"
            findings.append(f"{s['id']}: {int(frozen * 100)}% of the beat is frozen "
                            f"(instantaneous motion < 1.2) — the freeze ate the beat"
                            + (", and it is the SIGNATURE beat" if s.get("slot") == signature_slot else ""))
        motions[s.get("slot")] = motion
        print(f"{s['id']} [{clock:.0f}-{end:.0f}s] lum={lum} warm={warm} "
              f"motion={motion} frozen={int(frozen * 100)}%{flag}")
        if (s.get("end_state") or "").strip():
            # clamp the grab BEFORE the nearest detected cut: a grab after the cut
            # photographs the NEXT beat (measured on the first run)
            grab_t = end - 0.2
            near = [c for c in cuts if abs(c - end) < 0.6]
            if near:
                grab_t = min(grab_t, near[0] - 0.15)
            f = frame_at(video, max(clock + 0.1, min(grab_t, dur - 0.1)),
                         qa_dir / f"{s['id']}-endstate.jpg")
            print(f"  end-state frame -> {f.name}: \"{s['end_state'][:70]}\"")
        clock = end

    # The signature beat is the film's wow shot: it must be among the MOST dynamic
    # beats, not the sleepiest. Measured failure: a bullet-time hero at motion 6.9
    # against a film median of 9.5 read as "barely moves" and failed review, while
    # every absolute threshold missed it. Relative is the honest check.
    if signature_slot in motions and len(motions) >= 3:
        med = sorted(motions.values())[len(motions) // 2]
        sig = motions[signature_slot]
        if sig < med:
            findings.append(
                f"SIGNATURE beat motion {sig} is below the film's median {med} — the "
                "wow shot is the film's sleepiest shot. The freeze may hold at most "
                "~2s and the camera must sprint through it (taste.md motion floor)")
        elif med > 0 and (sig - med) / med < 0.10:
            # Measured: after a trim shifted the median, a signature beat passed at
            # EXACTLY the median — a coincidence that read as a verdict. Within a
            # few percent, the number proves nothing; the eye decides.
            print(f"  WARN: SIGNATURE motion {sig} is within "
                  f"{(sig - med) / med * 100:.0f}% of the median {med} — this pass is "
                  f"a coincidence, not a verdict. Watch the beat and judge by eye.")

    print(f"\n{len(findings)} hard findings")
    for x in findings:
        print(" ", x)
    sys.exit(1 if findings else 0)


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(2)
    main()
