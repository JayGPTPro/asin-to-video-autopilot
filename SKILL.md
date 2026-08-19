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
The one exception a user can switch on: `review_brief: true` in config.json stops the
run ONCE, after the brief and shot plan are written and before any credit moves, and
waits for a yes. Default false. It is the only gate that does not break the promise,
because it is free and it happens before the money.

## First run: environment + config

1. Run `bash setup/check-env.sh`. If anything is MISSING, print the fix lines it gives and
   stop. Never start a run in a broken environment.
2. If `config.json` does not exist next to this file's install location (or in the
   working directory), copy `setup/config.template.json` to `config.json`, show the
   user the cost cap (default USD 20 per run) and ask ONCE if they want to change it.
   This is the only money question this product ever asks.
3. Confirm the Genrupt MCP is connected: call `get_credit_balance_and_costs` for
   the BALANCE. Do not price renders from its presets — they cannot quote
   Seedance 2.5 (measured: silently resolved to fast-model keys and clamped to
   15s). Plan from the measured constants in `references/genrupt-flow.md` §0;
   the authoritative price of every render is the `costPreview` in its own
   `generate_video` response, and that is the number you log.

## How long a run takes, and what this skill does NOT do

Measured on real runs, 19.8: **about 40 minutes**, and the render queue is the small
part of it (probe ~4 min, master ~8 min). The rest is this agent reading the listing,
writing the brief, building the text layer and QA'ing. Tell the user the number up
front, then work without narrating.

**There is ONE pipeline. No fast mode, no toggles, no "lite" run.** Everyone gets the
same film, and the animated text layer is always part of it — it is the thing people
notice first, so it is never the thing that gets cut.

What was cut permanently to get here, because it cost minutes and changed the film
less than the type does:
- **The occlusion moment.** The subject passing in front of a super cost ~5 minutes,
  needed a segmentation engine that is not in every environment, and once hid 63% of a
  hero line. A super placed in measured dead space does not need rescuing.
- **The style card.** A 6-second card nobody watches, ~2 minutes.
- **Research beyond the listing page.** The title, the bullets and the gallery are the
  product's own words. Wider browsing added ~5 minutes and rarely changed the argument.
- **Three delivered mixes.** One FINAL and ONE alternate, not three.
- **At most 3 supers**, not 4-5. The hook, the differentiator, one fact.

What stays, and why, so nobody re-cuts it for speed:
- **The probe.** ~6 minutes of insurance on a ~USD 9 master. It fired on both recent
  runs (a mood band 20 points low; a hero interior rendering as an abstract blur).
  Cutting it does not save 6 minutes, it risks a re-render that costs 16 and USD 9.
- **Every QA gate.** They are seconds each and each one caught something real.
- **Audio candidates**, because they are now fired as ONE parallel batch
  (genrupt-flow 5a-quater): three directions cost the same wall clock as one.

## The money contract

- Total spend per run is bounded by `cost_cap_usd` in config.json.
- Report every paid action in one line as it happens: what, cost, running total.
- **BEFORE every paid action, check headroom against its WORST CASE cost, not its
  hoped-for cost.** If `running_total + worst_case > cap`, stop and ask. This is the
  only mid-run stop that exists.
- **Nothing else is ever a question for the user.** Measured 19.8: a run compiled at
  7,518 characters against the 7,500 ceiling, asked the user for permission to delete
  eighteen characters, and then sat idle for **54 minutes** — longer than all of its
  real work put together. A tool that refuses now prints the cheapest fixes with their
  character counts; apply them and carry on. If a decision is genuinely yours to make,
  make it, log it in the report, and keep moving.
- Typical run: probe ~USD 0.65, master 30s ~USD 9.80, audio ~USD 1 for a few
  candidates, so about USD 11-12 all in, leaving
  headroom for at most ONE autonomous fix. A second failure is written to the report
  with recommendations; it never spends more.

### How to count what you spent (the trap that fakes an overrun)

**NEVER compute spend by subtracting credit balances.** Measured, and it produced a
false alarm: one run reported USD 27.06 against a USD 15 cap and declared itself 80%
over. Its project actually contained exactly two renders — a probe and a master — and
the true spend was about USD 9.36. The phantom USD 17.70 was other sessions on the
same account moving the balance inside that run's window. A user seeing that report
would think the tool robbed them.

The rule:

1. **Running total = the SUM OF COST PREVIEWS you were quoted**, one line per paid
   action, plus audio at the constant below. Balance is a sanity check, never the
   source of truth.
