#!/usr/bin/env python3
"""Amazon listing-video policy check — run on the VO script + overlay texts
BEFORE the master renders (see references/amazon-video-policy.md).

Usage:
  policy_check.py <text_file> [more_text_files...]
  echo "some line" | policy_check.py -

HARD hits exit 1 (rewrite the line, free at this stage). SOFT hits exit 0 with
a warning: keep the claim only if the LISTING carries the same proof, and log
which listing element proves it.
"""
import sys, re

HARD = [
    (r"\bbest[\s-]?sell", "superlative: 'best seller'"),
    (r"(^|\s)#\s?1\b|\bnumber\s+one\b", "rank claim: '#1'"),
    (r"\btop[\s-]?rated\b", "superlative: 'top rated'"),
    (r"\bthe\s+best\b|\bworld'?s\s+(best|leading|finest)\b", "superlative: 'the best'"),
    (r"\bmost\s+(popular|trusted|loved)\b", "superlative: 'most …'"),
    (r"\baward[\s-]?winning\b", "unverifiable award claim"),
    (r"[$€£₪]\s?\d|\b\d+\s?(dollars|usd)\b", "price in video"),
    (r"\b(sale|discount|coupon|promo\b|%\s?off|free\s+shipping)\b", "promotion"),
    (r"\b(limited\s+time|order\s+now|buy\s+now|before\s+it'?s\s+gone|today\s+only)\b",
     "urgency / time-sensitive"),
    (r"\b(www\.|https?://|\.com\b|\.co\.|follow\s+us|instagram|tiktok|facebook)\b",
     "off-Amazon diversion"),
    (r"\b(five|5)[\s-]stars?\b|\bstar\s+rating\b", "review/star content"),
    (r"\b(thousands|millions)\s+of\s+(happy|satisfied)\s+customers\b", "testimonial claim"),
    (r"\breviews?\s+say\b|\bcustomers?\s+say\b", "review quoting"),
    (r"\b(cures?|treats?|heals?|prevents?)\b", "medical claim verb"),
    (r"\bclinically\s+proven\b", "unsubstantiated clinical claim"),
    (r"\b(better|cheaper|stronger)\s+than\s+(other|any|the\s+competition)\b",
     "competitor comparison"),
    (r"\bunlike\s+other\s+brands?\b", "competitor reference"),
    (r"\bmoney[\s-]?back\b|\blifetime\s+(warranty|guarantee)\b", "guarantee claim"),
]

SOFT = [
    (r"\b\d{2,}[\s-]?(hours?|days?|uses|washes|charges|mah)\b",
     "numeric claim — the listing copy must carry the same number"),
    (r"\b(usda|organic\s+certified|fda|certified|iso\s?\d+)\b",
     "certification — must be visible on the real label or listing"),
    (r"\bpatented?\b", "patent claim — only if the listing says it"),
    (r"\bguarantee[ds]?\b", "guarantee wording — check what the listing promises"),
]


def check(text, src):
    hard, soft = [], []
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for pat, why in HARD:
            if re.search(pat, low):
                hard.append(f"{src}:{n}  HARD  {why}\n    > {line.strip()}")
        for pat, why in SOFT:
            if re.search(pat, low):
                soft.append(f"{src}:{n}  SOFT  {why}\n    > {line.strip()}")
    return hard, soft


def main():
    hard, soft = [], []
    args = sys.argv[1:] or ["-"]
    for a in args:
        text = sys.stdin.read() if a == "-" else open(a).read()
        h, s = check(text, a)
        hard += h
        soft += s
    for x in soft:
        print(x)
    for x in hard:
        print(x)
    if hard:
        print(f"\nFAIL — {len(hard)} hard policy hit(s). Rewrite before rendering.")
        sys.exit(1)
    print(f"PASS — no hard hits ({len(soft)} soft warning(s) to verify against the listing)")


if __name__ == "__main__":
    main()
