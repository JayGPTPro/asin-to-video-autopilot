# The overlay grammar — a THEME KIT, locked per film

The text layer is a designed system, never per-super improvisation. Every film gets
ONE theme, chosen by product category, colored by the product's own label, locked in
a single file, choreographed from a shipped library, and QA'd by measurement. A
five-language showreel and a mid-film font drift are the two failures this
architecture makes structurally impossible.

## The flow (stage 11 of a run)

1. **Pick the theme** from `overlays/themes/` by the product's register:
   - `thin-cinematic` — THE DEFAULT (won a 4-option rendered A/B). Wellness,
     beauty, home, food, baby, anything calm or premium.
   - `kinetic-bold` — tools, gadgets, sports, automotive, gaming. Power products.
   - `playful-round` — kids, pets, party, novelty.
   - `label-echo` — heritage/craft/luxury packaging where the label IS the design.
   Log the choice + reason like any taste decision.
2. **Lock the palette from the label**: `scripts/theme_extract.py <label_plate>
   <base_theme> <run>/theme.json`. The accent and dark ink come from the product's
   own packaging (k-means over the cleanest label plate) — an overlay that echoes
   the label reads as designed for this product; a template gold reads as a template.
   The output `theme.json` is the run's single source of truth.
3. **Build from the template**: copy `overlays/template.html`, `overlays/lib.js`,
   `overlays/fonts.css` into the run. Fill the THEME BLOCK from theme.json — fonts
   are EMBEDDED woff2 (no network, no installed-font dependency; this is what makes
   non-Inter themes real). Every super takes its size, weight, tracking, ink and
   accent from the theme classes. **No super ever declares its own color or font.**
4. **Choreograph from `lib.js` only.** Entrances/holds/exits are the library's named
   builds, mapped per theme in its JSON. Every super is a BUILD (entrance + one
   secondary motion during the hold + exit), never a bare fade.
5. **QA the layer**: `scripts/overlay_qa.py <index.html> <film.mp4> <theme.json>
   [words.json]` (build words.json with `scripts/transcribe.py`) — theme lock,
   worst-frame contrast, busy-zone scrim demand,
   reading time, size floor, VO sync, breath gaps. FAIL blocks the render.
6. **The box-sheet eye pass is MANDATORY.** overlay_qa writes
   `qa/overlay-boxes/` — sampled frames with every super's box drawn on them.
   LOOK at every frame before compositing: a box on a face, the product, a
   label or hands is an automatic reposition, whatever the numbers said.
   Measured: a super passed every numeric check while sitting straight on a
   person's head. Numbers cannot see a face; the eye pass can.
   **A reposition moves the super to a DIFFERENT screen quadrant than its
   neighbors, never just to the nearest empty space.** Measured: an eye-pass
   fix nudged a super sideways into the same corner as two others, and the
   film shipped with four supers stacked top-left. overlay_qa's set-level
   DISTRIBUTION check now refuses a stacked corner, and its HIERARCHY check
   refuses a film whose supers are all one tier or never use the hero tier —
   the two laws below are enforced, not aspirational. The differentiator gets
   the top tier; the close never carries the smallest text in the film.

## The two laws (unchanged, they predate the themes)

1. **INTENSITY FOLLOWS IMPORTANCE.** The differentiator and the objection-killer get
   the loudest treatment; a spec gets a quiet one. Hierarchy is expressed by SIZE
   within the theme's three tiers (hero / line / kicker), never by switching styles.
2. **GRAPHICS LIVE IN MEASURED DEAD SPACE.** Never over the product, a label, a face
   or a hand. Measure the silhouette per SHOT, sampled across the super's whole
   window (subjects move inside a shot).

**Law 1 answers to law 2: MEASURE THE ROOM BEFORE YOU PICK THE SIZE.** The theme's
hero size is an aspiration, not a promise the footage can keep. Run
`scripts/deadspace.py <film> --from T0 --to T1 --lines "A pour,|not a pill"`: it
unions the busy pixels across the whole window, finds the largest rectangle that
stays clean, and prints the biggest type that fits it. Measured on a liquid-supplement film:
the theme asked for 150px and the film's roomiest window held 430x370px of clean
background. Only two outcomes exist when the tier does not fit, and both are bugs —
the super sits on a person, or it gets occluded into fragments. **Shrinking the tier
to the film's real dead space is the fix; 90/58/50 still reads as a clear
hierarchy.** A tight film simply has a smaller hero, and that is not a compromise:
text nobody can read has no tier at all.

