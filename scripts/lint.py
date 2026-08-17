#!/usr/bin/env python3
"""asin-to-video-autopilot lint: mechanical checks BEFORE any credit moves.

Every check exists because a paid take failed without it. Errors block the run;
warnings print and continue. Usage: python3 lint.py <run_dir>
"""

import json
import re
import sys
from pathlib import Path

SLOTS = ["hook", "hero", "use1", "use2", "use3", "use4", "close"]
MOODS = {"BRIGHT_EVERYDAY": (90, 140), "WARM_LAMPLIT": (55, 90), "MOODY_NIGHT": (25, 55)}
SLOW_WORDS = re.compile(r"\b(slowly|slow|unhurried|leisurely|lingers?|drifts?)\b", re.I)
# Loose shine language is how glitter artifacts get invited (measured: "catching the
# lamp in moving bands of shine" put sparkles in a woman's hair). Shine must be a
# surface property (glossy, sheen, gleam ON something), never free-floating light.
SPARKLE_BAIT = re.compile(r"\bcatch(?:es|ing)? the (?:\w+ ){0,2}(?:light|lamp|sun)\b|shimmer\w*|sparkl(?!ing\s+(?:water|wine|juice|cider|lemonade))\w*|glitter\w*|dancing light", re.I)
DESIGN = re.compile(r"#[0-9a-fA-F]{6}\b|\bfonts?\b|\btypefaces?\b|\bpantone\b|\bcolou?r palette\b", re.I)
NUMBER_WORDS = r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)"
# A group beat that implies SIMULTANEOUS handlers renders SEVERAL products
# (measured: "the football snaps around it ... quick low passes" rendered two
# footballs at once past an explicit uniqueness line and a no-second-ball line).
# Verb set = the true throw/pass class only; "goes"/"moves" are ordinary
# locomotion and false-positive on a person carrying the product around a room.
# Person words match plurals and the bare "circle" — the measured sentence was
# "snaps around the circle, quick low hand-offs between friends" and the old
# singular-only, "circle of"-only pattern missed it (adversarial review, 17.8).
DISTRIBUTION = re.compile(
    r"\b(?:snaps?|passes?|pass|flies|fly|whips?|zips?|bounces?|toss(?:es)?)\s+"
    r"(?:it\s+|around|between|among|across)"
    r"|\bto\s+(?:the\s+)?\w+\s+to\s+(?:the\s+)?\w+\b", re.I)
PERSON_WORDS = re.compile(
    r"\b(?:man|men|woman|women|boys?|girls?|kids?|teens?|friends?|players?|"
    r"brothers?|sisters?|father|mother|guys?|everyone|group|team|circle|"
    r"the four|the three)\b", re.I)
SINGLE_OBJECT = re.compile(r"same single|one object|never two|hand to hand|one continuous path", re.I)


