#!/usr/bin/env python3
"""Run report: every decision, measurement and dollar, as one HTML page.

    python3 report.py <run_dir>

Reads brief.json (incl. decision_log), compile-result.json, run-state.json and
qa/ frames if present. The report is the buyer's receipt AND their marketing
asset: "this is how the AI directed my product film".
"""

import json
import sys
from base64 import b64encode
from html import escape
from pathlib import Path


def img_tag(p, w=220):
    data = b64encode(p.read_bytes()).decode()
    return f'<img src="data:image/jpeg;base64,{data}" style="width:{w}px;border-radius:8px;margin:4px">'


def main(run_dir):
    run = Path(run_dir)
    brief = json.loads((run / "brief.json").read_text())
    compile_result = json.loads((run / "compile-result.json").read_text()) \
        if (run / "compile-result.json").exists() else {}
    state = json.loads((run / "run-state.json").read_text()) \
        if (run / "run-state.json").exists() else {}

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
            ("Prompt size", f"{compile_result.get('prompt_chars', '?')} chars, "
                            f"{compile_result.get('density_chars_per_sec', '?')} chars/sec"),
            ("Total spend", f"USD {state.get('spent_usd', '?')}"),
        ])

    decisions = "".join(f"<li>{escape(d)}</li>" for d in brief.get("decision_log", []))
    qa_frames = sorted((run / "qa").glob("*.jpg")) if (run / "qa").exists() else []
    frames_html = "".join(img_tag(f) for f in qa_frames[:12])

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Run report: {escape(brief.get('asin', ''))}</title>
<style>body{{font-family:-apple-system,Arial,sans-serif;max-width:860px;margin:32px auto;
padding:0 16px;line-height:1.6;color:#1d1a16;background:#faf6ef}}
h1{{font-size:1.5rem}}h2{{font-size:1.1rem;border-bottom:2px solid #b8860b;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%}}td{{border:1px solid #e8e0d2;padding:6px 10px;
vertical-align:top}}td:first-child{{font-weight:600;width:200px}}</style></head><body>
<h1>asin-to-video-autopilot run report</h1>
<h2>The film</h2><table>{rows}</table>
<h2>Decisions the autopilot made, and why</h2><ul>{decisions}</ul>
<h2>QA frames</h2>{frames_html or '<p>No QA frames yet.</p>'}
</body></html>"""
    out = run / "report.html"
    out.write_text(html)
    print(f"report: {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
