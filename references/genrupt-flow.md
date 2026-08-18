# Genrupt flow: the exact calls, in order, with the traps

All via the Genrupt MCP. Prices move — read them live, never from this file.

## 0. Balance + planning prices (free)

`get_credit_balance_and_costs` with NO operations — for the balance only.
**Do not price the renders from `presets`: the presets path cannot quote
Seedance 2.5.** Measured (16.8): a preset request for `seedance_2_5_reference`
silently resolved to `seedance2_fast_t2v_720p` keys, returned wrong numbers and
clamped the duration to 15s "for this model". Plan headroom from the measured
constants below, then treat the **`costPreview` block in each `generate_video`
response as the authoritative number** — that is the line you log.

Measured true prices (16.8.2026, at $0.06/credit — re-verify against costPreview
every run, Genrupt pricing moves):
- probe 4s/480p `seedance25_ref_480p` = 9 credits = $0.54
- master 30s/720p `seedance25_ref_720p` = 135 credits = $8.10
- audio, Seed Audio 30s = 2 credits = $0.12 per track

**Re-measured 18.8.2026, and both renders cost MORE than the line above** — probe
11 credits ($0.66), master 163 credits ($9.78), quoted by `costPreview` on the same
model and settings two days later. Plan headroom from the HIGHER numbers: a run that
budgets $8.10 for the master and holds $2 back for a fix is already over before the
fix. The file keeps both readings on purpose — the point is not which is current,
it is that the price moved 21% in two days and only `costPreview` knows.

## 1. Research scrape (free)

`scrape_video_reference_images_from_asin {asin, maxImages: 9}` → background op →
`wait_for_operation {operationId}` → `referenceImageUrls` (media-amazon URLs).
Download each URL and LOOK at every image (titles lie; the images are the truth).
The auto-created project name later echoes the real listing title — free research.
If Amazon page text is bot-blocked, ground the brief in the gallery itself: the
seller's own chosen argument, plus category knowledge. Log that fallback.

## 2. Reference prep (free)

- Screen every image for REAL PEOPLE — most beauty/lifestyle galleries are 60-80%
  people shots and every one of them can kill the render at the provider filter.
- Cut clean plates with `scripts/prep_refs.py` (spec-driven crops + ratio pad to
  [0.5, 2.0]). Marketing text and badges BAKE INTO renders — crop them out; paint
  out infographic connector lines with a corner-sampled background fill.
- LOOK at every finished plate before upload. A sliver of a face or a badge edge
  at a crop border is exactly what the first audit exists to catch.
- Upload: `genrupt upload media <folder> --json` → public URLs. A reference the
  provider fails to DOWNLOAD bills real credits (ratio outside [0.4, 2.5], dead
  URL); a content-filter refusal is free and fails in ~15s.
- **Never retype a reference URL. Copy it from run-state, and curl-check every URL
  returns 200 immediately before EVERY render call.** Measured: one hand-typed
  character in a 90-character URL cost a failed master (billed) — the URL check is
  two seconds, the failure is real money.

## 3. Probe (paid, ~11 credits at 480p x 4s)

Compose a one-beat probe (the SIGNATURE shot, the most fragile thing in the film)
via `compose.py` on a probe shotplan — never hand-write it. Then `generate_video`:

```jsonc
{
  "prompt": "<probe master-prompt.txt>",
  "asin": "<ASIN>", "videoIntent": "custom_video",
  "modelType": "fal_seedance", "seedanceModel": "seedance_2_5_reference",
  "seedanceMode": "reference_to_video", "seedanceDuration": 4,
  "seedanceResolution": "480p", "seedanceAspectRatio": "16:9",
  "seedanceGenerateAudio": true,
  "seedanceReferenceImageUrls": ["..."],
  "promptEnhancement": "already_enhanced",   // compiled prompt is final
  "idempotencyKey": "a2v-<asin>-probe-1"
}
```

