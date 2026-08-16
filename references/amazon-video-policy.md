# Amazon listing-video policy — what gets a video rejected

A film Amazon rejects is worth zero, whatever it cost. These are the content rules
for product-detail-page videos (Amazon's Product Detail Page rules + Creative
Acceptance policies, condensed to what a generated ad actually trips on). Run
`scripts/policy_check.py` on the VO script and every overlay text BEFORE the
master renders — at that stage a violation is a free line rewrite.

## HARD — never allowed, always rewrite

1. **Superlative and rank claims**: "best seller", "#1", "top rated", "the best",
   "world's leading", "most popular", "award-winning" (without naming a real,
   verifiable award). Amazon treats unverifiable superiority claims as prohibited.
2. **Price, promotion, urgency**: any price, "sale", "discount", "% off", "free
   shipping", "limited time", "buy now before". Videos outlive promotions; Amazon
   rejects time-bound or price content.
3. **Off-Amazon diversion**: URLs, "visit our website", social handles, QR codes,
   email addresses, phone numbers. Nothing may lead the customer off Amazon.
4. **Customer-review content**: quoting reviews, star ratings, "5 stars",
   "thousands of happy customers", testimonial framing.
5. **Health/medical claims** for non-medical products: "cures", "treats",
   "prevents", "clinically proven" (without the study), disease names as promises.
   Cosmetic/wellness language must stay cosmetic ("supports the look of…").
6. **Competitor references**: naming or showing another brand, "better than X",
   "unlike other brands".
7. **Guarantees Amazon does not honor**: "money-back guarantee", "lifetime
   warranty" (warranty terms live in the listing, not the video).

## SOFT — allowed only with proof in the listing itself

- Specific numeric claims ("lasts 24 hours", "10,000 uses") — keep only if the
  listing's own copy carries the same number; the video may never out-claim the
  listing.
- Certifications ("USDA Organic", "FDA registered") — only if visible on the real
  label or in the listing images. If the label shows it, the video may say it.
- "Patented" — only if the listing says it.

## Format facts (the conform stage already satisfies these)

- 16:9 at 1280x720 minimum; .mp4; under 500MB; no black bars.
- No letterboxing text into the safe margins Amazon's player crops on mobile:
  keep supers inside 5% margins (the template's default positions comply).

The checker errs strict: a HARD hit blocks; a SOFT hit prints the claim and the
proof it needs, and the run keeps the line only if the listing carries the proof
(log which listing element proves it).
