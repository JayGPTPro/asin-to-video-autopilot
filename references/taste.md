# The taste engine — every creative decision, decided

These rules were paid for: measured on real paid productions, take against take, on the
same model and the same compiler. When a rule says "measured", a film succeeded or died
to establish it. Apply them in order during stage 2 and LOG each decision with its
reason — the run report prints them.

## 0. What is this product FOR? Read the occasion before the features

An outside reviewer ran the skill on a small china figurine sold as a memorial gift
and returned four notes that were really one note: the run read the ATTRIBUTES and missed the INTENT. It did not carry the
bereavement occasion that the title states in plain words, it did not know a shamrock
means luck, it ignored the authenticity backstamp that is the whole trust argument in
heritage china, and it dropped the gift box on a product whose entire use is being
handed to someone. A film can be technically perfect and still be the wrong film.

Before the angle, answer four questions from the listing's own words. The lint checks
all four against `listing.json`, so stage 1 must persist the title and bullets.

- **Occasion.** Who is this bought FOR and on what day? If the listing says sympathy,
  memorial, loss, bereavement, urn, remembrance, hospice, get-well: this is a
  SENSITIVE occasion. Register is `calm`, full stop. Nobody laughs, cheers, high-fives
  or celebrates. No upbeat bed, no groove, no snappy cutting. The film's argument is
  meaning, and the product is handled the way you handle something that matters. Set
  `brief.occasion {sensitive, what, handling}`.
- **Symbols.** A shamrock, a cross, a claddagh, an angel, a birthstone, an anniversary
  number: a viewer reads the MEANING before they read the object. Name each symbol,
  what it signifies, and the beat that shows it WHOLE. A symbol cropped in half is
  worse than a symbol absent. Set `brief.symbols`.
- **Provenance.** "Made in Ireland", hand painted, hallmarked, a certificate, a
  backstamp, "since 1857". In heritage and craft categories this is the trust asset,
  and it has a picture: the stamp, the mark, the signature, the hand at work. Give it
  a beat. Set `brief.provenance`.
- **Packaging.** "Gift boxed" means the box is part of the product, not shipping
  material. The product reference sheets exclude packaging by DEFAULT, so this one
  gets dropped silently unless someone says otherwise. Set `brief.packaging_beat`.

None of this applies to a commodity. A baking sheet has no occasion, no symbol and no
provenance, and the lint stays quiet on it. The rule is not "add ceremony to
everything", it is "when the seller tells you what the product MEANS, believe them".

## 1. Center of gravity: emotion or features (70/30, never 100/0)

Read the reviews' LANGUAGE, not just their complaints. Emotional wording ("felt like
real camping", "my kids loved it") → emotion-led. Functional wording ("stopped
working", "fits the drawer") → feature-led with one emotional beat. The unguided
default of the model is features, and that is the measured boring film. Whatever the
lean, the other side keeps ~30%: a feature film still gets one human payoff beat; an
emotion film still proves the differentiator on screen.

## 2. Hook and close: they rhyme

- The hook is a QUESTION the film answers: tension, an incomplete action, a face
  reacting to something off-screen. Never the product logo, never a spec.
- The close is the hook's mirror: the camera move reversed, the question answered,
  the product at rest in its finished world. Decide the FINAL IMAGE in stage 2 and
  write it into the closing beat — the last five seconds are a fifth of the ad and
  they are what the viewer carries out. A close that just "ends" is a film that
  evaporates.
- **The strongest form of the mirror is IDENTICAL FRAMING, INVERTED STATE.** Not
  "the close rhymes with the hook" — the same lens, the same distance, the same
  person in the same seat in the same posture, and the only thing that changed is
  that the problem is gone. The contrast IS the punch, and it costs nothing to
  write. Prefer it whenever the hook has a person or a fixed vantage; fall back to
  the reversed camera move when the hook is pure product. The lint warns when the
  hook and close use different shot sizes, because the identical-framing version
  is almost always the better film.
- The signature shot does NOT go on the hook. It goes on the hero beat, where the
  viewer already knows what they are looking at.

## 3. People: diverse, faces on, someone reacts