2. **A balance delta is only evidence when you have confirmed nothing else is
   running** on the account. Otherwise it is noise, in both directions: it can invent
   spending you did not do, and it can hide a job that did not run.
3. **Audio is cheap: ~2 credits (~USD 0.12) per 30s track** (measured live).
   Count the tracks you fire and add them to the running total. Because it is
   this cheap, generating 2-3 music candidates and 2 VO takes IN ONE PARALLEL BATCH
   (genrupt-flow 5a-quater, same wall clock as one) to pick the best
   is the right call — the taste gate stays.
4. A content-filter refusal on audio costs nothing, same as on video.

## Run stages

Stage-by-stage detail lives in `references/` (see the map below). The shape:

1. **Research — the listing page ONLY, one pass.** Scrape the ASIN through Genrupt
   (`scrape_video_reference_images_from_asin` + listing data). OPEN the product images
   and look; titles lie. Read the reviews that come back with the listing for emotional
   vs functional language. **Do not browse further**: no competitor pages, no brand
   site, no search. Measured 19.8: wider browsing cost ~5 minutes a run and never
   changed the film's argument, which comes from the seller's own title, bullets,
   gallery and reviews. **Write `listing.json` into the run** (title,
   bullets, description, image URLs): the lint checks the brief against the seller's
   own words, and cannot if the run does not keep them. Then answer **taste.md §0**
   before anything else — occasion, symbols, provenance, packaging. An outside
   reviewer's four notes on a sympathy figurine were all the same miss: attributes
   read, intent ignored.
2. **Taste decisions** — apply `references/taste.md`: emotion/features center of
   gravity, mood band with a target luminance range, the signature camera move, cast
   diversity plan, the final image. Log every decision + its reason for the report.
3. **Brief + shot plan** — the 7-beat listing template, **summing to 30 seconds** with
   a rhythm that VARIES: hook 4s, hero 6s (the signature shot), then 3 / 2 / 5 / 4, close
   6s. The old template was 4/6/4/4/4/4/4 and it shipped a film a viewer called boring
   before anything else about it: seven shots of one length is a slideshow, and the music
   brief, which reads the cut rhythm, then wrote itself a 60 BPM bed to match. taste.md
   7a states the law and the lint enforces it (at most two shots of a length, one accent
   of 2-3s, one held beat of 5s+, longest/shortest ≥ 2.0). 30 is the model's ceiling and
   the beats must USE it: an earlier template stopped at 27s because it reserved 3s for a
   post-production CTA card this skill does not make, which quietly threw away three
   seconds of paid runtime. A close that rhymes with the hook, and end states on every
   fragile beat.
4. **Compose + lint** — `scripts/compose.py` + `scripts/lint.py`. The lint gate is
   hard: density, slow words, end states, reference roles with USE/DO-NOT-USE,
   design silence, character budget. Never hand-write the master prompt.
5. **References prep** — `scripts/prep_refs.py`: screen for real people, crop
   marketing text, pad to legal aspect ratio BEFORE upload (a failed download bills;
   a filter refusal is free).
6. **Probe** — 4s/480p of the signature shot with
   real references. QA the probe:
   product fidelity, luminance vs the declared mood band. **Every probe finding must
   become a change in the master prompt before the master runs, not a note.** Measured:
   a probe predicted the product losing its surface texture in close foreground, the
   master ran unchanged, and the finished film lost it exactly there. A film-wide
   guard does not protect one beat: write the fix INTO the beat that showed it.
7. **Master** — 30s/720p via `generate_video`, diegetic sound only (no music, no
   voiceover in the generated pass).
8. **QA** — `scripts/qa.py`: true beat lengths, end-state audit per beat (grabs
   clamped before detected cuts), luminance/warmth with the close weighted double,
   count checks (Seedance cannot count), per-beat instantaneous MOTION with a
   frozen-fraction cap, and the relative signature check: the wow shot must not be
   the film's sleepiest shot. Plus the eye pass: glitter artifacts on hair and
   fabric, invented props, label fidelity.
9. **Autonomous fix — by SEVERITY CLASS, not by count.** Measured failure: a run
   spent its single fix on a dark hero and shipped with a SECOND product visible in
   frame and a third-party branded can beside it. Three classes are NEVER shippable
   and outrank everything, in this order:
   1. **A second copy of the product, or a competitor/third-party brand, in frame.**
      A seller cannot use that video at all.
   2. **Generated text or a fake logo in frame.**
   3. **A beat that is unwatchable** (near-black, frozen, or the wow shot dead).
   Try the FREE repairs first and they often suffice: trim the offending seconds at
   scene-detect boundaries, reframe with a crop, or cover the corner with an overlay.
   Only then spend. Whatever is left unfixed goes in the report by class, so the
   person knows what they are looking at.