The tool's thresholds are calibrated against regions known to be good and known to
be busy, and it is deliberately CONSERVATIVE — it will never tell you an oversized
number is safe. Defocused background that drifts under a moving camera is not busy;
that is exactly where type belongs. A hard edge is.

## Placement and motion intelligence

- **Ink adapts to the zone like ink to paper**: `ink-light` (theme cream) on dark
  zones, `ink-dark` (the label's own dark) on bright zones. overlay_qa measures the
  zone; when worst-frame contrast is under 3.2:1 or the zone is busy (luminance
  std > 55), add the theme scrim or a plate — the QA demands it, don't debate it.
- **The entrance follows the camera.** The shot plan names each shot's dominant
  camera move; a super enters along that vector's side (camera tracking left =
  enter from the right, moving WITH the world). An arbitrary entrance direction
  reads as pasted on.
- **Land on the music.** Super entrances snap to the nearest music onset/beat
  within ~0.25s (the audio stage already extracts the RMS envelope — reuse its
  peaks). Ties break toward the VO word time.
- **VO owns the clock**: in/out times come from MEASURED whisper word timestamps
  (`data-vo="the spoken phrase"` on the super, checked by overlay_qa within
  ±0.35s). A super never asserts a different claim than the words playing under it.
- **The signature shot's peak is text-free.** Nothing competes with the wow moment;
  a super may live in the beat's entry or exit, never across the freeze/burst.
- **Breath**: at least 1s between one super's exit and the next entrance.

## Choreography minimums (a bare appearance reads as boring — measured)

- A stack's lines stagger in separately, then the accent rule DRAWS itself
  (`ruleDraw`, scaleX 0→1 from its origin side).
- A word-list super pops or rises word by word (`wordPop` / `wordRise`).
- One slow secondary motion during every hold (`drift` / `microShake` /
  `gentleSway`, 6-10px) keeps it alive.
- Exits stay short and directional for kinetic, quiet fades for thin/label-echo.
- ONE hero number per film may `counterRoll`; several counting numbers is a
  dashboard, not an ad.
- The accent does ONE job per beat (rule / dot / slab / pill — the theme lists
  its two allowed jobs), same hue and weight all film.
- Mirror the beats that rhyme: the same construction on opposite sides at
  different sizes reads as a campaign, not a sampler.

## The integration pass (make the type belong to the plate)

Amateur text is applied ON a video; professional text is built INTO it. Three
mechanical steps, all measured (research doc 17.8):

1. **Ink capped to the plate's highlight.** `scripts/integrate.py measure <film>`
   once per film → scale the theme's `ink_light` so its luma never exceeds the
   99.5th-percentile luma of the plate. Measured: pure #FFF was 55% brighter
   than the plate's own brightest pixel and read as a sticker. This one line
   does more than every other integration step combined.
2. **Matched grain AFTER the composite**, over everything:
   `integrate.py grain <in> <out> --sigma <measured>`. Grain on the film but
   not the type is the loudest amateur tell.
3. **Sub-pixel soften** — `filter: blur(0.3px)` on supers (in the template).
   Real lenses never resolve a perfect edge.

## Occlusion — the subject passes IN FRONT of the text

The single loudest "expensive" move available: one hero super per film crosses
the frame at hero scale, and the person/product occludes it
(`scripts/occlude.py <composite> <plate> <out> --from T0 --to T1`). Rules:

- **ONE occlusion moment per film**, on the hero-tier super. Everywhere = gimmick.
- The occluded super is **exempt from the dead-space law** — text may cross the
  subject exactly because the subject wins. Mark it in the HTML with a comment
  and check the effect by eye in the final (the subject's face must sit ON TOP
  of the letters).
