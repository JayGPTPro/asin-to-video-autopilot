#!/usr/bin/env python3
"""asin-to-video-autopilot composer: brief + shotplan in, one master prompt out.

Self-contained on purpose. Reads brief.json and shotplan.json from the run folder,
writes master-prompt.txt and compile-result.json. Run lint.py FIRST; this refuses
only what cannot compile at all.

Usage: python3 compose.py <run_dir>
"""

import json
import re
import sys
from pathlib import Path

# Measured on a 30s film, same subject, three rounds: ~3,400 chars were obeyed
# beat-for-beat; ~7,500 measurably lost the choreography. Count, not style.
CHARS_OBEYED = 3400
CHARS_LOST = 7500

# A product film is a perfect world CAPTURED, not rendered. Without a capture
# medium and a light logic the model emits gradient-smooth render space. The brief
# overrides this with `capture_block` when the mood needs a different light logic.
DEFAULT_CAPTURE = (
    "Shot on a cinema camera with prime lenses: shallow focus falloff, fine film "
    "grain, controlled highlights, real time, no slow motion unless a beat says so. "
    "Smooth motion-control camera moves, never handheld.")


def sentence(text):
    text = (text or "").strip()
    return text if not text or text[-1] in ".!?" else text + "."


def timecode(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def negative(text):
    text = (text or "").strip().rstrip(".")
    if not text:
        return ""
    first = text.split()[0].lower()
    if first in ("no", "never", "keep", "do", "avoid"):
        return sentence(text)
    if first in ("a", "an", "the", "any", "anything", "anyone", "nothing"):
        return sentence(f"Do not show {text}")
    return sentence(f"No {text}")


def reference_lines(references, when):
    lines = []
    for i, ref in enumerate(references or [], start=1):
        role = (ref.get("role") or "").strip().rstrip(".")
        tag = f"@Image {i}"
        spans = [when[b] for b in ref.get("serves") or [] if b in when]
        at = f" It applies to the shot at {', '.join(spans)}." if spans else ""
        if ref.get("kind") == "product":
            lines.append(f"{tag} defines the product: {role or 'the exact product'}. "
                         "Match it exactly wherever the product appears.")
        else:
            lines.append(f"{tag} defines {role or 'the scene'}.{at}")
    return lines


def cast_lines(cast):
    lines = []
    for c in cast or []:
        bits = [b for b in (f"about {c.get('age_display', '')}".strip(),
                            c.get("gender", ""), c.get("look_notes", "")) if b and b != "about"]
        wardrobe = (c.get("wardrobe") or "").strip().rstrip(".")
        wears = f" They wear {wardrobe}, in every shot they appear." if wardrobe else ""
        role = (c.get("role") or "one person").strip()
        lines.append(f"{role[0].upper() + role[1:]} appears, {', '.join(bits)}.{wears} "
                     "Keep their identity, wardrobe and the scene's layout identical throughout.")
    return lines


def beat_block(shot, start):
    seconds = float(shot["seconds"])
    cam = shot.get("camera") or {}
    size = (cam.get("size") or "MEDIUM").upper()
    move = cam.get("move") or "static shot"
    action = (shot.get("action") or "").strip()
    if not action:
        raise SystemExit(f"ERROR: beat {shot.get('id')} has no action — the shot plan "
                         "is underspecified; fix the plan, do not invent content here")
    parts = [sentence(f"{size}, {move}"), sentence(action)]
    if shot.get("end_state"):
        parts.append(sentence(f"End state: {shot['end_state'].strip().rstrip('.')}"))
    if shot.get("setting"):
        parts.append(sentence(shot["setting"]))
    must_read = shot.get("must_read") or []
    if isinstance(must_read, str):
        must_read = [must_read]
    if must_read:
        parts.append(sentence(f"Keep {', '.join(must_read)} sharp and unchanged"))
    cue = (shot.get("ambience") or "").strip().rstrip(".")
    if cue:
        parts.append(sentence(f"Sound: {cue}"))
    end = start + seconds
    return f"[{timecode(start)}-{timecode(end)}] " + " ".join(parts), end


def compose(run_dir):
    run = Path(run_dir)
    brief = json.loads((run / "brief.json").read_text())
    plan = json.loads((run / "shotplan.json").read_text())
    shots = plan["shots"]

    total = sum(float(s["seconds"]) for s in shots)
    product = brief.get("product_name") or brief.get("asin") or "the product"
    look = brief.get("global_look") or "natural light, one continuous mood"
    capture = brief.get("capture_block") or DEFAULT_CAPTURE
    head = (f"A photorealistic {int(total)} second product film for "
            f"{sentence(product)} {sentence(look)} {capture}")

    clock, beat_lines, when = 0.0, [], {}
    for s in shots:
        start = clock
        block, clock = beat_block(s, clock)
        beat_lines.append(block)
        for key in (s.get("id"), s.get("slot")):
            if key:
                when[key] = f"{timecode(start)}-{timecode(clock)}"

    refs = reference_lines(brief.get("references"), when)
    # Cast continuity lines only when someone is actually on screen: a standing
    # "X appears" instruction over a people-free timeline invites the model to
    # cast them into a shot that never asked for anyone.
    anyone = any((s.get("people") or {}).get("present") for s in shots)
    cast = cast_lines(brief.get("cast")) if anyone else []

    constraints = ["No jump cuts.", "No text overlays, captions or subtitles."]
    noun = (brief.get("product_noun") or "").strip()
    if noun:
        constraints.append(
            f"No other {noun}, and no object like it, exists anywhere in this world; "
            f"the {noun} from the references is the only one, in every scene and "
            "every reflection.")
    # Diegetic-only pass: the two bans are structural, not optional.
    constraints.append("No music, song or score plays anywhere in this film.")
    constraints.append("No voice, narration or dialogue exists in this film; nobody speaks.")
    # The model decorates hair, fabric and liquid with sparkles whenever shine is
    # described loosely (measured artifact, failed review 14.8). Realism films ban
    # particles by default; a brief opts out with allow_particles + a reason.
    if not brief.get("allow_particles"):
        constraints.append("No glitter, sparkles, shimmer particles, lens flares or "
                           "magical light effects appear anywhere.")
    seen = set()
    for f in brief.get("forbidden") or []:
        line = negative(f)
        if line and line.lower() not in seen:
            seen.add(line.lower())
            constraints.append(line)

    sections = [head, ""]
    if refs:
        sections += refs + [""]
    if cast:
        sections += cast + [""]
    sections += beat_lines + ["", " ".join(constraints)]
    prompt = "\n".join(sections).strip()

    beat_chars = sum(len(l) for l in beat_lines)
    density = beat_chars / total if total else 0
    result = {
        "prompt_chars": len(prompt),
        "beat_chars": beat_chars,
        "density_chars_per_sec": round(density, 1),
        "duration_seconds": int(total),
        "over_soft": len(prompt) > CHARS_OBEYED,
        "over_hard": len(prompt) >= CHARS_LOST,
        "settings": {
            "seedanceDuration": int(total),
            "seedanceResolution": brief.get("resolution", "720p"),
            "aspect_ratio": brief.get("aspect_ratio", "16:9"),
            "seedanceGenerateAudio": True,
            "promptEnhancement": "already_enhanced",
        },
    }
    (run / "master-prompt.txt").write_text(prompt + "\n")
    (run / "compile-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"composed: {len(prompt)} chars total, {result['density_chars_per_sec']} "
          f"chars/sec on beats, {int(total)}s of film")
    if result["over_hard"]:
        print(f"REFUSE: past {CHARS_LOST} chars the model measurably drops its own "
              "choreography. Cut a beat.")
        sys.exit(2)
    if result["over_soft"]:
        print(f"warn: past {CHARS_OBEYED} chars the smallest instructions get dropped "
              "first. Prefer cutting a beat over thinning every beat.")
    return result


if __name__ == "__main__":
    compose(sys.argv[1] if len(sys.argv) > 1 else ".")
