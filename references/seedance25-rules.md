# Seedance 2.5 prompt rulebook

Grounded in ByteDance's official Seedance 2.5 prompt guide (published at
docs.byteplus.com/en/docs/ModelArk — read it there for the full first-party text),
distilled here and layered with rules measured on real paid productions. Where the official guide and a measured result disagree, the
measured result wins. The composer (`scripts/compose.py`) owns the prompt text; these
rules are expressed by how you fill the brief and shot plan fields.

## 1. Stage grammar: dense beats, one state change, a named end state

- Each beat is one timecoded block with ONE primary state change, told through ~3
  physical micro-events (density rule, taste.md §9).
- **End states.** A beat whose counts, ownership, or positions must survive the cut
  sets `end_state`: "the jar stands closed in the center, label to camera, her hands
  out of frame". This is the official mechanism for the measured failure class of
  props drifting and payoffs starving.
- **Carry-over.** A beat inheriting fragile state opens its action with "Continuing
  from the previous shot, the same …". Spend it only where drift is likely.
- **Timestamps are a time budget, not edit points** (official). Actions may land
  slightly off the boundary. Never demand frequencies ("three actions in one second").

## 2. References: USE + DO-NOT-USE, one object

- Every reference `role` states what it defines AND what to ignore: "the exact
  lantern: matte green shell, fold-flat handle. Do not use the paper backdrop or the
  props beside it". Role text must not end with a period (the composer adds one).
- On VIDEO references the ignore clause is MANDATORY, naming identity, scene and
  incidental detail: "Do not use the person's identity, clothing, or scene from the
  video". A reference donates the objects inside it.
- **Multiple product images declare one object** (official multi-view rule): each
  role reads "front view of the same single <noun>", "underside of the same single
  <noun>". The composer adds the categorical uniqueness line ("no other <noun>
  exists anywhere in this world") from `product_noun` — both are needed.
- Fill `serves` on every non-product reference; the composer addresses it to its
  beats by timecode (the official per-scene selection). An empty `serves` is a
  film-wide reference by accident.
- Separate view images beat collages. Limits: up to 30 images / 10 videos (30s
  combined) / 10 audio, but 5 focused references measurably beat 10 diluted ones —
  the official recommended range (1-8 subjects) agrees.

## 3. Camera: one dominant move, translated into what the lens sees

- One dominant camera move per shot. With several subjects, name whom the camera
  follows, where the move starts, and where it ends.
- Uncommon or ambitious terms: keep the term AND translate it — term + target
  subject + visible change + foreground/background relation + direction or speed.
  "Rack focus: shift focus smoothly from the steam in the foreground to her face;
  the steam blurs as her face sharpens."
- Required detail per technique (official): dolly zoom names the subject whose size
  is preserved; bullet time names the frozen action and orbit direction; a speed
  ramp names where it accelerates, decelerates, and its resting state.
- **Temporal set pieces need a NAMED EXCEPTION**: "time locks completely at the peak
  of the pour; only the boy remains free to move". The exception is what makes a
  freeze readable. Release it exactly at a beat boundary.
- Physics vocabulary fills density with meaning: liquid ribbons, suspended droplets,
  surface tension, sharp motion blur only on moving elements, flour sprays
  realistically. Concrete outcomes, never quality adjectives.

## 4. Emotion: trigger, then observable cues

Structure (official): trigger event → immediate visible reaction → 2-4 cues (eyes,
brows, mouth, breathing, hands) → restrained or explicit end behavior. In action
prose: "The lid clicks; her fingers stop on the counter, her eyes go wide, and she
leans in." Two to four cues; more is a list. Never a feeling-word without its cue.

## 5. Audio in the generated pass: diegetic only

- Per-beat `ambience` compiles to "Sound: …" inside its own beat — placed sound
  renders reliably; a merged film-wide cue pile does not.
- No music, no voiceover in the generated pass (taste.md §11). The composer bans
  both in the constraints block automatically. The VO script lives in
  `audio.vo_script_for_post` and is laid in stage 10 against the locked cut.
- Post-VO language: name language + regional variety + delivery ("warm, natural
  American English") — the official dialogue-language reinforcement.

## 6. Global constraints the composer writes for you

- "No jump cuts. No text overlays, captions or subtitles." — text is post, where a
  keyword swap is free and spelling is guaranteed.
- The categorical uniqueness line from `product_noun`.
- Your `forbidden` entries, normalized: start each with "no/never/keep" or the
  composer prefixes "No " (an entry phrased as a positive sentence would otherwise
  compile into its own negation).
- Design silence: no hex colors, fonts, or palettes anywhere in the prompt — the
  overlay layer owns the look. The lint refuses violations.

## 7. Known model limits (official + measured)

- Timestamps are budgets; text in frame is unreliable (post owns all text).
- Editing locks the source's aspect ratio and duration (±0.3s); first-frame inputs
  lock the ratio; extension locks ratio, duration settable.
- Seedance cannot count (measured, taste.md §8).
- Reference aspect ratios must sit in [0.5, 2.0] after prep — a failed reference
  DOWNLOAD bills real credits; a content-filter refusal is free. Check ratios at
  prep time, always.

## 8. Pre-flight checklist (run after lint, before any credit moves)

1. Every reference role has its ignore clause; product pack declares one object.
2. `serves` filled on every non-product reference.
3. End states on the hero, the close, and every fragile beat.
4. No bare emotion adjectives; no untranslated niche camera terms.
5. Signature shot present, on the hero, written with the translation formula.
6. Density: for films up to ~15s target 230 chars/sec on compiled beat lines. For a
   27-30s film, 230/sec collides with the character ceiling by arithmetic — fill the
   budget to just under the hard ceiling instead (lands around 185-210/sec) and never
   go below 150, the measured floor that still followed its plan.
7. No slow-words outside the one held beat; "real time" stated.
8. No countable product rows anywhere.
9. Mood band declared; closing beat consistent with it.
10. Diegetic-only audio confirmed: no music direction, no VO lines.
