#!/usr/bin/env python3
"""Build the run's locked theme.json: base theme + a palette pulled from the
product's own label.

Usage:
  theme_extract.py <label_image> <base_theme.json> <out_theme.json>

The label image must be a PRODUCT-SURFACE-ONLY crop — tighter than the render
plate. Measured: a plate that included the product's splash background handed
the palette to the water (a pool-blue accent from scenery, not the product);
re-cropping to the shell alone fixed it. Crop out every pixel of scenery,
splash, props or backdrop before extracting. The palette comes
from THERE because the product already chose its colors — an overlay that
echoes the label reads as designed; an arbitrary gold reads as a template.

Output = the base theme with FROM_LABEL fields resolved:
  accent    — the label's most saturated distinct color, brightened to read at
              4px height on video (min luminance floor applied)
  ink_dark  — the label's darkest legible color (for text on bright zones)
Every super in the film reads from this one file. That is the theme lock:
mid-film font/color drift becomes structurally impossible.
"""
import sys, json, colorsys
from PIL import Image


def kmeans_palette(img, k=6, iters=12):
    """Tiny dependency-free k-means over RGB pixels. Returns [(r,g,b,share)]."""
    im = img.convert("RGB").resize((96, 96))
    px = list(im.getdata())
    # init: spread over luminance-sorted pixels
    px_sorted = sorted(px, key=lambda p: sum(p))
    centers = [px_sorted[int((i + 0.5) * len(px_sorted) / k)] for i in range(k)]
    for _ in range(iters):
        buckets = [[] for _ in range(k)]
        for p in px:
            d = [sum((a - b) ** 2 for a, b in zip(p, c)) for c in centers]
            buckets[d.index(min(d))].append(p)
        for i, b in enumerate(buckets):
            if b:
                centers[i] = tuple(sum(ch) / len(b) for ch in zip(*b))
    out = []
    for i, b in enumerate(buckets):
        if b:
            r, g, bl = centers[i]
            out.append((int(r), int(g), int(bl), len(b) / len(px)))
    return sorted(out, key=lambda c: -c[3])


def hexc(r, g, b):
    return "#%02X%02X%02X" % (r, g, b)


def pick_accent(palette):
    """Most saturated color with meaningful share; lifted to overlay-legible."""
    best, best_score = None, -1
    for r, g, b, share in palette:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if share < 0.03:
            continue
        score = s * (1 - abs(l - 0.5)) * (0.5 + share)
        if score > best_score:
            best, best_score = (r, g, b), score
    if best is None:  # monochrome label: fall back to a warm neutral
        return "#C9A227"
    h, l, s = colorsys.rgb_to_hls(*[c / 255 for c in best])
    l = max(l, 0.42)          # floor: a 4px rule must read against video
    s = min(max(s, 0.45), 0.85)
    r, g, b = (int(round(c * 255)) for c in colorsys.hls_to_rgb(h, l, s))
    return hexc(r, g, b)


def pick_ink_dark(palette):
    """Darkest color with real share — the label's own 'ink'."""
    cands = [(r, g, b, sh) for r, g, b, sh in palette if sh > 0.05]
    r, g, b, _ = min(cands or palette, key=lambda c: c[0] + c[1] + c[2])
    # clamp so text stays legible on bright zones (not near-black mud)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum > 96:  # label has no dark ink; synthesize one from its hue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        r, g, b = (int(round(c * 255)) for c in colorsys.hls_to_rgb(h, 0.18, min(s, 0.5)))
    return hexc(r, g, b)


def main():
    label_path, base_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    theme = json.load(open(base_path))
    palette = kmeans_palette(Image.open(label_path))
    theme["palette_from_label"] = [
        {"hex": hexc(r, g, b), "share": round(sh, 3)} for r, g, b, sh in palette]
    theme["accent"] = pick_accent(palette)
    theme["ink_dark"] = pick_ink_dark(palette)
    theme["locked"] = True
    json.dump(theme, open(out_path, "w"), indent=2)
    print(f"theme locked: {theme['name']}  accent={theme['accent']}  "
          f"ink_dark={theme['ink_dark']}")
    for c in theme["palette_from_label"]:
        print(f"  label color {c['hex']}  share {c['share']}")


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(1)
    main()
