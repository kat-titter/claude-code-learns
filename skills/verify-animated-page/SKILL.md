---
name: verify-animated-page
description: Verifies an animated web page (canvas or WebGL, a requestAnimationFrame loop, a p5.js or three.js sketch, a timer-driven UI) in an automated or embedded browser such as the Claude browser pane. Use when screenshotting or driving such a page to confirm a change, when a screenshot does not show state just set from JavaScript, or when a held press or drag vanishes after a screenshot.
when_to_use: Before trusting a screenshot of a rAF-driven page; when writing a harness that drives the page's own tick(now).
---

## Gotchas: three traps, and what to do

**1 · Stale frames.** The pane presents frames lazily when a page's `requestAnimationFrame` is throttled
(pane hidden or unfocused, tab in the background). After you change state from JavaScript, the next screenshot
often shows the *previous* frame, and time-based state (fades, holds, timers) does not advance in real time.
- Run `${CLAUDE_SKILL_DIR}/scripts/raf_probe.js` in the page: `rafPerSecond` near 0 means you are looking at a stale page.
  Measured in the Claude pane (2026-10-15, on a second page, an art piece): 7 frames/s while visible but unfocused, and 0
  with `visibilityState: hidden` right after a screenshot. A healthy page reports about 60.
- Take a tiny throwaway screenshot (scale 0.1) first, or two in a row, and trust the second: judge a change from a fresh capture.
- Read state with JavaScript or `read_page` instead of pixels whenever the claim is about state, not looks.

**2 · A screenshot can fire `blur`.** Pages that release a press, hold or drag on `window` blur (a common, correct
pattern) drop the state you set up the moment you capture it.
- Show the same render through a focus-independent path: a hover, preview or "peek" mode that puts the same picture on screen.
- Or assert from JavaScript (is it held? what is the caption?) and keep screenshots for things that do not depend on focus.
- If the page has a test flag (`?probe`), it may offer a way to ignore blur. Keep that behaviour behind the flag.

**3 · Synthetic clocks drift from page deadlines.** Driving the page's own `tick(now)` with synthetic timestamps is the
reliable way to step an animation (expose `tick` behind a test flag). But each run that starts from `performance.now()`
restarts from real time, while the page sets deadlines with `performance.now()` (hover delays, timeouts). A 2.2 s deadline
can look unexpired after a "2 s" run that began 0.2 s late.
- Keep one synthetic timeline across calls (store the last `t` and continue from it), or jump explicitly past the deadline.
- Re-sync to `performance.now()` right before calls that stamp real time (e.g. starting a hold), so durations stay honest.

## A harness that works

```js
// expose in the page behind ?probe:  window.__app = { tick, ... }
window.__run = (secs, fps = 30) => { let t = window.__t ?? performance.now(); for (let i = 0; i < Math.round(secs*fps); i++) { t += 1000/fps; window.__app.tick(t); } return (window.__t = t); };
```
Then: change state, `__run(n)`, assert from JS, and only then a throwaway screenshot plus the real one.

Provenance: a WebGL sink piece, 2026-10-15. Captures showed the previous state after probe-driven finds;
a screenshot released a test hold through the page's blur handler; a hover-recall timeout looked broken until the
synthetic-clock restart was accounted for. The previous session had already hit stalled rAF and clock drift.

**Hover and tap UI.** When a page explains things on hover, verify from JavaScript that the card appears (not hidden, inside the viewport) and that nothing else moves: compare the container's height before and after the hover (layout shift must be 0). Floating cards beat rows that drop open (a DJ tool audit, 2026-10-20).

- **Background tabs do not run requestAnimationFrame.** A transition that re-renders when its rAF loop ends never finishes in an unpainted test tab (or a hidden real one): end it with a `setTimeout(finish, duration + 200)` as well, `finish` idempotent, and wait past that before checking (a DJ tool playlist map, 2026-10-20).

- **A page renderer can reset a canvas you sized.** A template runtime (an art piece's docs' dc/React runtime) put a canvas back to 300 x 150 after load, at device pixel ratio 2 only, while the script's cached W and H still matched, so it never resized and retina screens showed nothing; 1x tests passed. Size from the bitmap itself (`cv.width !== Math.round(rect.width * dpr)`), test at ratio 2, and keep a reduced-motion still frame alive the same way (an art piece an art piece gold bubbles, 2026-11-17).
- **Chrome's PDF drops what lies under a transparent canvas.** Printing a page with a full-bleed canvas over a photo gave a white cover with only the canvas marks. Hide the canvas in print and show a still PNG of it (`toBlob` at the page size) instead; check by rendering page 1 of the PDF, since a screen capture never shows it (same day).
