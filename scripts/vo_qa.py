#!/usr/bin/env python3
"""VO flow gate: the mechanical version of "does the narration flow".

    python3 vo_qa.py <placed_vo.(wav|mp3)> <film_seconds>

Run it on the PLACED voiceover track (the VO stem laid out on the film's
timeline, before the mix). It transcribes with whisper word timestamps, infers
blocks (runs of speech separated by silences over the block threshold), and
enforces the flow doctrine (genrupt-flow §5c-bis). Every rule below maps to a
failure a user actually heard:

  HOLE       — a silence over 0.9s INSIDE a block. This is the robotic pause
               (measured: 1.9s mid-phrase) that reads as "the VO was made
               before the edit".
  BLOCKS     — more than 4 placement blocks. Sentence-by-sentence sharding is
               how a continuous read turns choppy.
  DEAD AIR   — a gap between blocks over 5s. One musical breather is design;
               longer is a film that went silent.
  QUARTERS   — a quarter of the film with no spoken word. Narration that
               clusters at the start reads as abandoned.
  COVERAGE   — speech under 50% (thin) or over 85% (wall-to-wall cannot sync).
  TAIL       — the last word must land in the final quarter; a read that ends
               mid-film leaves a dead tail no music can carry.

Exit 1 with findings; a failing layout gets re-spaced or a re-paced read
(~USD 0.12), never shipped.
"""
import re
import subprocess
import sys

# Geometry comes from ENERGY (ffmpeg silencedetect), never from whisper:
# measured here, whisper smears word timestamps across silences and reported a
# track with a real 6.5s hole as "1 block, 100% coverage". Transcription tools
# read words; only the waveform reads silence.
HOLE_MAX = 0.9       # a pause above this is unnatural...
BLOCK_GAP = 2.0      # ...unless it reaches this: then it is a designed breather
BLOCKS_MAX = 4
DEAD_AIR_MAX = 5.0
COVERAGE_MIN, COVERAGE_MAX = 0.50, 0.85
SILENCE_DB = "-38dB"
SILENCE_MIN = 0.30   # ignore blips shorter than this


def speech_intervals(audio, film_dur):
    """[(start, end)] of speech, from silencedetect inverted."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(audio), "-af",
         f"silencedetect=n={SILENCE_DB}:d={SILENCE_MIN}", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", r.stderr)]
    # build speech spans between silences
    spans, cursor = [], 0.0
    for s0, s1 in zip(starts, ends + [film_dur]):
        if s0 - cursor > 0.05:
            spans.append((cursor, s0))
        cursor = s1
    if film_dur - cursor > 0.05 and (not starts or cursor > starts[-1] - 0.01):
        spans.append((cursor, film_dur))
    # an unended final silence means the track ends silent — spans already right
    return [(a, b) for a, b in spans if b - a > 0.15]


def main():
    audio, film_dur = sys.argv[1], float(sys.argv[2])
    spans = speech_intervals(audio, film_dur)
    if not spans:
        sys.exit("VO QA FAILED: no speech found in the placed track")

    # merge spans into blocks; gaps in (HOLE_MAX, BLOCK_GAP) are HOLES —
    # too long for a breath, too short to be a designed breather
    fails = []
    blocks = [[spans[0]]]
    for a, b in zip(spans, spans[1:]):
        gap = b[0] - a[1]
        if gap >= BLOCK_GAP:
            blocks.append([b])
        else:
            if gap > HOLE_MAX:
                fails.append(f"HOLE: {gap:.2f}s of silence at {a[1]:.2f}s — too long "
                             f"for a breath, too short to be a breather: the robotic "
                             f"pause. Re-pace the read")
            blocks[-1].append(b)

    if len(blocks) > BLOCKS_MAX:
        fails.append(f"BLOCKS: {len(blocks)} placement blocks (max {BLOCKS_MAX}) — "
                     f"sentence-sharding is how a read turns choppy; merge blocks")
    for a, b in zip(blocks, blocks[1:]):
        gap = b[0][0] - a[-1][1]
        if gap > DEAD_AIR_MAX:
            fails.append(f"DEAD AIR: {gap:.1f}s with no narration after {a[-1][1]:.1f}s "
                         f"(max {DEAD_AIR_MAX}s)")
    q = film_dur / 4
    for i in range(4):
        if not any(s0 < (i + 1) * q and s1 > i * q for s0, s1 in spans):
            fails.append(f"QUARTERS: no narration in quarter {i + 1} "
                         f"({i * q:.1f}-{(i + 1) * q:.1f}s)")
    cov = sum(b - a for a, b in spans) / film_dur
    if not COVERAGE_MIN <= cov <= COVERAGE_MAX:
        fails.append(f"COVERAGE: speech fills {cov:.0%} of the film "
                     f"(band {COVERAGE_MIN:.0%}-{COVERAGE_MAX:.0%})")
    if spans[-1][1] < film_dur * 0.75:
        fails.append(f"TAIL: narration ends at {spans[-1][1]:.1f}s of {film_dur:.1f}s — "
                     f"the close line must land in the final quarter")

    print(f"{len(spans)} speech spans, {len(blocks)} blocks, coverage {cov:.0%}, "
          f"ends {spans[-1][1]:.1f}s/{film_dur:.1f}s")
    if fails:
        for f in fails:
            print("FAIL", f)
        sys.exit(1)
    print("PASS — the read flows")


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(2)
    main()