Poll `get_video_generation_result {commandId}`. THE trap, measured hard on 14.8: the
status API served a frozen `processing` for 50+ minutes on a job that had actually
COMPLETED 5 minutes in — and the BALANCE lagged the same way (a 16:10 balance check
showed the credits unspent for a 15:24 completion), so neither status nor balance is
a reliable "lost job" differential inside the stale window. The rule that survives:
**never re-queue before 60 minutes have passed since queue time — and prove the
elapsed time with `date`, never by counting the sleeps you issued.** Measured: in
some harnesses background sleeps do not block the next call, and a session
"waited" minutes in seconds; only `date` against the queue timestamp is real.
A premature requeue
double-bills (147 x 2 on that run — both takes rendered; the only consolation is that
two takes of one prompt are an A/B, pick the better one). If 60+ minutes pass with
frozen `updatedAt` AND an unchanged balance, then re-queue with a new idempotencyKey,
with the cap sized for the possible double.
A `fictionalAvatarApproval` in the response means a reference was flagged as a real
person: drop or replace that plate (people-free product plates are the fix that
always ships); the refusal was free.

QA the probe: `qa.py <probe.mp4> <run_dir> --probe` (mood band) + LOOK at frames
for product fidelity (label, glass, proportions).

## 4. Master (paid, ~147 credits at 720p x 30s)

Same call, full compiled prompt, `seedanceDuration` = the compile result's
duration (the 7-beat template sums to 30),
`seedanceResolution: "720p"`, new idempotencyKey. Diegetic sound only by
construction (the composer bans music and voice).

## 5. Post audio (paid, quoted live) — derived, auditioned, measured

The first shipped mix failed review as "boring, unmatched to the picture, does not
flow" because the music was briefed generically and one candidate was accepted blind.
The process that replaces it:

