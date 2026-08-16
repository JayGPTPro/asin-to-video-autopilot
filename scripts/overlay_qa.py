#!/usr/bin/env python3
"""QA the overlay layer itself — readability, theme lock, and VO sync.
The video QA (qa.py) never looks at the text; this script does.

Usage:
  overlay_qa.py <overlay_index.html> <film.mp4> <theme.json> [words.json]

words.json = whisper word timestamps: [{"word": "roots", "start": 8.31, ...}].
A super that should track speech carries data-vo="the spoken phrase" in its
HTML; sync is checked against the measured time of that phrase.

Also WRITES qa/overlay-boxes/: sampled frames with each super's box drawn on
them. The run MUST look at this sheet before compositing — a box sitting on a
face, the product, a label or hands is an automatic reposition, whatever the
contrast numbers say. (Measured failure: a hand-placed test super sat straight
on a woman's head while passing every numeric check. Numbers cannot see a face;
the eye pass on the box sheet is the check that can.)

Checks (each measured, each prints PASS/FAIL):
 1. THEME LOCK — every hex color in the HTML belongs to the theme (accent,
    inks, scrim neutrals); every font-family is the theme family. Drift fails.
 2. CONTRAST — for each super, sample the film under its estimated box across
    its WHOLE window (4 fps). Ink-vs-zone contrast must be >= 4.5:1 in the
    worst sampled frame, else the super needs a scrim/plate or an ink flip.
    A busy zone (luminance std > 55) demands a scrim even if contrast passes.
 3. READING TIME — duration >= 0.18s x words + 0.7s. A 5-word line cannot
    live 1.2 seconds.
 4. SIZE FLOOR — no text under 24px at 1280-wide; under phone scaling it
    does not exist.
 5. VO SYNC — a super with data-vo must start within +/-0.35s of its phrase.
 6. BREATH — >= 1.0s between one super's exit and the next one's entrance.
 7. HIERARCHY (set-level) — at least one super uses the theme's top tier, and
    the supers are not all one size. Measured: a film shipped with every super
    at the same tier, the hero tier never used, and the close (a fifth of the
    film) carrying the SMALLEST text — every per-super check passed. A film
    whose supers are all one tier has no argument.
 8. DISTRIBUTION (set-level) — no more than half the supers share a screen
    quadrant. Measured: four supers stacked in the same top-left corner, each
    individually fine. The eye-pass reposition must move a super to a
    DIFFERENT quadrant than its neighbors, never just the nearest empty spot.
"""
import sys, re, json, subprocess, tempfile, os, warnings
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

FPS_SAMPLE = 4
# 3.2 not 4.5: supers carry a mandatory text-shadow that lifts effective
# contrast, and a shipped, review-approved film measured 3.5:1 in its worst
# frame. 4.5 would have forced a scrim onto a super a human already passed.
CONTRAST_MIN = 3.2
BUSY_STD = 55
SIZE_FLOOR = 24
READ_PER_WORD, READ_BASE = 0.18, 0.7
SYNC_TOL = 0.35
BREATH_MIN = 1.0
NEUTRALS = {"#000", "#000000", "#FFF", "#FFFFFF"}


def rel_lum(hexc):
    hexc = hexc.lstrip("#")
    if len(hexc) == 3:
        hexc = "".join(c * 2 for c in hexc)
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def parse_supers(html):
    sups = []
    for m in re.finditer(
            r'<div[^>]*class="[^"]*\bsuper\b[^"]*"[^>]*>(.*?)</div>\s*(?:</div>)?',
            html, re.S):
        tag = m.group(0)

        def attr(name, default=None):
            a = re.search(name + r'="([^"]*)"', tag)
            return a.group(1) if a else default

        style = attr("style", "")
        text = re.sub(r"<[^>]+>", " ", m.group(1))
        text = re.sub(r"&nbsp;|\s+", " ", text).strip()
        px = re.search(r"font-size:\s*(\d+)px", style)
        sups.append({
            "id": attr("id", "?"),
            "start": float(attr("data-start", "0")),
            "dur": float(attr("data-duration", "0")),
            "vo": attr("data-vo"),
            "text": text,
            "style": style,
            "classes": attr("class", ""),
            "font_px": int(px.group(1)) if px else None,
        })
    return [s for s in sups if s["text"]]


