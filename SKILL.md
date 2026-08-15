---
name: asin-to-video-autopilot
description: >-
  Turn any Amazon ASIN into a finished 30-second listing video, fully on autopilot.
  One command in, a complete product film out: emotional hook, real use cases with
  people, one signature camera move, diegetic sound, music, voiceover, and animated
  text overlays. Zero questions during the run; a cost cap set once in config. Use
  when the user provides an ASIN or Amazon product URL and wants a product video,
  listing video, or video ad created end to end: "make a video for this ASIN",
  "asin to video", "product video autopilot", "listing video for B0...".
---

# asin-to-video-autopilot

One command, one finished listing video. You (the agent) make every creative decision
using the taste rules in `references/`; the user's only inputs are the ASIN and the
one-time config. The promise is AUTOPILOT: after the environment check passes and the
config exists, a run never stops to ask anything unless it would cross the cost cap.

## First run: environment + config

1. Run `setup/check-env.sh`. If anything is MISSING, print the fix lines it gives and
   stop. Never start a run in a broken environment.
2. If `config.json` does not exist next to this file's install location (or in the
   working directory), copy `setup/config.template.json` to `config.json`, show the
   user the cost cap (default USD 20 per run) and ask ONCE if they want to change it.
   This is the only money question this product ever asks.
3. Confirm the Genrupt MCP is connected: call `get_credit_balance_and_costs`. This
   also fetches LIVE pricing — never use hardcoded prices; Genrupt pricing moves.

## The money contract

- Total spend per run is bounded by `cost_cap_usd` in config.json.
- Report every paid action in one line as it happens: what, cost, running total.
- A typical run: probe ~USD 0.55, master 30s/720p ~USD 8-9, post audio ~USD 1-3.
  The headroom inside the cap funds at most ONE autonomous fix (retake or surgical
  edit) if QA fails hard. A second failure is written to the report with
  recommendations; it never spends more.
- If the next action would cross the cap: stop, state exactly what is left undone
  and what it would cost, and wait. This is the only mid-run stop that exists.

## Run stages

Stage-by-stage detail lives in `references/` (see the map below). The shape:

1. **Research** — scrape the ASIN through Genrupt (`scrape_video_reference_images_from_asin`
   + listing data). OPEN the product images and look; titles lie. Read reviews for
   emotional vs functional language.
2. **Taste decisions** — apply `references/taste.md`: emotion/features center of
   gravity, mood band with a target luminance range, the signature camera move, cast
   diversity plan, the final image. Log every decision + its reason for the report.
3. **Brief + shot plan** — the 7-beat listing template, **summing to 30 seconds**:
   hook 4s, hero 6s (the signature shot), four distinct use beats at 4s, close 4s.
   30 is the model's ceiling and the beats must USE it: an earlier template stopped at
   27s because it reserved 3s for a post-production CTA card this skill does not make,
   which quietly threw away three seconds of paid runtime. A close that rhymes with the
   hook, and end states on every fragile beat.
4. **Compose + lint** — `scripts/compose.py` + `scripts/lint.py`. The lint gate is
   hard: density, slow words, end states, reference roles with USE/DO-NOT-USE,
   design silence, character budget. Never hand-write the master prompt.
5. **References prep** — `scripts/prep_refs.py`: screen for real people, crop
   marketing text, pad to legal aspect ratio BEFORE upload (a failed download bills;
   a filter refusal is free).
6. **Probe** — 4s/480p of the signature shot with real references. QA the probe:
   product fidelity, luminance vs the declared mood band.
7. **Master** — 30s/720p via `generate_video`, diegetic sound only (no music, no
   voiceover in the generated pass).
8. **QA** — `scripts/qa.py`: true beat lengths, end-state audit per beat (grabs
   clamped before detected cuts), luminance/warmth with the close weighted double,
   count checks (Seedance cannot count), per-beat instantaneous MOTION with a
   frozen-fraction cap, and the relative signature check: the wow shot must not be
   the film's sleepiest shot. Plus the eye pass: glitter artifacts on hair and
   fabric, invented props, label fidelity.
9. **Autonomous fix** — if a hard failure and the cap allows: one retake (systemic)
   or one surgical edit (local). Attribution first: fix the owning layer.
10. **Post audio** — derived, auditioned, measured (`references/genrupt-flow.md`
    §5a-5e). The music brief is DERIVED from the film's register, cut rhythm and
    energy curve; 2-3 candidates are generated and PICKED by envelope-vs-cuts
    alignment; VO word timings are MEASURED with whisper and verified against
    their beats; the mix keeps SFX forward (they are the realism layer), music
    ducked under, VO on top. Never ship the only candidate unheard.
11. **Overlays** — HyperFrames, per `references/overlay-grammar.md`: the two-object
    system (type stack + gold-edged plate), Z-push entrances with the snap, tiers
    by importance, mirrored beats, measured dead space. A diet version (thin
    kickers, plain fades) failed review — the grammar is the floor. Super in/out
    times come from the MEASURED VO word timestamps. **Brand marks: real or
    absent** (taste.md §4b).
12. **THE AUDIO TASTE GATE.** Audio is the one layer meters cannot judge: every
    measured number can pass while the track sounds cheap, choppy or wrong for
    the picture (it happened; it failed review twice). So audio gets what
    graphics get: the autopilot builds its best mix AND 1-2 clearly different
    alternates (other music candidate, minimal-music, continuous vs re-paced VO),
    ships them beside the film, and the report presents them as a listening
    choice. Flow beats sync: never chop a continuous VO read into segments to
    chase beat alignment — shift the whole read or ask for a re-paced read; a
    choppy voice is worse than a half-beat drift.
13. **Conform + report** — 1280x720, 24fps, final mute-watch pass. Write the run
    report (`scripts/report.py`): every decision, measurement, and dollar.


## Reference map (complete)

| File | Owns |
|---|---|
| `references/taste.md` | Every creative decision rule, measured |
| `references/seedance25-rules.md` | Prompt grammar: end states, references, camera, density |
| `references/genrupt-flow.md` | Exact MCP calls, pricing, traps, audio doctrine, edit recipes |
| `references/overlay-grammar.md` | The text system: house register, choreography, dead space |
| `scripts/` | compose, lint, prep_refs, qa, report — all battle-tested |

Every stage above is runnable; the rules were paid for on real productions (two full
acceptance-grade runs, five review rounds). Do not improvise around a rule — the
measured rules ARE the product. When a rule and reality disagree, measure, fix the
rule, and leave the measurement in the file.