- Faces visible is the DEFAULT — it is this model's strength and the best emotion
  carrier. Below-shoulders framing only with a written reason.
- Across the four use beats: different people, different ages, different settings.
  Same person twice reads as a cheap shoot.
- Cast ages: real buyer age; display under-50 as is, from 50 show ~5 years younger.
- At least ONE beat where a face REACTS to the product as a physical event ("her
  eyes go wide and she leans in"), never an adjective ("delighted"). Audit the plan:
  count face beats and reaction beats before compiling.
- Every cast member gets a NAMED wardrobe. "Keep wardrobe identical" cannot hold a
  wardrobe nobody specified (measured: bare torso one beat, sweater the next).

## 4. Use cases: four beats, four different arguments

Each use beat carries ONE dominant message, a different situation, and a different
proof shape (in-action / result / contrast / context). No two adjacent beats argue
the same way. A skipped selling point is fine; an unfocused beat is not.

## 4b. Brand marks: real or absent, never typeset

NEVER set a brand name in a font and present it as the brand. A typeset wordmark is a
fake logo. The options, in order:
1. **Extract the real mark from the listing images** — crop the brand lockup from a
   clean label shot or A+ banner (straight-on, unwarped). If it survives a crop at
   overlay resolution, use it.
2. **No logo at all.** The product's own label IS the brand mark and it is already in
   frame; an endframe of the product with its label readable needs nothing else.
Plain descriptive text (the product category, a CTA) is fine — it must not be styled
as a logo lockup. Measured failure: a brand name set in a generic font on the endframe
read as a fake logo and failed review.

## 5. The signature shot: one impossible camera move per film

Every film is built around ONE move a real crew could not do. Pick by category:

| Product type | Moves that render well |
|---|---|
| Container / appliance with an inside | The lens travels THROUGH the opening into a macro interior, holds, then reverses out |
| Mechanism / moving parts | Snap-zoom onto the mechanism at the moment it engages; or a whip orbit as it comes apart in mid-air |
| Food / liquid contact | Through-the-pour: camera passes under the stream; suspended droplets, surface tension visible |
| Textile / soft goods | The fabric falls in slow motion and the camera dives INTO the fold as it settles |
| Small / handheld | Drone-style pull-back from macro detail to the whole room in one move |

Write it with the translation formula (term + subject + visible change + direction),
see the rulebook §3. A camera move is the cheapest ambition there is: ~180 characters
that change the whole film. Buy it by REPLACING procedural prose, never by adding.
And probe it first — the most ambitious shot is the most likely to render as mush,
and the probe of exactly that shot is the cheapest insurance in the run.

**THE MOTION FLOOR (measured failure, 14.8: a 5s bullet-time beat rendered near-static
and review called it "barely moves").** A freeze buys stillness ONLY if the camera sprints:
- The frozen hold is capped at ~1.5-2 seconds of the beat, never the whole beat.
- The camera's speed is written in TIME: "the camera sweeps the half orbit in about
  one second", not "orbits the drop".
- Real-time action brackets the freeze: something moves before it and the release is
  a burst (the crash, the splash, the landing), so the beat's energy curve is
  move -> lock -> burst, never a long hush.
- QA verifies this with the per-beat motion metric (qa.py): a signature beat that
  measures near-static failed, whatever the prompt said.
- **Underwater and buoyancy moves are slow by nature** (measured: a beautiful
  underwater plunge was genuinely the film's least kinetic beat). A signature
  move that lives in water must write its BURST into the beat — the surface
  break, the grab, the crash of the crown — exactly as the freeze rule demands
  a sprint around the hold. Drift alone cannot carry a wow shot.

## 5a-bis. A move that goes INSIDE an object must light the inside

Measured twice: a lens travelling through a fan hub produced 0.9s of near-black that
"reads as a black whip", and a move inside a sealed ball measured luminance 32.7
against a 63-196 band. The interior of a real object is dark, and the model renders
that honestly. So a through-the-object signature move must either name its interior
light ("the LED ring ignites and lights the chamber as the lens arrives"), or keep the
interior to under half a second and cut out on a bright frame. Never write a
through-the-object move without deciding which of the two you are doing.

## 5b. Fantasy stays physical: no glitter, ever

Fantasy moments are welcome as PHYSICS (a freeze, an impossible lens path, scale).
They are never PARTICLES. The model decorates hair, fabric and liquids with sparkles
the moment shine is described loosely — a measured artifact ("something glitters in
her hair, completely unnatural"). Rules:
- Shine is written as a surface property: "glossy", "a sheen along the strands",
  "the wet-glass gleam on skin". Never free-floating light: no "catching the light",
  "shimmering", "sparkling", "dancing light".
- The composer bans particles film-wide by default ("no glitter, sparkles, shimmer
  particles, lens flares or magical light effects"); a brief that truly wants
  particles opts out with `allow_particles: true` and a written reason.

## 5c. A face never lives in a reflection

Measured on a mirror-polished baking-sheet film: the brief put the woman's face in the
mirror floor of the
pan ("her face travels upside-down through the mirror beneath the lens"). Seedance
SWAPPED the physics. It rendered the real woman above the rim upside down and her
reflection inside the pan right way up. Two viewers read it the same way: not a mirror,
a broken person. A Gemini Omni edit asked to invert it back changed nothing; the model
does not reason about mirror geometry.

- A mirror beat reflects OBJECTS and LIGHT: the window, the ceiling line, the bowl, the
  product, the food falling in. Those the model gets right, and they prove the finish
  just as well.
- If a person has to be in a mirror beat, they are hands and forearms. No head, no face,
  not in the picture and not in the reflection.
- This is a beat-level ban, not a film-level one. Faces stay ON everywhere else
  (rule 3); the reflection is the one place they break.

## 6. Mood: declared up front, in numbers

Mood is PICTURE, not post. An undeclared mood lets the model choose night, and every
later layer (grade, music, read) follows the picture down — measured on a film whose
team verdict was "frightening". Declare one of three worlds in the brief, with its
target band; QA measures against it and weights the close double:

- **BRIGHT EVERYDAY** — daylight, window light, people smiling. Ease and routine.
  Mean luminance target 90-140. Default for kitchen, home, kids, wellness.
- **WARM LAMPLIT** — evening practicals, warm skin. Ritual and care. 55-90.
  Default for care products, bedding, evening-use items.
- **MOODY NIGHT** — low key, deep shadow. Luxury and seriousness. 25-55. NEVER for
  a family or wellness product; this is the band that turns frightening when the
  music goes minor. Requires a written reason.

Any close darker than ~25 mean luminance needs a written reason in the brief.

## 7. Pace: never slow by accident

The model renders exactly the tempo you describe. Measured: a rejected draft carried
16 slow-words and zero pace words.

- No "slow/slowly/gentle/unhurried" in a camera line unless that beat IS the film's
  one held moment (and there is at most one, at the end).
- Every action COMPLETES inside its own beat.
- Write "real time, no slow motion" into camera lines by default; slow motion is
  spent ONLY on the signature shot or the close.

### 7a. The cut rhythm has to VARY. A uniform grid is the boring film

Measured on a baking-sheet film: the plan was 4/6/4/4/4/4/4 and the render came back
3.79 / 4.75 / 4.17 / 4.08 / 4.33 / 3.83 / 3.96, standard deviation 0.33s. Every check
passed. A viewer watched it and said the pace was very boring, and they were right:
seven shots
of the same length is a slideshow, not an edit. The damage does not stop at the
picture. The music brief derives its tempo from the cut rhythm, so a 4-second grid
wrote itself a 60 BPM bed with "nothing showy" in it, and the film ended up asking for
the boring music it then got.

The plan must satisfy all three, and the lint refuses it otherwise:
- At most TWO shots share the same planned length.
- At least one accent shot of 2 or 3 seconds, and at least one held shot of 5 or more.
- longest / shortest >= 2.0.

Seedance compresses the spread it is given (planned 4/6 came back 3.8/4.8), so plan a
WIDER spread than the one you want to watch. A rhythm that reads on screen starts life
on paper as something like 3 / 6 / 3 / 4 / 2 / 5 / 4.

## 8. Seedance cannot count

Measured four generations in a row: a five-piece set rendered as four, every time,
once with a duplicate. NEVER rest a beat on a countable row of products. Show a
stack, a pile, one hero unit, or the product in use — the set size lives in the
overlay text, where it is typed, not generated. The lint refuses countable rows.

## 8b. A group beat choreographs ONE object's path

Measured (16.8): "the football snaps around the circle, quick low passes" rendered TWO
footballs simultaneously — past an explicit categorical-uniqueness line AND a
"no second football" line, and it cost the film a 3-second trim. A distribution verb
("passes around", "flies between", "goes from X to Y to Z") over several people is an
instruction to render several products; the uniqueness line cannot protect a beat whose
action describes simultaneous handling. **Write the relay, not the flurry**: one
continuous path, named hand to hand — "the same single football goes from her hands to
his, then to the boy's, one object the whole time, never two in the air". The lint
refuses multi-handler beats without this language.

## 9. Density: 230 characters per second of film

Measured: the take that passed ran ~230 chars of compiled beat prose per second; the
take that was rejected ran ~116 — and thin beats read as a licence for the model to
invent. Every beat's action carries THREE physical events, a named lens, the light
direction, and motion speed. If density and the character budget fight, cut a BEAT,
never the detail. (Budget: ~3,400 chars obeyed beat-for-beat; ~7,500 measurably lost
the choreography. The composer reports both numbers.) Plan for the ceiling from
the FIRST draft: with a 4-person cast block, header and references, the beats get
roughly 5,200-5,600 chars — about 55-65 words of action per 4s beat. Writing
long and trimming six times (measured) wastes a session; write to size.

**The target DEPENDS ON DURATION, because the 7,500 ceiling binds first on long
films.** Measured 19.8: a 30s film with a 4-person cast carries ~2,400 chars of
scaffold, so "185-210 chars/sec" would need ~7,950 total — arithmetically impossible
under the ceiling, and chasing it cost a run five rewrite rounds (~10 minutes) before
compiling at 160. The honest bands:
- up to ~15s of film: 210-230 chars/sec on beats
- ~16-24s: 175-200
- 27-30s with a full cast: **155-170, floor 150**
Never iterate toward these by feel: run `compose.py --budget <run_dir>` FIRST. It
builds the real scaffold for this brief and prints each beat's character allowance;
write each beat to its printed number, once.

## 9b. An effect that SPREADS is enumerated, in order, one item per line

When a beat's payoff is something propagating — light filling a room, water
sheeting off a surface, foam rising, a stain lifting, heat blooming, a coating
covering — a single sentence renders as a vague haze. The satisfying version
NAMES 5-8 specific things the effect reaches, in the order it reaches them,
one line each:

> the light catches the rim first, then the handle, then the counter behind it,
> then the tiles, then the far wall

This is the same instinct as the density rule (three physical events per beat)
applied to a single continuous event: the model needs the path, not the noun.
Two guards: keep it to ONE spreading idea per film (two competing effects read
as chaos), and it never licenses particles — the spread is surfaces changing
state, not glitter filling the air (§5b still holds).

## 10. One world

One film, one world. Every extra world costs a cast block and a setting out of the
same character budget and starves the direction. The four use beats vary the corner
of the world, not the world itself.

## 11. End states and references

- Any beat whose counts, ownership or positions must survive the cut ends with
  "End state: …" naming what is visible. QA audits the final frame of each such beat.
- Every reference role states what it defines AND what to ignore; on video
  references the ignore clause is mandatory (a reference donates the objects inside
  it — measured leaks include a nail color and framed paintings from "style" refs).
- Sound in the generated pass is DIEGETIC ONLY. Music and voiceover are post layers
  on the locked cut: effects are welded to the picture and cannot be rebuilt; music
  and VO are cheap to lay again. The lint refuses a music direction or VO line in
  the generated pass.
- **A spoken NUMBER never plays over a countable picture.** "Five drops" narrated
  over one visible frozen drop confused the review ("something here is muddled").
  Since Seedance cannot count, the fix is placement: count lines play over beats
  where nothing countable is in frame (the hook, before anything pours), where the
  number is a promise; the picture then illustrates the ritual, not the count.