10. **Post audio** — derived, auditioned, measured (`references/genrupt-flow.md`
    §5a-5e). **The VO read is FINALIZED after the locked cut** (the brief's
    script is a planning draft; revise it against the real beats before
    generating), placed as AT MOST 4 blocks cut only at sentence boundaries,
    and gated by `scripts/vo_qa.py <placed_vo> <film_seconds>` — no robotic
    holes, no dead air over 5s, narration present in every quarter
    (genrupt-flow §5c-bis; the flow rule used to contradict itself across two
    files and each run picked one at random, which is why some films flowed
    and some were full of silences). **Build the mix with
    `scripts/mix_audio.py`, never by hand**: it
    derives the music gain from the measured VO and music levels and then proves
    the bed is audible by rendering the mix twice, with and against music muted,
    and comparing. It exits 1 on a buried bed. A hand-written ffmpeg line has
    buried the music on three runs and shipped it twice, because every absolute
    number in a finished mix looks correct whether or not the music is there. The music brief is DERIVED from the film's register, cut rhythm and
    energy curve; 2-3 candidates are generated and PICKED by envelope-vs-cuts
    alignment; VO word timings are MEASURED (`scripts/transcribe.py <placed_vo.wav>
    words.json`, which owns the model lookup and the file shape) and verified against
    their beats; the mix keeps SFX forward (they are the realism layer), music
    ducked under, VO on top. Never ship the only candidate unheard.
11. **Overlays — the theme kit** (ALWAYS runs; at most 3 supers) (`references/overlay-grammar.md`). Pick ONE theme
    from `overlays/themes/` (five registers incl. condensed-editorial), lock its
    palette from the product's own label (`scripts/theme_extract.py`) and **cap
    the ink to the plate's highlight** (`scripts/integrate.py measure`).
    **MEASURE THE ROOM BEFORE YOU PICK A SIZE**: `scripts/deadspace.py <film>
    --from T0 --to T1 --lines "line one|line two"` returns the largest rectangle
    that stays clean across the WHOLE window and the biggest type that fits it.
    The theme's hero size is an aspiration; the footage decides. Measured: a
    theme asked for 150px where the roomiest window held 430x370, and the two
    ways that ends are both bugs — type on a person, or type occluded into
    fragments. Build from `overlays/template.html` + `lib.js` with EMBEDDED
    fonts, and QA with `scripts/overlay_qa.py` (theme lock, contrast, STILL-time
    reading, cut adjacency, lead-biased VO sync, breath, hierarchy, anchor-group
    distribution) — FAIL blocks the composite. LOOK at `qa/overlay-boxes/`:
    a box on a face, the product or a label is a REPOSITION, always. There is no
    occlusion escape hatch any more: `scripts/occlude.py` still ships for a
    deliberate one-off, but the pipeline does not call it, because it cost ~5
    minutes, needs a segmentation engine that is not in every environment, and
    once hid 63% of a hero line ("ur, / a ill" reached a customer). Type that sits
    in measured dead space does not need rescuing. After the composite: **matched
    grain** (`integrate.py grain`). Sizes meet Amazon's 50pt/720p floor. **Brand
    marks: real or absent** (taste.md §4b).
12. **THE AUDIO TASTE GATE.**
    Audio is the one layer meters cannot judge: every
    measured number can pass while the track sounds cheap, choppy or wrong for
    the picture (it happened; it failed review twice). So audio gets what
    graphics get: the autopilot briefs THREE music directions that argue with each
    other (never variations of one), renders the film with each, and ships them as
    a listening choice beside the mix it recommends. One track per direction is
    about $0.12. Each brief names a hummable hook, one structural event on a named
    second, and one texture that is wrong for the category (`genrupt-flow`
    5a-brief) — instruments-and-a-mood is an order for wallpaper, and four films
    in a row came back with "I was not happy with the music".
    Flow beats sync: never chop a continuous VO read into segments to
    chase beat alignment — shift the whole read or ask for a re-paced read; a
    choppy voice is worse than a half-beat drift.