**5a. The music brief is DERIVED from the film, never generic.**
Build it from three film facts: the register (energy/desire/calm), a TEMPO, and the
film's ENERGY CURVE named
beat by beat ("rises with the hook, suspends and empties out during the frozen hero
beat, grooves through the four use beats, resolves warm on the close"). Write that
curve INTO the promptRequest with rough second marks. A bed that ignores the film is
wallpaper; wallpaper is what failed.

**5a-brief. Three CONTRASTING directions, and every one names an event.**
A reviewer, after watching four finished films: "in most of the videos I was not
happy with the music."
The cause is not the level and not the model. It is that the brief keeps ordering
instruments and a mood, which is an order for wallpaper, and then two near-identical
candidates get generated so the choice is between one idea and itself.

Every music brief names three things or it is not finished:
- **A HOOK** you could hum: "a kalimba motif of four notes that repeats", "a plucked
  guitar figure of five notes with tape delay". Not "a warm melodic line".
- **ONE STRUCTURAL EVENT on a named second**: "at about 16 seconds everything stops
  for half a beat, then the hook returns alone". A bed with no event is flat, and
  `mix_audio.py` now measures that (quarter-to-quarter arc; the bed the user called
  boring scored 0.8 dB, the three that replaced it scored 7.9, 8.6, 8.2).
- **ONE TEXTURE THAT IS WRONG FOR THE CATEGORY**: the register to reach for is a
  premium technology ad, never the category cliché. A kitchen product does NOT get
  cooking-show music. The strongest of the three directions built the percussion out
  of the product itself, a fingertip ring on the steel, a knife tap, a drawer slide,
  quantised into a groove.

And generate THREE directions that argue with each other (found-sound score / pulse
and pluck / warm bloom), never three variations of one. One track each, about $0.12,
and the user picks by ear. Two variations of one idea is not a choice.

**5a-tempo. The tempo comes from the REGISTER, never from the cut grid.**
This paragraph used to say "4s beats → 60 or 120 BPM so phrases land near cuts", and
on 18.8 that arithmetic wrote a real film a 60 BPM felt-piano bed with "nothing showy"
in it, off a shot plan that was 4/6/4/4/4/4/4. The verdict on that delivery was that
the music and the pace were both very boring, and both came from the same line of maths.
A cut grid is a symptom of the plan (see taste 7a, which now refuses a flat one); it
is not a musical instruction.

- Tempo floor is **85 BPM** unless the brief argues in writing for slower, and calm
  register does NOT count as that argument: calm is an instrument and arrangement
  choice (felt piano, brushes, upright bass), not a slow tempo.
- Never write "a bar must land every N seconds" into a music prompt. Ask instead for
  one lift and one resolve, placed at second marks taken from the energy curve.
- Mix it with `--under 2 --ratio 1.5 --release 200 --sfx 0.55` under a continuous
  read. The old defaults (6 dB under, ratio 2.5, release 550, ambience at unity) put
  the bed **+0.7 dB under the voice and +4.6 dB louder the moment the read stopped**,
  which is exactly the report that came back: "you barely hear the music, at the end
  you do."
  The release has to be shorter than the read's shortest gap (0.47s here) or the duck
  never recovers, and the diegetic kitchen sound is usually the real masker, not the
  voice.

**5a-ter. A music refusal is a COIN FLIP, not a verdict on your brief — retry it.**
Measured 18.8: Seed Audio `audioMode: "music"` returned `Content Policy Violation`
seven times on a kitchen-music brief while `voiceover` succeeded on the same
pipeline minutes apart. The refusals do not track the prompt. Two near-identical
short prompts fired seconds apart in the SAME project split pass/fail; a long
derived brief failed, a short one passed, then the same short shape failed again.
The run lost about twenty minutes to rewriting a brief that was never the problem.

The rule: **on a music refusal, fire the same request again.** Vary nothing but
the idempotency key for at least three tries before touching a word. If it still
refuses, try a short (~80 char) prompt and a fresh project — both correlated
loosely with passing — but treat that as a lottery ticket, not a diagnosis, and
never let a refusal talk you into shipping the generic bed the derived brief was
written to replace. Refusals cost zero credits, so retrying is free and rewriting
is what costs the run its music.

**Seed Audio ignores `durationSeconds` for music.** Measured: 29s requested,
16.5s returned, twice. Build the bed to length yourself with a crossfade loop
(`acrossfade=d=0.7`) and fade the tail, then let `mix_audio.py` gate it — a raw
short track leaves the film's second half silent and the differential check
catches exactly that (measured: an alternate scored +1.9 dB against the +2.0
floor purely because its bed ran out halfway).

**5a-bis. Audio is CHEAP and priceable via presets.**
Quote it live: `get_credit_balance_and_costs {presets: [{workflow:
"audio_generation", audioDurationSeconds: 30, trackCount: N}]}` returned a real
preview (measured live: 2 credits, ~USD 0.12 per 30s track). The old
operation-key form still has no audio key — use the presets form. So generating 2-3 music candidates costs
well under a dollar and the quality gain is worth it. What you must NOT do is infer
the price from a balance delta: one run did that with other sessions active and
reported a USD 27.06 spend on a run that truly cost about USD 9.36. Count the tracks
you fire, multiply by `audio_track_usd`, add it to the running total.

**5b. Generate 2-3 music candidates and PICK against the cut.** At ~USD 0.20 each this
is the cheapest quality decision in the run. For each candidate: extract the RMS envelope
(`ffmpeg -af astats` per second, or numpy on the decoded wave) and score how its
swells align with the film's cut points and its quietest bar with the hero freeze.
Pick the best-aligned; note the scores in the report. Never ship the only candidate
unheard.

**5c. VO timing is MEASURED, not assumed.** Transcribe the generated VO with word
timestamps (`whisper-cli -ml 1`). Verify each content line overlaps the beat that
shows it (the "roots" line over the scalp beat, the brand line over the close). Text
overlays take their in/out times from these measured word times — never from guessed
line positions.

**The script WRITES the delivery (measured failure: robotic pauses).** Seed Audio
stops dead at every period — a script of staccato fragments ("Five drops. That is
the whole ritual. For your scalp. Your skin.") renders with unnatural gaps between
words (a 1.9s hole was measured mid-phrase) and fails review as robotic. Write the
VO script as CONNECTED sentences with commas and colons, tell the writer "one
natural conversational flow, no long pauses", and QA the take mechanically: whisper
word timestamps → the largest inter-word gap must be under ~0.9s AND sit at a
sentence boundary, never inside a phrase. Generate 2 takes and pick by gap profile.

**The music FLOOR (measured over-correction, and measured AGAIN 17.8).** After "the
music is boring" the next mix buried it at -16dB under and failed review as "I hear
no music at all". It happened a THIRD time on the bug-zapper run and shipped that
way, so the floor now has numbers and an honest test instead of a feel.

**Set the gain from measured levels, never from a guessed multiplier.** Measure both
sources (`ffmpeg -i X -af volumedetect -f null -`), then place the bed 8-10dB under
the voice's mean. Worked example that failed: VO mean -19.6dB, music mean -24.4dB,
and a `volume=0.30` guess put the bed at ~-35dB — 15dB under, not 9. The correct
factor was ~1.0.

**Duck GENTLY, because the read is nearly continuous.** A 74-80% speech budget means
a ratio-6 sidechain is not ducking, it is a permanent mute: the bed only surfaces in
the handful of half-seconds between phrases. Use ratio 2.5-3 with a threshold high
enough that quiet passages pass untouched, and expect the bed to dip a few dB under
speech, not twenty.

**THE VERIFICATION THAT ACTUALLY WORKS.** The old check — "in a speech-free second
the mix's RMS must be well above the SFX track alone" — is BROKEN, and it is broken
in the direction that ships a silent bed: the mix also contains the VO, so it towers
over the SFX track whether or not the music is there. Measured: that check reported
every diegetic moment healthy while the music was inaudible to the user. Replace it
with a differential:

1. Render the mix twice, identical except `volume=<music>` vs `volume=0.0001`.
2. Compare per-half-second RMS: `delta = 20*log10(with/without)`.
3. **The music is present only if the mean delta is >= 2dB** (a shipped, approved
   mix measured +4.6dB mean, +24.7dB peak). Anything under ~1dB is a silent bed
   whatever the LUFS says.

A single number from the mix alone can never prove a bed is audible. Only the
difference between two renders can.

**5c-bis. THE FLOW DOCTRINE — one rule, because two contradictory ones shipped
choppy reads.** This file used to say "place the VO as SEGMENTS, one line per
beat" while the taste gate said "never chop a continuous read" — and each run
picked one at random, which is exactly why some films flow and some are full of
dead holes. The unified rule:

1. **The read is FINALIZED after the locked cut, not before.** The brief's
   vo_script_for_post is a planning draft. Once the master is QA'd and its true
   cut times are known, REVISE the script against the real beats (which claims
   land where, what got trimmed) and only then generate the read. A read
   recorded against an imagined film is why narration feels pasted on.
2. **Script budget: spoken words fill 55-80% of the runtime**, with air written
   in around the freeze and the close. Wall-to-wall cannot stay in sync.
3. **Generate 2 takes of ONE continuous read** and pick by whisper gap profile
   (no intra-phrase hole over ~0.9s).
4. **Place the pick as AT MOST 4 BLOCKS** (hook / body / body / close), cutting
   ONLY at sentence boundaries. Inside a block the read is untouched — the
   pauses inside it are the narrator's own breathing and they are what "flows"
   sounds like. If block placement cannot reach sync, buy a re-paced read
   (~USD 0.12) instead of a fifth cut. A line may bridge a beat boundary by a
   few tenths; a line a whole beat from its picture is the failure.
5. **Gate it: `python3 scripts/vo_qa.py <placed_vo.wav> <film_seconds>`** —
   blocks ≤ 4, no hole inside a block over 0.9s, no gap between blocks over
   5s, one spoken word in every quarter of the film, speech coverage 50-85%,
   and the last word inside the final quarter. It exits 1 with the finding;
   a failing layout gets re-spaced or re-paced, never shipped.
   The gaps BETWEEN blocks are musical, not dead, because mix_audio.py has
   already proven the bed is audible there — the two gates only work together.

**5d. The mix hierarchy: SFX are the realism layer.** The diegetic track is what
makes the picture feel real, and it is the layer that cannot be rebuilt — it sits
FORWARD (target around -22 LUFS contribution), music UNDER it (-28 to -30 under
speech, sidechain-ducked by the VO), VO on top (~-16 integrated). After the mix,
QA per beat: every named `ambience` sound must be audible over the bed at its
moment — a click, a plink and a mist hiss that exist in the track but cannot be
heard did not happen.

**5d-bis. A live insect leaving the product, and the class of error it belongs to.**
Measured on the bug-zapper run: at 0:12 a mosquito flew OUT of the racket's mesh and
away, alive — the exact inverse of the product's promise, in a beat QA scored clean.
No metric catches this: luminance, motion, end states and the box sheet all passed.
Only watching does. Add to the eye pass a per-beat question: **does anything on
screen argue AGAINST the product?** A bug escaping a zapper, a spill near a cleaner,
a crease in a wrinkle remover.

The fix is free and it is a TRIM, but the trim has one rule: **excise to a real
scene-detect boundary, not to the offending frame.** Cutting 12.55-14.04 (out-point =
the film's own cut) reads as an ordinary cut; cutting 12.55-13.65 would have left a
jump inside a static shot. Then keep sync by time-compressing the VO and music by
`old_duration / new_duration` (1.05 here, inaudible on speech) rather than shifting
or re-cutting the read, and re-measure the word times: the run kept 6/7 lines inside
their beat with the 7th leading its beat by 0.34s, which is correct lead-bias.

**5e. A content-checker refusal never dumbs the brief down.** Change the flagged
word, keep every specific musical instruction. Measured trap: the word "bed" in a
track TITLE drew two refusals, and the retry that also simplified the prompt
produced the generic track that failed review. Fix the word, not the ambition.

**5e-bis. But first check it is not the trackCount (measured 17.8).** Six music
refusals on one run were NOT about wording: `trackCount: 3` was refused with a
1,300-char brief, a 400-char brief and a 120-char brief alike, while the SAME full
brief at `trackCount: 1` passed. The filter is also intermittent — of three
single-track calls with equally innocuous prompts, one passed and two were refused.
So: **generate candidates as N separate `trackCount: 1` calls, and retry a refusal
once with a fresh idempotencyKey before touching a single word.** Rewriting the
brief in response to a refusal that had nothing to do with the brief is how a run
loses its derived music and ships wallpaper. Refusals are free; retries are cheap.

Mechanics: `generate_project_audio` via `search_capabilities` with the master's
projectId; VO text = `audio.vo_script_for_post`, voice/language from `audio.vo_tone`.

## 6. Surgical edit, when QA demands one (paid, ~21 credits)

Cut the bad shot on true scene-detect boundaries (Omni caps source at 10s),
upload it, then `generate_video` with `modelType: "google"`, `googleModel:
"gemini-omni-flash-preview"`, `googleMode: "edit"`, `sourceVideoUrl`, and a
prompt structured as edit goal / sole master / edit scope / content to preserve /
timeline inheritance. Splice back BY FRAME NUMBER and prove nothing else moved
(PSNR vs the previous cut; only the replaced range may score under ~45dB).

**6b. Omni REDRAWS more than asked — composite back only the region.** An
upper-half bottle fix also redrew and simplified the LABEL despite an explicit
do-not-modify. The fix that shipped: a feathered mask (PIL rectangle +
GaussianBlur ~22px) over only the intended region, `alphamerge` + `overlay` of
Omni's frames onto the originals. This is the still-image composite rule applied
to video; it works because Omni inherits the camera, so the regions stay aligned.

**6c. The FREE retime rescue (before paying for a retake).** A beat that rendered
sleepy can often be rebuilt from frames that already exist. Measured recipe: pull
the beat's LIVE material (including unused frames from an alternate take of the
same prompt), then piecewise-retime inside the fixed slot: real-time action, the
static-ish middle at 1.6-2x fast, the payoff near real time. NEVER slow-motion a
section that is already a hold — slowing a hold manufactures the exact "barely
moves" failure. Force EXACT frame counts on every piece (`fps=24` +
`trim=start_frame/end_frame` + `tpad=stop_mode=clone` for rounding) so the tail
stays frame-locked to the audio. Verify with the per-second motion profile.

**6d. Two takes of one prompt = a per-beat A/B.** If a double render ever exists
(deliberate or from a requeue), QA BOTH per beat and frame-splice the best beats
into one film. Per-beat compliance is stochastic; the composite of two takes
beats either take (measured: hero from take 2 into take 1's body, 17.4 motion vs
4.5).
