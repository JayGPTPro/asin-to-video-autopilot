#!/usr/bin/env python3
"""asin-to-video-autopilot lint: mechanical checks BEFORE any credit moves.

Every check exists because a paid take failed without it. Errors block the run;
warnings print and continue. Usage: python3 lint.py <run_dir>
"""

import json
import re
import sys
from collections import Counter
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

# ── what the LISTING'S OWN WORDS demand of the film ──────────────────────────
# From an outside review, on an Irish china figurine sold as a memorial gift: the run read
# features and missed the meaning. It did not know a shamrock is a luck symbol, it
# did not carry the sympathy occasion that the TITLE states outright, it ignored the
# authenticity backstamp that is the trust asset in heritage china, and it dropped
# the gift box on a product whose whole use is being given. Four misses, one shape:
# a research stage that extracts attributes cannot see intent. These patterns make
# the listing's own words demand a decision in the brief.
SENSITIVE_OCCASION = re.compile(
    r"\b(sympathy|condolence|bereave\w*|memorial|in memory|loss of|passed away|"
    r"funeral|urn|remembrance|grief|grieving|miscarriage|stillbirth|hospice|"
    r"cancer|chemo|get well)\b", re.I)
SYMBOLIC = re.compile(
    r"\b(shamrock|clover|cross|crucifix|angel|hamsa|evil eye|star of david|"
    r"menorah|lotus|infinity|claddagh|celtic knot|tree of life|birthstone|"
    r"anniversary|zodiac|horseshoe|dove|butterfly|guardian)\b", re.I)
PROVENANCE = re.compile(
    r"\b(made in \w+|hand ?painted|hand ?made|handcrafted|artisan|hallmark\w*|"
    r"backstamp|certificate of authenticity|authenticity (?:stamp|mark)|"
    r"heirloom|since \d{4}|family ?owned)\b", re.I)
GIFT_PACKAGING = re.compile(
    r"\b(gift ?box\w*|gift ?ready|gift ?wrapped|presentation box|keepsake box|"
    r"comes in a (?:box|tin|pouch)|ready to gift)\b", re.I)


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

    # ── the listing's own words demand a beat (taste 0) ─────────────
    listing_p = run / "listing.json"
    if not listing_p.exists():
        warnings.append("no listing.json in the run — stage 1 must persist the title and "
                        "bullets, or the brief cannot be checked against what the seller "
                        "actually says the product IS")
    else:
        listing = json.loads(listing_p.read_text())
        blob = " ".join([str(listing.get("title", ""))] +
                        [str(b) for b in (listing.get("bullets") or [])] +
                        [str(listing.get("description", ""))])

        hit = SENSITIVE_OCCASION.search(blob)
        if hit:
            occ = brief.get("occasion") or {}
            if not occ.get("sensitive"):
                errors.append(
                    f"the listing says '{hit.group(0)}' — this is a SENSITIVE-OCCASION "
                    f"product (sympathy, memorial, illness). Set brief.occasion "
                    f"{{sensitive: true, what: ..., handling: ...}} and read taste.md 0. "
                    f"A cheerful film on a bereavement gift is the one failure that "
                    f"cannot be fixed after it ships")
            elif brief.get("register") != "calm":
                errors.append(f"sensitive occasion ('{hit.group(0)}') with register "
                              f"'{brief.get('register')}' — the register is calm, and the "
                              f"cast does not laugh, cheer or celebrate")
            elif (brief.get("mood") or {}).get("band") == "BRIGHT_EVERYDAY" \
                    and not (occ.get("handling") or "").strip():
                errors.append("sensitive occasion in a BRIGHT_EVERYDAY band with no written "
                              "handling note — say in one line why the daylight is right here")

        hit = SYMBOLIC.search(blob)
        if hit and not (brief.get("symbols") or []):
            errors.append(
                f"the listing names '{hit.group(0)}', which carries MEANING a viewer reads "
                f"before they read the product. Set brief.symbols [{{symbol, means, beat}}] "
                f"— what it is, what it signifies, and which beat shows it whole. A symbol "
                f"cropped in half is worse than a symbol absent")

        hit = PROVENANCE.search(blob)
        if hit and not (brief.get("provenance") or "").strip():
            errors.append(
                f"the listing claims '{hit.group(0)}' — provenance is the trust asset in "
                f"this kind of product, and it has a PICTURE (a stamp, a mark, a signature, "
                f"a hand at work). Set brief.provenance naming the beat that shows it")

        hit = GIFT_PACKAGING.search(blob)
        if hit and not (brief.get("packaging_beat") or "").strip():
            errors.append(
                f"the listing says '{hit.group(0)}' — for a gift, the box IS part of the "
                f"product and the reference sheets exclude packaging by default. Set "
                f"brief.packaging_beat naming the beat where the box appears")

    # ── rhythm: a uniform grid is the boring film (taste 7a) ────────
    # Measured on a baking-sheet film: a 4/6/4/4/4/4/4 plan came back as seven shots
    # between 3.79s and 4.75s and read as a slideshow. The damage spread: the
    # music brief derives tempo from the cut rhythm, so the same flat grid wrote
    # itself a 60 BPM bed. Every other check passed.
    plan_secs = [s.get("seconds") for s in shots
                 if isinstance(s.get("seconds"), (int, float)) and s.get("seconds") > 0]
    if len(plan_secs) >= 5:
        repeated = sorted(n for n, c in Counter(plan_secs).items() if c > 2)
        if repeated:
            errors.append(f"shot rhythm: {repeated} used more than twice — at most two "
                          "shots share a length (taste 7a)")
        if not any(x <= 3 for x in plan_secs):
            errors.append("shot rhythm: no accent beat — the plan needs at least one "
                          "shot of 2 or 3 seconds")
        if not any(x >= 5 for x in plan_secs):
            errors.append("shot rhythm: no held beat — the plan needs at least one shot "
                          "of 5 seconds or more")
        if max(plan_secs) / min(plan_secs) < 2.0:
            errors.append(f"shot rhythm: longest/shortest is "
                          f"{max(plan_secs) / min(plan_secs):.2f}, under 2.0. Seedance "
                          "compresses the spread it is given, so plan wider than the "
                          "rhythm you want to watch")

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

    # ── hook/close mirror ───────────────────────────────────────────
    # The strongest close is IDENTICAL FRAMING with the state inverted (same
    # lens, same seat, same posture, problem gone). A different shot size is
    # legal (a reversed move mirrors too) but is usually the weaker film.
    hook = next((x for x in shots if x.get("slot") == "hook"), None)
    close = next((x for x in shots if x.get("slot") == "close"), None)
    if hook and close:
        hs = ((hook.get("camera") or {}).get("size") or "").strip().upper()
        cs = ((close.get("camera") or {}).get("size") or "").strip().upper()
        hook_has_people = (hook.get("people") or {}).get("present")
        if hs and cs and hs != cs and hook_has_people:
            warnings.append(
                f"hook is {hs} and close is {cs}: with a person in the hook, the "
                f"strongest close is the SAME framing with the state inverted "
                f"(same seat, same posture, problem gone) — taste.md §2")

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


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(1)
    errs, _ = lint(sys.argv[1] if len(sys.argv) > 1 else ".")
    sys.exit(1 if errs else 0)