def lint(run_dir):
    run = Path(run_dir)
    brief = json.loads((run / "brief.json").read_text())
    plan = json.loads((run / "shotplan.json").read_text())
    shots = plan.get("shots") or []
    errors, warnings = [], []

    # ── the argument ────────────────────────────────────────────────
    if not (brief.get("angle") or "").strip():
        errors.append("brief.angle is empty — the one sentence the film argues is the film")
    if len((brief.get("angle") or "").split(".")) > 3:
        warnings.append("angle reads like more than one sentence — two angles is two videos")
    if brief.get("register") not in ("energy", "desire", "calm"):
        errors.append("register must be energy / desire / calm — choosing it by accident "
                      "is how a correct film comes out boring")

    # ── mood, declared in numbers ───────────────────────────────────
    mood = brief.get("mood") or {}
    band = mood.get("band")
    if band not in MOODS:
        errors.append(f"mood.band must be one of {list(MOODS)} with its luminance range — "
                      "an undeclared mood lets the model choose night")
    else:
        if band == "MOODY_NIGHT" and not (mood.get("reason") or "").strip():
            errors.append("MOODY_NIGHT needs a written reason; it is never a default")
        # ONE source of truth for the band's numbers. Measured: a brief carried
        # the range under a different key, QA silently fell back to WARM_LAMPLIT
        # and reported a correct bright film as OUT OF BAND at lum 163.
        declared = mood.get("lum_range") or mood.get("target_luminance")
        if declared is None:
            errors.append(f"mood.lum_range missing — set it to {list(MOODS[band])} "
                          f"(the {band} band). QA refuses to guess")
        elif list(declared) != list(MOODS[band]):
            errors.append(f"mood.lum_range {list(declared)} contradicts band {band} "
                          f"{list(MOODS[band])} — one line of truth, fix the range or the band")
        elif "lum_range" not in mood:
            warnings.append("mood range is under 'target_luminance' — rename to "
                            "'lum_range' (QA accepts the alias but the canonical key wins)")

    # ── the template ────────────────────────────────────────────────
    got = [s.get("slot") for s in shots]
    for slot in SLOTS:
        if slot not in got:
            errors.append(f"template beat '{slot}' is missing")
    if [s for s in got if s in SLOTS] != [s for s in SLOTS if s in got]:
        errors.append("beats are out of template order — the compiled timeline follows "
                      "the shot list")
    sig = brief.get("signature_shot") or {}
    if not (sig.get("move") or "").strip():
        errors.append("no signature_shot in the brief — every film is built around one "
                      "impossible camera move")
    elif (sig.get("beat") or "hero") == "hook":
        errors.append("the signature shot goes on the hero beat, not the hook")

    # ── beats ───────────────────────────────────────────────────────
    noun = (brief.get("product_noun") or "").strip()
    count_re = re.compile(rf"\b{NUMBER_WORDS}\s+(?:\w+\s+)?{re.escape(noun)}s?\b", re.I) if noun else None
    face_beats = reaction = 0
    for s in shots:
        sid = s.get("id") or s.get("slot")
        action = s.get("action") or ""
        secs = s.get("seconds")
        if not isinstance(secs, (int, float)) or secs != int(secs) or secs <= 0:
            errors.append(f"{sid}: seconds must be a positive whole number (timecodes truncate)")
        if s.get("vo_line"):
            errors.append(f"{sid}: carries a vo_line — voiceover is a POST layer on the "
                          "locked cut, keep the script in audio.vo_script_for_post")
        if count_re and count_re.search(action):
            errors.append(f"{sid}: rests on a countable row of {noun}s — Seedance cannot "
                          "count (measured: a five-piece set rendered four, four times). "
                          "Show a stack, a pile, or one hero unit")
        # Multi-handler group beat: several people + a distribution verb on the
        # product = an instruction to render several products, whatever the
        # uniqueness line says. Measured: two footballs at once, severity class 1.
        if noun and noun.lower() in action.lower() and DISTRIBUTION.search(action) \
                and len(PERSON_WORDS.findall(action)) >= 2 \
                and not SINGLE_OBJECT.search(action):
            errors.append(f"{sid}: a group beat distributes the {noun} among several "
                          "people — Seedance renders several. Choreograph ONE object's "
                          "relay: 'the same single {noun} goes from her hands to his, "
                          "one object the whole time, never two in the air'")
        people = s.get("people") or {}
        if people.get("present") and people.get("face_visible", True):
            face_beats += 1
            if re.search(r"\b(eyes?|smiles?|grins?|leans? in|laughs?|gasps?|eyebrows?)\b",
                         action, re.I):
                reaction += 1
        for m in set(x.group(0).lower() for x in SPARKLE_BAIT.finditer(action)):
            warnings.append(f"{sid}: shine written as free-floating light ('{m}') — "
                            "this is how glitter artifacts get into hair and fabric. "
                            "Write shine as a surface property: glossy, a sheen, a gleam ON the thing")
        pace_text = f"{action} {(s.get('camera') or {}).get('move', '')}"
        # "no slow motion" is the PACE INSTRUCTION, not a slow-word.
        pace_text = re.sub(r"\bno slow motion\b", "", pace_text, flags=re.I)
        for w in set(m.group(0).lower() for m in SLOW_WORDS.finditer(pace_text)):
            if s.get("slot") != "close":
                warnings.append(f"{sid}: slow-word '{w}' outside the closing held beat — "
                                "the model renders exactly the tempo you describe")
    if face_beats == 0:
        errors.append("no beat shows a visible face — faces are the model's strength and "
                      "the emotion carrier; below-shoulders needs a written reason")
    if reaction == 0:
        warnings.append("no beat has a facial REACTION as a physical event — emotion "
                        "carried as adjectives does not render")

    # ── end states ──────────────────────────────────────────────────
    for slot in ("hero", "close"):
        s = next((x for x in shots if x.get("slot") == slot), None)
        if s is not None and not (s.get("end_state") or "").strip():
            errors.append(f"{slot}: no end_state — the beats the film cannot lose declare "
                          "what is visible when they end")

    # ── cast ────────────────────────────────────────────────────────
    anyone = any((s.get("people") or {}).get("present") for s in shots)
    cast = brief.get("cast") or []
    if anyone and not cast:
        errors.append("people appear and the brief declares no cast — nothing holds the "
                      "same person together between beats")
    for c in cast:
        if not (c.get("wardrobe") or "").strip():
            errors.append(f"cast '{c.get('role')}': no named wardrobe — 'keep wardrobe "
                          "identical' cannot hold a wardrobe nobody specified")

    # ── references ──────────────────────────────────────────────────
    refs = brief.get("references") or []
    if not any(r.get("kind") == "product" for r in refs):
        errors.append("no product reference in the pack")
    products = [r for r in refs if r.get("kind") == "product"]
    if len(products) > 1:
        for r in products:
            if "same single" not in (r.get("role") or ""):
                errors.append("multiple product references must each read as a view of "
                              "'the same single <noun>' — the official one-object rule")
            break
    for r in refs:
        role = (r.get("role") or "")
        if r.get("kind") == "video" and "do not use" not in role.lower():
            errors.append("a video reference has no 'Do not use …' clause — a reference "
                          "donates the objects inside it (measured leaks)")
        if r.get("kind") not in ("product",) and not r.get("serves"):
            warnings.append(f"reference '{role[:40]}' has no serves list — it becomes a "
                            "film-wide reference by accident")
        if role.rstrip().endswith("."):
            warnings.append(f"reference role '{role[:40]}' ends with a period — the "
                            "composer adds one, this prints '..'")
    if len(refs) > 8:
        warnings.append(f"{len(refs)} references — 5 focused measurably beat 10 diluted")

    # ── the generated pass is diegetic-only ─────────────────────────
    if ((brief.get("audio") or {}).get("music_direction") or "").strip():
        errors.append("audio.music_direction is set — music is a POST layer; the "
                      "generated pass is diegetic sound only")

    # ── design silence ──────────────────────────────────────────────
    blob = " ".join(str(s.get(k, "")) for s in shots for k in ("action", "setting"))
    blob += " " + str(brief.get("global_look", ""))
    if DESIGN.search(blob):
        errors.append("the plan dictates the look (hex/font/palette) — the overlay layer "
                      "owns design; the prompt stays design-silent")

    print(f"lint: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print(f"  ERROR  {e}")
    for w in warnings:
        print(f"  warn   {w}")
    return errors, warnings


if __name__ == "__main__":
    errs, _ = lint(sys.argv[1] if len(sys.argv) > 1 else ".")
    sys.exit(1 if errs else 0)
