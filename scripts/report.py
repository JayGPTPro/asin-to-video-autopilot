#!/usr/bin/env python3
"""Run report: the film, the decisions, the measurements and every dollar,
as one self-contained HTML page.

    python3 report.py <run_dir>

Reads brief.json (incl. decision_log), compile-result.json, run-state.json,
theme.json, qa/ frames, and embeds players for what it finds on disk:
  out/FINAL*.mp4          — the delivered film (hero player)
  out/ALT*.mp4            — audio/edit alternates, presented as a choice
  out/style-card*.mp4     — the 6s overlay style card
Videos are LINKED relative (not base64) so the report stays small; keep it in
the run folder next to out/. The report is the user's receipt AND their
marketing asset: "this is how the AI directed my product film".
"""

import json
import sys
from base64 import b64encode
from html import escape
from pathlib import Path

# Attribution travels with the artifact. Every report a user shows a client is
# also the only marketing this skill ever does — so the credit is a signature,
# never a banner: one byline, one quiet footer, no price, no urgency, nothing
# that would make a person LESS willing to forward the page.
SKILL_VERSION = "1.1"
MAKER = "Jay GPT Pro"
MAKER_URL = "https://jaygptpro.com/video-autopilot/"
BOOTCAMP_URL = "https://jaygptpro.com/wonka"


def img_tag(p, w=220):
    data = b64encode(p.read_bytes()).decode()
    return f'<img src="data:image/jpeg;base64,{data}" style="width:{w}px;border-radius:8px;margin:4px">'


def video_tag(p, run, w=820):
    rel = p.relative_to(run)
    return (f'<video controls preload="metadata" style="width:{w}px;max-width:100%;'
            f'border-radius:10px;background:#000" src="{rel}"></video>')


def spend_rows(state):
    """spend_lines: [{"what": "master 30s", "usd": 8.64}, ...] — the sum of cost
    previews, per the money contract. Falls back to spent_usd alone."""
    lines = state.get("spend_lines") or []
    rows = "".join(
        f"<tr><td>{escape(str(l.get('what', '')))}</td>"
        f"<td style='text-align:right'>USD {float(l.get('usd', 0)):.2f}</td></tr>"
        for l in lines)
    total = sum(float(l.get("usd", 0)) for l in lines) if lines \
        else state.get("spent_usd", "?")
    cap = state.get("cost_cap_usd") or state.get("cap_usd", "?")
    rows += (f"<tr style='font-weight:700;border-top:2px solid #b8860b'>"
             f"<td>Total (cap USD {cap})</td>"
             f"<td style='text-align:right'>USD {total if isinstance(total, str) else f'{total:.2f}'}</td></tr>")
    return rows