13. **Conform + report** — 1280x720, 24fps, final mute-watch pass. Write the run
    report (`scripts/report.py`): every decision, measurement, and dollar, with
    the final film and the audio alternate embedded as players.

    **THE DELIVERY LAYOUT — one file is the answer.** The person asked for a
    video, and a folder where the finished film hides among mixes and takes is
    a failure of the delivery, not a bonus. The run folder ends EXACTLY like
    this, and report.py enforces it (it refuses to write the report over a
    messy out/):

    ```
    out/FINAL-<slug>.mp4     <- the film. The ONLY mp4 at out/ root.
    out/extras/              <- ONE audio alternate. Nothing else.
    out/report.html          <- the receipt, players for FINAL and extras.
    work/                    <- every intermediate: composites, mixes, masks,
                                probe, trimmed segments. Never shown, safe to
                                delete after delivery.
    ```

    When you hand the result to the user, hand ONE path: `out/FINAL-<slug>.mp4`.
    Mention the report; never list the intermediates.

## Policy gate: the video must survive Amazon

A finished film Amazon rejects is worth zero. Before the master renders, run
`scripts/policy_check.py` on the VO script and every planned overlay text
(per `references/amazon-video-policy.md`): no superlative/rank claims, no prices
or promotions, no off-Amazon CTAs, no review quotes, no time-sensitive claims,
no unsubstantiated health claims. A HARD finding rewrites the line before any
credit moves — this is a free fix at that stage and an unusable video after it.

## Re-runs on the same ASIN: variant by default

The render is stochastic but the taste engine is not — left alone, run 2 produces
the SAME commercial as run 1 in a different take. So on every run, FIRST check for
previous runs on this ASIN in BOTH places:

1. **The runs directory**: `runs/<ASIN>*` under the folder the skill runs in (or
   under config `output_dir`). Scan for `run-state.json` files carrying this ASIN.
2. **Genrupt's own record**: `get_project_scenes` on the ASIN's project. Measured:
   a disk scan missed a parallel session's finished run because it looked in the
   wrong folder — the provider's record is the one that cannot be missed, and an
   `IDEMPOTENCY_CONFLICT` on your first render key means the same thing.

If a previous run exists (and the user did not ask for a retake), this run is a
VARIANT: choose differently on at least TWO axes where more than one defensible
option exists, and write the divergence into the report ("Variant B — differs
from run 1: signature move, mood band, hook"). The axes, in preference order:

1. Signature camera move (the category table usually offers two).
2. Mood band (bright-everyday vs warm-lamplit — never force moody-night).
3. Hook concept (a different question, a different incomplete action).
4. World/setting + cast.
5. Overlay theme (where two registers are defensible).
6. Music register.

Never vary just to vary a rule: every variant choice must still pass the taste
engine on its own merits. The point is that a user running the skill three times
gets three FILMS to choose from, not three takes of one film.

**Retake mode** (user asks for "the same film again" / "another take"): reuse the
locked prompt verbatim with a new idempotencyKey, then per-beat A/B the two
masters and frame-splice the best beats (genrupt-flow.md §6d) — measured to beat
either take alone. Variant = variety to pick from; retake = maximum quality of
one film.

## Resume: a broken run never pays twice

Every paid action and completed stage is already recorded in the run's
`run-state.json` as it happens. On invocation, if that file exists for this ASIN
with `status != delivered`: tell the user in one line ("found an unfinished run,
resuming at stage 8 — the master is already rendered and paid for") and continue
from the first incomplete stage. Never re-run research, re-upload references,
re-probe, or re-render a master that run-state shows as completed — verify the
artifact exists (file on disk, or `get_video_generation_result` for a render)
and move on. Only a missing/corrupt artifact justifies re-paying, and that gets
its own money line. Starting a fresh run despite an unfinished one requires the
user saying so; the fresh run then goes to a new run folder (and becomes a
variant per the rule above).


## Reference map (complete)

| File | Owns |
|---|---|
| `references/taste.md` | Every creative decision rule, measured |
| `references/seedance25-rules.md` | Prompt grammar: end states, references, camera, density |
| `references/genrupt-flow.md` | Exact MCP calls, pricing, traps, audio doctrine, edit recipes |
| `references/overlay-grammar.md` | The text system: theme kit, choreography library, overlay QA |
| `references/amazon-video-policy.md` | What Amazon rejects — checked before any credit moves |
| `overlays/` | themes/, template.html, lib.js, embedded fonts.css |
| `scripts/` | compose, lint, prep_refs, qa, deadspace, overlay_qa, theme_extract, policy_check, occlude, integrate, transcribe, mix_audio, vo_qa, report |

Every stage above is runnable; the rules were paid for on real productions (two full
acceptance-grade runs, five review rounds). Do not improvise around a rule — the
measured rules ARE the product. When a rule and reality disagree, measure, fix the
rule, and leave the measurement in the file.
