# The taste engine — every creative decision, decided

These rules were paid for: measured on real paid productions, take against take, on the
same model and the same compiler. When a rule says "measured", a film succeeded or died
to establish it. Apply them in order during stage 2 and LOG each decision with its
reason — the run report prints them.

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
long and trimming six times (measured) wastes a session; write to size. On a 27-30s film the ceiling
binds first: fill the budget to just under it (~185-210 chars/sec) and treat 150 as
the floor; 230 is the target only up to ~15s of film.

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