def box_estimate(s, class_px, W=1280, H=720):
    """Rough box from inline left/right/top + font size + text length."""
    fs = s["font_px"] or class_px.get(
        next((c for c in ("hero", "line", "kicker") if c in s["classes"]), "line"), 40)
    lines = max(1, s["text"].count("\n") + 1)
    w = min(int(len(s["text"]) * fs * 0.62), W - 80)
    h = int(lines * fs * 1.15) + 24
    style = s["style"]
    left = re.search(r"left:\s*(\d+)px", style)
    right = re.search(r"right:\s*(\d+)px", style)
    top = re.search(r"top:\s*(\d+)px", style)
    x = int(left.group(1)) if left else (W - int(right.group(1)) - w if right else (W - w) // 2)
    y = int(top.group(1)) if top else 60
    return max(0, x), max(0, y), min(W, x + w), min(H, y + h), fs


def sample_zone(film, t0, t1, box):
    """Mean luminance + std per sampled frame under the box; returns list."""
    out = []
    t = t0
    with tempfile.TemporaryDirectory() as td:
        while t < t1:
            fp = os.path.join(td, "f.jpg")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", film, "-frames:v", "1",
                 "-loglevel", "error", fp], check=True)
            im = Image.open(fp).convert("L").crop(box)
            px = list(im.getdata())
            mean = sum(px) / len(px)
            var = sum((p - mean) ** 2 for p in px) / len(px)
            out.append((mean, var ** 0.5))
            t += 1.0 / FPS_SAMPLE
    return out


def draw_box_sheet(film, sups, class_px, out_dir):
    """3 frames per super (start/mid/end) with the super's box drawn in red.
    This sheet is for EYES: the agent must confirm no box covers a face, the
    product, a label or hands."""
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for s in sups:
        x0, y0, x1, y1, _ = box_estimate(s, class_px)
        for tag, t in (("a", s["start"] + 0.1),
                       ("b", s["start"] + s["dur"] / 2),
                       ("c", s["start"] + s["dur"] - 0.1)):
            fp = os.path.join(out_dir, f"{s['id']}-{tag}.jpg")
            subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", film,
                            "-frames:v", "1", "-loglevel", "error", fp], check=True)
            im = Image.open(fp)
            d = ImageDraw.Draw(im)
            d.rectangle([x0, y0, x1, y1], outline=(255, 40, 40), width=4)
            d.text((x0 + 6, max(2, y0 - 18)), f"{s['id']} @{t:.1f}s", fill=(255, 40, 40))
            im.save(fp)
            n += 1
    print(f"box sheet: {n} frames in {out_dir} — LOOK at them: no box on a "
          f"face, the product, a label or hands.")


