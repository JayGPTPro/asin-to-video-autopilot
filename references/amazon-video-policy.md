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

## AI disclosure — where it stands, and what this skill does

Raised by an outside reviewer, 18.8: "if using people, do we need an AI warning?"
Worth answering precisely, because the answer differs by surface and it is easy to
either over-comply with a label nobody asks for or under-comply in the EU.

- **Amazon does not require an on-screen AI-generated label on listing videos.** What
  it does require is that nothing in the video misleads: no invented certifications,
  no performance a real unit cannot deliver, no implied endorsement. A synthetic cast
  in an ordinary domestic scene is not itself a claim. Amazon's own creative tools
  generate imagery for listings, which is the clearest signal on where the line sits.
- **The EU AI Act's transparency duty (Art. 50) covers synthetic audio/video** and
  falls on whoever puts it on the market there. A seller shipping this film to an EU
  marketplace should disclose. That disclosure belongs in the listing or the seller's
  own policy, not burned into the frame.
- **What this skill does**: the run report states in plain words that the film was
  generated end to end, so the seller always holds a written record of what it is and
  what tools made it. It does not burn a label into the picture. If a user asks for
  one, it goes in the close, in the kicker tier, never over the product.
- **Never** let a synthetic person state a fact about the product on camera, and never
  stage anything that reads as a testimonial or a review. That is where a synthetic
  cast stops being set dressing and starts being a claim.
