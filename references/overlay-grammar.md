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
   [words.json]` — theme lock, worst-frame contrast, busy-zone scrim demand,
   reading time, size floor, VO sync, breath gaps. FAIL blocks the render.
6. **The box-sheet eye pass is MANDATORY.** overlay_qa writes
   `qa/overlay-boxes/` — sampled frames with every super's box drawn on them.
   LOOK at every frame before compositing: a box on a face, the product, a
   label or hands is an automatic reposition, whatever the numbers said.
   Measured: a super passed every numeric check while sitting straight on a
   person's head. Numbers cannot see a face; the eye pass can.

## The two laws (unchanged, they predate the themes)

1. **INTENSITY FOLLOWS IMPORTANCE.** The differentiator and the objection-killer get
   the loudest treatment; a spec gets a quiet one. Hierarchy is expressed by SIZE
   within the theme's three tiers (hero / line / kicker), never by switching styles.
2. **GRAPHICS LIVE IN MEASURED DEAD SPACE.** Never over the product, a label, a face
   or a hand. Measure the silhouette per SHOT, sampled across the super's whole
   window (subjects move inside a shot).

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