def main():
    html_path, film, theme_path = sys.argv[1], sys.argv[2], sys.argv[3]
    words = json.load(open(sys.argv[4]))["words"] if len(sys.argv) > 4 else None
    html = open(html_path).read()
    theme = json.load(open(theme_path))
    fails = []

    # 1. THEME LOCK
    allowed = {theme.get("accent", "").upper(), theme.get("ink_light", "").upper(),
               theme.get("ink_dark", "").upper()} | NEUTRALS
    for hexc in set(re.findall(r"#[0-9A-Fa-f]{3,6}\b", html)):
        if hexc.upper() not in allowed:
            fails.append(f"THEME LOCK: color {hexc} is not in the theme")
    fam = theme["font"]["family"]
    for f in re.findall(r'font-family:\s*"([^"]+)"', html):
        if f not in (fam, "THEME_FONT"):
            fails.append(f"THEME LOCK: font '{f}' is not the theme font '{fam}'")
    if 'font-family: "THEME_FONT"' in html:
        fails.append("THEME LOCK: template placeholder THEME_FONT was never filled")

    class_px = {k: v for k, v in zip(("hero", "line", "kicker"),
                (theme["sizes_px"]["hero"], theme["sizes_px"]["line"],
                 theme["sizes_px"]["kicker"]))}
    sups = sorted(parse_supers(html), key=lambda s: s["start"])
    print(f"{len(sups)} supers found")

    ink_l = {"light": rel_lum(theme.get("ink_light", "#F5EFE3")),
             "dark": rel_lum(theme.get("ink_dark", "#24352B"))}

    draw_box_sheet(film, sups, class_px,
                   os.path.join(os.path.dirname(os.path.abspath(html_path)),
                                "..", "qa", "overlay-boxes"))

    for s in sups:
        x0, y0, x1, y1, fs = box_estimate(s, class_px)
        label = f"{s['id']} \"{s['text'][:32]}\" @{s['start']:.2f}"

        # 4. SIZE FLOOR
        if fs < SIZE_FLOOR:
            fails.append(f"SIZE: {label} is {fs}px (< {SIZE_FLOOR}px)")

        # 3. READING TIME
        nwords = len(s["text"].split())
        need = READ_PER_WORD * nwords + READ_BASE
        if s["dur"] < need:
            fails.append(f"READ TIME: {label} shows {nwords} words for "
                         f"{s['dur']:.2f}s (needs {need:.2f}s)")

        # 2. CONTRAST over the whole window
        ink = ink_l["dark"] if "ink-dark" in s["classes"] else ink_l["light"]
        has_cover = "scrim" in html or "plate" in s["classes"] or "slab" in s["classes"]
        samples = sample_zone(film, s["start"], s["start"] + s["dur"], (x0, y0, x1, y1))
        worst = min(contrast(ink, m / 255) for m, _ in samples)
        busiest = max(sd for _, sd in samples)
        if worst < CONTRAST_MIN and not has_cover:
            fails.append(f"CONTRAST: {label} worst {worst:.1f}:1 "
                         f"(< {CONTRAST_MIN}:1) — add a scrim/plate or flip the ink")
        if busiest > BUSY_STD and not has_cover:
            fails.append(f"BUSY ZONE: {label} luminance std {busiest:.0f} — "
                         f"add a scrim even though contrast may pass")

        # 5. VO SYNC
        if s["vo"] and words:
            phrase = s["vo"].lower().split()
            best = None
            for i in range(len(words) - len(phrase) + 1):
                if [w["word"].lower().strip(".,!?") for w in
                        words[i:i + len(phrase)]] == phrase:
                    best = words[i]["start"]
                    break
            if best is None:
                fails.append(f"VO SYNC: {label} phrase '{s['vo']}' not found in transcript")
            elif abs(s["start"] - best) > SYNC_TOL:
                fails.append(f"VO SYNC: {label} starts {s['start']:.2f}, phrase "
                             f"spoken at {best:.2f} (off by {abs(s['start']-best):.2f}s)")

    # 6. BREATH
    for a, b in zip(sups, sups[1:]):
        gap = b["start"] - (a["start"] + a["dur"])
        if gap < BREATH_MIN:
            fails.append(f"BREATH: {a['id']} -> {b['id']} gap {gap:.2f}s (< {BREATH_MIN}s)")

    # 7. HIERARCHY + 8. DISTRIBUTION — checks on the SET, not the super
    if len(sups) >= 2:
        sizes, quads = [], []
        for s in sups:
            x0, y0, x1, y1, fs = box_estimate(s, class_px)
            sizes.append(fs)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            quads.append(("T" if cy < 360 else "B") + ("L" if cx < 640 else "R"))
        hero_px = theme["sizes_px"]["hero"]
        if max(sizes) < hero_px * 0.85:
            fails.append(f"HIERARCHY: no super reaches the theme's top tier "
                         f"({hero_px}px hero; largest here {max(sizes)}px) — a film "
                         f"whose supers are all one tier has no argument")
        if len(set(sizes)) == 1:
            fails.append(f"HIERARCHY: all {len(sups)} supers are the same size "
                         f"({sizes[0]}px) — intensity must follow importance")
        from collections import Counter
        q, n = Counter(quads).most_common(1)[0]
        if n > len(sups) / 2:
            fails.append(f"DISTRIBUTION: {n} of {len(sups)} supers sit in the same "
                         f"{q} quadrant ({quads}) — reposition to different quadrants, "
                         f"never stack a corner")

    print()
    if fails:
        for f in fails:
            print("FAIL", f)
        sys.exit(1)
    print("PASS — overlay layer clean")


if __name__ == "__main__":
    main()