def main(run_dir):
    run = Path(run_dir)
    brief = json.loads((run / "brief.json").read_text())
    compile_result = json.loads((run / "compile-result.json").read_text()) \
        if (run / "compile-result.json").exists() else {}
    state = json.loads((run / "run-state.json").read_text()) \
        if (run / "run-state.json").exists() else {}
    theme = json.loads((run / "theme.json").read_text()) \
        if (run / "theme.json").exists() else {}

    out_dir = run / "out"
    finals = sorted(out_dir.glob("FINAL*.mp4")) if out_dir.exists() else []
    extras_dir = out_dir / "extras"
    alts = sorted(extras_dir.glob("ALT*.mp4")) if extras_dir.exists() else []
    cards = sorted(extras_dir.glob("style-card*.mp4")) if extras_dir.exists() else []

    # THE DELIVERY LAYOUT (SKILL.md stage 13): out/ root holds exactly ONE mp4,
    # the final. Alternates and cards live in out/extras/, intermediates in
    # work/. A user opening the folder must never have to guess which file is
    # the film — that guess shipped once and the feedback was "which one is
    # the real one?"
    stray = [p for p in (out_dir.glob("*.mp4") if out_dir.exists() else [])
             if p not in finals]
    problems = []
    if len(finals) != 1:
        problems.append(f"expected exactly 1 FINAL-*.mp4 at out/ root, found "
                        f"{len(finals)}: {[f.name for f in finals]}")
    if stray:
        problems.append(f"non-FINAL mp4s at out/ root (move to out/extras/ or "
                        f"work/): {[p.name for p in stray]}")
    if problems:
        print("DELIVERY LAYOUT VIOLATION — fix out/ before writing the report:")
        for x in problems:
            print("  -", x)
        sys.exit(1)

    hero_html = video_tag(finals[0], run) if finals else "<p>No final film yet.</p>"
    alts_html = "".join(
        f"<div style='margin:10px 0'><p style='margin:2px 0;font-weight:600'>"
        f"{escape(p.stem)}</p>{video_tag(p, run, 480)}</div>" for p in alts)
    card_html = "".join(video_tag(p, run, 480) for p in cards)

    theme_html = ""
    if theme:
        sw = "".join(
            f"<span style='display:inline-block;width:44px;height:44px;border-radius:8px;"
            f"background:{escape(c)};margin-right:6px;vertical-align:middle'></span>"
            for c in [theme.get("accent", ""), theme.get("ink_dark", ""),
                      theme.get("ink_light", "")] if c and c != "FROM_LABEL")
        theme_html = (f"<p><b>{escape(theme.get('name', ''))}</b> — "
                      f"{escape(theme.get('font', {}).get('family', ''))}. "
                      f"Palette pulled from the product's own label: {sw}</p>")

    rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{escape(str(v))}</td></tr>"
        for k, v in [
            ("Product", brief.get("product_name", "")),
            ("ASIN", brief.get("asin", "")),
            ("The film's one argument", brief.get("angle", "")),
            ("Mood", f"{(brief.get('mood') or {}).get('band')} "
                     f"(target luminance {(brief.get('mood') or {}).get('lum_range')})"),
            ("Signature shot", (brief.get("signature_shot") or {}).get("move", "")),
            ("Final image", brief.get("final_image", "")),
            ("Variant", state.get("variant_of",
                "first run on this ASIN") if state.get("variant_axes") is None
                else f"differs from previous run on: {', '.join(state['variant_axes'])}"),
            ("Prompt size", f"{compile_result.get('prompt_chars', '?')} chars, "
                            f"{compile_result.get('density_chars_per_sec', '?')} chars/sec"),
        ])

    decisions = "".join(f"<li>{escape(d)}</li>" for d in brief.get("decision_log", []))
    qa_frames = sorted((run / "qa").glob("*.jpg")) if (run / "qa").exists() else []
    frames_html = "".join(img_tag(f) for f in qa_frames[:12])

    unfixed = state.get("unfixed_findings") or []
    unfixed_html = ("".join(f"<li>{escape(str(u))}</li>" for u in unfixed)
                    if unfixed else "<li>Nothing — QA closed clean.</li>")

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Run report: {escape(brief.get('asin', ''))}</title>
<style>body{{font-family:-apple-system,Arial,sans-serif;max-width:900px;margin:32px auto;
padding:0 16px;line-height:1.6;color:#1d1a16;background:#faf6ef}}
h1{{font-size:1.5rem}}h2{{font-size:1.1rem;border-bottom:2px solid #b8860b;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%}}td{{border:1px solid #e8e0d2;padding:6px 10px;
vertical-align:top}}td:first-child{{font-weight:600;width:210px}}
.byline{{color:#6b6459;font-size:.95rem;margin:-6px 0 22px}}
footer{{margin-top:44px;padding-top:16px;border-top:1px solid #e8e0d2;
color:#6b6459;font-size:.88rem}}
footer p{{margin:0 0 6px}}
a{{color:#8A5A2B}}</style></head><body>
<h1>asin-to-video-autopilot run report</h1>
<p class="byline">Made with <b>asin-to-video-autopilot</b> v{SKILL_VERSION} — a skill
of <b>Wonka</b>, the creative AI employee built by
<a href="{MAKER_URL}">{MAKER}</a>.</p>
<h2>The film</h2>{hero_html}
<table style="margin-top:14px">{rows}</table>
<h2>Overlay theme</h2>{theme_html or '<p>No theme.json in this run.</p>'}{card_html}
{f'<h2>Audio alternates — a listening choice</h2>{alts_html}' if alts_html else ''}
<h2>Decisions the autopilot made, and why</h2><ul>{decisions}</ul>
<h2>What you paid for</h2><table>{spend_rows(state)}</table>
<h2>Known limits of this delivery</h2><ul>{unfixed_html}</ul>
<h2>QA frames</h2>{frames_html or '<p>No QA frames yet.</p>'}
<footer>
  <p>This film was directed end to end by <b>asin-to-video-autopilot</b>
  v{SKILL_VERSION}, one skill of <b>Wonka</b> — the creative AI employee built by
  <a href="{MAKER_URL}">{MAKER}</a>. Wonka has others: skills that make Amazon
  product images, listing copy and A+ layouts the same way this one makes video.</p>
  <p>Building a creative employee of your own is what the
  <a href="{BOOTCAMP_URL}">Wonka Creative Bootcamp</a> is for.</p>
</footer>
</body></html>"""
    out = run / "report.html"
    out.write_text(html)
    print(f"report: {out}")


def _usage(min_args):
    """A missing argument prints the script's own usage, never a traceback.
    These scripts are read and run by hand as often as by the agent."""
    if len(sys.argv) <= min_args:
        print((__doc__ or "").strip() or f"usage: {sys.argv[0]} <args>")
        sys.exit(2)

if __name__ == "__main__":
    _usage(1)
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
