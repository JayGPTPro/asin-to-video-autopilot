# Genrupt flow: the exact calls, in order, with the traps

All via the Genrupt MCP. Prices move — read them live, never from this file.

## 0. Balance + live prices (free)

`get_credit_balance_and_costs` with two `video_generation` presets:
`seedance_2_5_reference` at 720p x film seconds (master) and 480p x 4s (probe).
Record `estimatedCustomerCostUSD` for both into the run state; every later money
line quotes THESE numbers.

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
**never re-queue before 60 minutes have passed since queue time.** A premature requeue
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
Build it from three film facts: the register (energy/desire/calm), the cut rhythm
(average beat length in seconds → name a tempo whose bar lands on it: 4s beats →
60 or 120 BPM so musical phrases land near cuts), and the film's ENERGY CURVE named
beat by beat ("rises with the hook, suspends and empties out during the frozen hero
beat, grooves through the four use beats, resolves warm on the close"). Write that
curve INTO the promptRequest with rough second marks. A bed that ignores the film is
wallpaper; wallpaper is what failed.

**5a-bis. AUDIO IS UNPRICEABLE AND EXPENSIVE. Budget it before you fire it.**
`get_credit_balance_and_costs` has no operation key for audio (verified), so
`generate_project_audio` gives no preview. Measured: four tracks in one run came to
USD 18.42 — more than the master render, and enough to blow a USD 15 cap by 80%.
Rules: ONE music + ONE voiceover by default; reserve `2 x audio_track_usd` from the
cap before generating; if it does not fit, skip audio and ship the diegetic cut with
a note. Alternates for the taste gate are free re-mixes of the same two tracks.

**5b. Pick between MIXES, not between generations.** One generation each; the choice happens in
the mix (music forward, music off, voice shifted), which costs nothing. If a second
music generation is genuinely needed, it must fit the reserved audio budget. For the
track you have: extract the RMS envelope
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

**The music FLOOR (measured over-correction).** After "the music is boring" the next
mix buried it at -16dB under and failed review as "I hear no music at all". The bed
sits 8-10dB under the voice, gently ducked — present in every no-speech window.
Verify mechanically: in a speech-free second, the mix's RMS must be well above the
SFX track alone (the music is contributing), and by ear it reads as real music.

Measured failure mode: continuous narration DRIFTS — speech runs ~2.5s per idea while
beats run 4s, so by mid-film every line lands one beat early ("your skin" over the
hair shot). Two rules that fix it:
- **Script budget: spoken words fill at most ~80% of the runtime**, with air written
  in (especially around the freeze and the close). A wall-to-wall script cannot stay
  in sync and reads as "does not flow".
- **Place the VO as SEGMENTS, not one file**: cut the track at measured word
  boundaries and delay each line onto its beat (ffmpeg atrim + adelay). A line may
  bridge a cut by a few tenths — that is normal ad grammar — but a line a whole beat
  away is a failure. Cutting a redundant line (a tagline the label already carries)
  to buy air is always allowed.

**5d. The mix hierarchy: SFX are the realism layer.** The diegetic track is what
makes the picture feel real, and it is the layer that cannot be rebuilt — it sits
FORWARD (target around -22 LUFS contribution), music UNDER it (-28 to -30 under
speech, sidechain-ducked by the VO), VO on top (~-16 integrated). After the mix,
QA per beat: every named `ambience` sound must be audible over the bed at its
moment — a click, a plink and a mist hiss that exist in the track but cannot be
heard did not happen.

**5e. A content-checker refusal never dumbs the brief down.** Change the flagged
word, keep every specific musical instruction. Measured trap: the word "bed" in a
track TITLE drew two refusals, and the retry that also simplified the prompt
produced the generic track that failed review. Fix the word, not the ambition.

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
