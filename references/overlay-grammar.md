# The overlay grammar — ONE system, varied performance

**THE HOUSE REGISTER (Jay's pick, 15.8, from a 4-option rendered A/B): THIN CINEMATIC.**
Inter weight 200-300 at every tier, hierarchy expressed by SIZE (tier 3 = ~132px hero
stack, tier 2 = ~40px line, tier 1 = ~30px), per-letter/per-word soft RISES in sequence
(power3.out, 0.05-0.12s stagger), one slow drift during holds, quiet fades out. The
gold accent keeps its one-job-per-beat rule (a drawn rule under the hero, a dot
separator elsewhere). Ink adapts to the zone like ink to paper: cream on dark zones,
the label's deep green on bright zones. Rejected in the same A/B: gold slab fills
(too loud beside the thin register), full-height panels (a different world). The
heavier plate/Z-push system below remains the fallback for busy frames that need
contrast, and for products whose category demands loud (tools, gaming).

Ported from the proven broadcast system (built and approved on real productions).
Five different visual languages in one film reads as an effects showreel; broadcast
keeps ONE system and varies the performance. A diet version of this grammar (thin
kickers, plain slide-fades) failed review — the system below is the floor, not the
ceiling.

## The two laws

1. **INTENSITY FOLLOWS IMPORTANCE.** The differentiator and the objection-killer get
   the loudest treatment; a spec or certification gets a quiet one. Effect is a
   volume knob, never decoration. Tier 3 = a 150-220px hero word plus a second line.
   Tier 2 = ~84px single line. Tier 1 = a small plate or quiet super.
2. **GRAPHICS LIVE IN MEASURED DEAD SPACE.** Never over the product, a label, a face
   or a hand. Measure the silhouette per SHOT (not per beat — subjects move inside a
   shot), sample the whole window the super is alive for.

## The system: two objects only

- **The type stack**: big Inter 800, tight tracking on the hero word, a lighter
  second line. Cream (#F5EFE3) with a soft dark shadow for lift.
- **The plate**: an ink panel (deep neutral from the film's palette at ~0.82 alpha),
  a 4-5px GOLD border on the ENTERING side, 21px/800/5-7px tracking text, 8-16px
  padding. Certifications are plates; kickers are plates.
- **One gold accent** (pick the film's gold once) that does a DIFFERENT job each
  beat — the plate border, a rule under the hero word, a slab behind one word — but
  never changes hue or weight.

## Choreography minimums (a ram-in alone reads as boring — measured)

Every super is a BUILD, not an appearance. The container ram-in is only stage one:
- A stack's lines stagger in separately (0.10-0.14s apart), then the gold rule
  DRAWS itself (`scaleX: 0 → 1` from its origin side).
- A plate lands, then settles (a small scaleX 1.08 → 1.0), or its words pop in
  sequence (`back.out`, ~0.09s apart) — a word-list super pops word by word.
- One slow secondary motion during the hold (a 6-10px drift) keeps it alive.
- Exits stay short and directional. Never animate letterSpacing (reflow stutter);
  per-glyph effects use spans and `x`.

## The entrance and exit (the part the diet version lost)

- **Entrance: a Z-push ram-in from the beat's own side.**
  `gsap.fromTo(el, {x: ∓300, z: -620, rotationY: ∓22, opacity: 0},
  {x: 0, z: 0, rotationY: 0, opacity: 1, duration: 0.5, ease: "expo.out"})`
  with a scaleX overshoot (1.06 → 1.0, 0.12s) that SNAPS. The parent needs
  `perspective` (e.g. 900px) or the z reads as nothing.
- **Exit: fade + a 46px slide back the way it came**, `power3.in`, 0.36s.
- **Mirror the beats that rhyme**: the same plate-then-stack construction on
  opposite sides at different sizes reads as a campaign, not a sampler.

## HyperFrames mechanics for this grammar

- GSAP owns ALL transforms: never a CSS `transform` on an animated node; centering
  via `gsap.set(el, {xPercent: -50})`.
- Per-glyph effects: split into spans and animate `x`, never `letterSpacing`.
- Scale breathing on a block: `transform-origin: left top`, scale the BLOCK.
- Every timed element: `class="clip"` + its own `data-track-index`; register the
  timeline on `window.__timelines`.
- Text shadows count as ink for overlap checks — keep them tight and use margins.

## Brand marks

Real or absent (taste.md §4b). The endframe is the product carrying its own label,
or a real extracted logo. Plain descriptive text is allowed but never styled as a
logo lockup.