- **THE LEGIBILITY BUDGET: at most ~35% of the glyphs may be hidden, and
  occlude.py now measures it and REFUSES past the budget.** Measured failure
  on a liquid-supplement film: the subject was punched over "A pour, not a pill" and the
  customer received "ur, / a ill" — 63% of the type hidden on average, 84% at
  worst. Every other check passed, because they all run on the PRE-occlusion
  render: contrast, reading time, VO sync and breath were all measured on text
  that was about to be covered up, and the occlusion verify only asked whether
  the window still moved. **Exemption from the dead-space law was never
  exemption from being readable**, and nothing in the pipeline was asking the
  only question that decides whether the super did its job.
  The gate is hard, it deletes its own output on failure, and a shipped
  occlusion that read well measured ~7-20% hidden. When it refuses, the fix is
  placement or size, never a bigger budget.
- Mask only the super's window, never the whole film. ~1.4s/frame with rembg;
  the macOS Vision engine (auto-detected) is ~8x faster.
- occlude.py self-verifies: it FAILS if the occluded window comes out frozen
  (measured failure: inline trims + fps filters in the merge graph froze the
  segment; the fixed pipeline pre-trims to clean intermediates).

## Timing laws (broadcast-grade, enforced by overlay_qa)

- **Reading time counts only while the text is STILL** — entrance/exit motion
  is subtracted (0.9s overhead) before the words-per-second check.
- **Cut adjacency**: never start a super in the 1s before a cut (start ON the
  cut ±2 frames instead), never let one die in the 1s after a cut (die ≥2
  frames before, or live ≥1s past). A cut through moving text sends the eye
  back to the start of the line.
- **VO sync is lead-biased**: the super lands 0.1-0.3s BEFORE its spoken
  phrase (read first, hear second). Max lead 0.35s; max trail 0.05s.
- **Every super whose words are SPOKEN is a synced super, tagged or not.**
  Measured 18.8: the sizes super lost its `data-vo` during a contrast fix, the
  sync check only ran on tagged supers, and the numbers reached the customer
  4.1s after the narrator read them. overlay_qa now looks an untagged super's
  own words up in the transcript (digits spelled out, filler words tolerated,
  so a typed `9″ · 12″ · 16″` matches a spoken "nine, twelve and sixteen") and
  fails it if the type arrives more than 0.5s late or has vanished more than 1s
  before the line. **Never drop `data-vo` to make another check pass.**
- **The read is placed to the SUPERS, not the other way round.** The VO is one
  take, but §5c-bis allows up to four blocks cut at sentence boundaries: use
  them. If a line's words belong to a beat, delay that block until they land on
  it (keep the gap ≥2.0s so vo_qa reads it as a breather, not a hole). Moving
  one block is free; re-timing the picture is not.
- **Anchored groups**: successive supers may share ONE optical center (the
  RSVP pattern — less eye travel, faster reading). Variety is required BETWEEN
  groups, not within them.

## The style card

Before compositing the full film, render ~6s of one real beat with the locked
theme (`npx hyperframes render` on a trimmed clip). It costs seconds, ships in the
report, and is the eye-check that catches a theme that measured fine and looks
wrong. Swapping the theme is a one-line change + re-render, free.

## HyperFrames mechanics

- GSAP owns ALL transforms: never a CSS `transform` on an animated node; centering
  via `gsap.set(el, {xPercent: -50})`.
- Never animate `letterSpacing` (layout reflow stutter — the lint catches it as
  `gsap_non_transform_motion`). Per-glyph motion = spans + transforms
  (`splitGlyphs()` in lib.js).
- Every timed element: `class="clip"` + its own `data-track-index`; register the
  timeline on `window.__timelines`.
- Text shadows count as ink for overlap checks — keep them tight and use margins.
- The heavier plate/Z-push system lives on in `kinetic-bold` and as the documented
  escape for busy frames in any theme (a plate is the strongest scrim).

## Brand marks

Real or absent (taste.md §4b). The endframe is the product carrying its own label,
or a real extracted logo. Plain descriptive text is allowed but never styled as a
logo lockup.
