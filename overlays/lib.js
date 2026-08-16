/*
 * Overlay choreography library — every build here shipped on a real production.
 * Rules that keep renders clean:
 *   - GSAP owns ALL transforms. Never a CSS `transform` on an animated node.
 *   - Never animate letterSpacing (layout reflow stutters in the render).
 *     Per-glyph motion = spans + y/x transforms.
 *   - Every super element: class="clip", its own data-track-index, and the
 *     timeline registered on window.__timelines.
 *
 * Usage: build one paused timeline, then call these with (tl, selector, t, opts).
 * Times are absolute film seconds (from measured VO word timestamps).
 * Split text into spans first with splitGlyphs()/the .w word pattern in HTML.
 */

/* eslint-disable no-unused-vars */

// ---- text prep ------------------------------------------------------------

// Wrap each glyph of el's text in a span.g (spaces become fixed-width spacers).
function splitGlyphs(el, spacingPx) {
  const text = el.textContent;
  el.textContent = "";
  for (const ch of text) {
    const s = document.createElement("span");
    s.className = "g";
    s.style.display = "inline-block";
    if (spacingPx) s.style.marginLeft = spacingPx + "px";
    if (ch === " ") { s.innerHTML = "&nbsp;"; s.classList.add("gs"); }
    else s.textContent = ch;
    el.appendChild(s);
  }
}

// ---- entrances ------------------------------------------------------------

// Thin-cinematic signature: glyphs rise softly in sequence.
function letterRise(tl, sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05 }, t);
  tl.fromTo(sel + " .g", { y: o.rise || 30, opacity: 0 },
    { y: 0, opacity: 1, duration: o.dur || 0.7, ease: "power3.out",
      stagger: o.stagger || 0.05 }, t + 0.03);
}

// Words (span.w and .dot separators) rise in sequence — kickers, triads.
function wordRise(tl, sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05 }, t);
  tl.fromTo(sel + " .w, " + sel + " .dot", { y: o.rise || 22, opacity: 0 },
    { y: 0, opacity: 1, duration: o.dur || 0.65, ease: "power3.out",
      stagger: o.stagger || 0.12 }, t + 0.02);
}

// Kinetic signature: Z-push ram-in from the beat's own side, then the SNAP.
// Parent needs `perspective: 900px` or the z reads as nothing.
function ramIn(tl, sel, t, o = {}) {
  const side = o.side === "right" ? 1 : -1;
  tl.fromTo(sel,
    { x: 300 * side, z: -620, rotationY: 22 * side, opacity: 0 },
    { x: 0, z: 0, rotationY: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, t);
  tl.fromTo(sel, { scaleX: 1.06 }, { scaleX: 1.0, duration: 0.12 }, t + 0.42);
}

// Words pop in sequence with a back overshoot — lists, playful lines.
function wordPop(tl, sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05 }, t);
  tl.fromTo(sel + " .w, " + sel + " .dot", { scale: 0.55, opacity: 0 },
    { scale: 1, opacity: 1, duration: o.dur || 0.5, ease: "back.out(2)",
      stagger: o.stagger || 0.09 }, t + 0.02);
}

// Playful rise with a bounce settle.
function bounceRise(tl, sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05 }, t);
  tl.fromTo(sel + " .g", { y: o.rise || 46, opacity: 0 },
    { y: 0, opacity: 1, duration: o.dur || 0.8, ease: "bounce.out",
      stagger: o.stagger || 0.04 }, t + 0.02);
}

// Label-echo signature: text revealed from behind a line (clip-path wipe).
// The wrapper stays put; only the clip moves — no reflow.
function maskReveal(tl, sel, t, o = {}) {
  tl.set(sel, { opacity: 1 }, t);
  tl.fromTo(sel, { clipPath: "inset(0 100% 0 0)" },
    { clipPath: "inset(0 0% 0 0)", duration: o.dur || 0.85,
      ease: "power2.inOut" }, t);
}

// A rule/underline draws itself from its origin side.
function ruleDraw(tl, sel, t, o = {}) {
  tl.fromTo(sel, { scaleX: 0, transformOrigin: (o.from || "right") + " center" },
    { scaleX: 1, duration: o.dur || 0.4, ease: "power3.out" }, t);
}

// A slab/pill lands behind one word, then settles.
function slabLand(tl, sel, t, o = {}) {
  tl.fromTo(sel, { scaleX: 1.08, opacity: 0, transformOrigin: "left center" },
    { scaleX: 1.0, opacity: 1, duration: 0.35, ease: "power2.out" }, t);
}

// A number counts up to its value inside a span (typed text stays crisp;
// this is for ONE hero number, never several).
function counterRoll(tl, sel, t, o = {}) {
  const el = document.querySelector(sel);
  const end = o.to != null ? o.to : parseInt(el.textContent.replace(/\D/g, ""), 10);
  const suffix = o.suffix || "";
  const obj = { v: o.from || 0 };
  tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.2 }, t);
  tl.to(obj, {
    v: end, duration: o.dur || 0.9, ease: "power2.out",
    onUpdate: () => { el.textContent = Math.round(obj.v).toLocaleString() + suffix; }
  }, t);
}

// ---- holds (one slow secondary motion keeps a super alive) ----------------

function drift(tl, sel, t, o = {}) {
  tl.to(sel, { y: -(o.px || 8), duration: o.dur || 1.4, ease: "sine.inOut" }, t);
}

function microShake(tl, sel, t, o = {}) {
  tl.to(sel, { x: "+=2", yoyo: true, repeat: 5, duration: 0.05 }, t);
  tl.to(sel, { y: -(o.px || 6), duration: o.dur || 1.2, ease: "sine.inOut" }, t + 0.3);
}

function gentleSway(tl, sel, t, o = {}) {
  tl.to(sel, { rotation: o.deg || 1.2, yoyo: true, repeat: 1,
    duration: (o.dur || 1.6) / 2, ease: "sine.inOut" }, t);
}

// ---- exits ----------------------------------------------------------------

function quietFade(tl, sel, t, o = {}) {
  tl.to(sel, { opacity: 0, duration: o.dur || 0.4, ease: "power2.in" }, t);
}

function directionalSlide(tl, sel, t, o = {}) {
  const side = o.side === "right" ? 1 : -1;
  tl.to(sel, { x: 46 * side, opacity: 0, duration: o.dur || 0.36,
    ease: "power3.in" }, t);
}

function popOut(tl, sel, t, o = {}) {
  tl.to(sel, { scale: 0.85, opacity: 0, duration: o.dur || 0.3,
    ease: "back.in(1.6)" }, t);
}
