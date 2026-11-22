---
name: page-legibility-check
description: Measures, rather than eyeballs, whether an HTML page or figure is legible - WCAG AA contrast against what is painted behind each text run, SVG label collisions, sideways overflow and tiny text, at 1280 px and a true 400 px phone width, in light and dark. Use before publishing a page with charts, maps or labelled figures, or when someone says "labels overlap", "check on mobile", "dark mode" or "text a bit larger".
when_to_use: Once per publish of a page with figures (wording-only edits need no run); when a figure must work on phones; when a screenshot looks fine but nothing was measured.
---

# Page legibility check

Run it:

```bash
${CLAUDE_SKILL_DIR}/scripts/check-page.sh <page.html> [query] [delay-ms] [screenshot-dir]
```

- `query` is appended to the URL (e.g. `solo=5` for one slide); `theme=light|dark` is added for you and sets `<html data-theme>`.
- `delay-ms` (default 1500) is how long after load to measure; raise it for pages that fetch or animate in.
- `screenshot-dir` also writes `desk-<theme>.png` and `phone-<theme>.png` to look at.
- Output: one JSON line per run (1280/400 × light/dark), then PASS or FAIL. FAIL means contrast failures, overlaps (SVG text on text or dots, HTML text over a figure's boxes), shapes clipped at their svg's edge (`clipped`), or anything wider than the viewport. `tiny` (rendered text under 9 px) is listed but not counted; a 16:9 deck at phone width will always show it.

Pages that `fetch()` JSON files next to them work as-is (the run allows file access from files). Pages that load claude.ai artifact `db` data render empty locally: make a test copy that defines a mock (e.g. `window.claude={use:async n=>n==='db'?mockDb:null}`) before the page script, fed with the real rows exported via `ArtifactData list` with `out_dir`. Either way, also check a stress copy with many extra rows piled on one place and one month.

The checker jumps finite CSS/Web animations to their end before measuring: mid-animation (bars growing in) labels sit on the wrong background, and headless Chrome sometimes never starts an animation clock, so waiting can hang. If a result flips between runs, suspect timing first.

For interactions (filters, popovers, drag), inject a small script into a test copy that clicks or dispatches `PointerEvent`s, then writes what the page shows into a `<pre>` for `--dump-dom` to read.

For a slide deck that mounts each slide in a shadow root, the checker sees nothing inside the slides: write one flat page per
view (the slide's markup in the light DOM, scaled to the window as the deck scales it, the view's class set, the stage layer's
hide rule), and in it finish the entry animations (`document.getAnimations()`, `finish()`) and set `display:none` on whatever
is still at opacity 0, so the other views stacked in the same slide do not join the count. Run the check per page, four at a time.
Case: a pitch deck, 2026-10-26: the first flat pages, every view left in place, counted 05b's map labels on 05a.

For a PDF made with Chrome `--print-to-pdf`, look at chosen pages without installing anything: render them through PDFKit from JavaScript for Automation (`osascript -l JavaScript`, `ObjC.import('PDFKit')`, `page.thumbnailOfSizeForBox(...)`, write PNG). The Swift toolchain can lag the SDK; JXA has no compile step.

## Gotchas

- **An overlap of text boxes is not a collision.** An svg text box runs ascent to descent, so two STACKED lines
  on a tight line step overlap by a pixel or two with clear white between the glyphs. That is leading. Raising a
  figure's labels from 12 to 14 px on an unchanged 16-unit step turned 96 such pairs into "overlaps" and failed a
  page for having ordinary line spacing (a peptide explainer, 2026-11-06; measured 0.7-3.2 px, every one under a quarter
  of the text height, while a real collision runs half to all of it). `check.js` now counts a stacked pair only
  when it bites deeper than a quarter of the smaller box; labels sharing a line are still judged on their
  horizontal overlap. Confirm any change here with a negative control: inject one real collision and watch it fail.
- **Touching is what crowding looks like first.** This checker tests for overlap, so two labels that abut with a
  1 px gap pass while reading as one word ("NO MOTS-c"). After any change to label size, also measure the GAP
  between labels that share a line - a small gap script (not included here) did this on one explainer and found all
  five real collisions of that raise, none of which the overlap test saw.
- **Open every `<details>` before measuring.** A figure inside a closed fold is laid out but never painted, so its
  labels measure against a box the reader never sees and report collisions and clipping that do not exist (the
  the same run: 7 phantom entries, "outside svg" and a label on a dot, all from folded figures). A fold is
  content and its figures must be legible too, so open them rather than skip them.
- Measure at the width the reader uses, not only 1280 and 400: the Claude app's artifact pane is narrower than a full
  window, and a layout switched on above it (a `min-width:1440px` grid) is a fix the reader never sees (a peptide explainer
  cell map, 2026-11-06: "what happened to arranging text alongside position in cell? this is the third time im asking").
  Prefer layouts that scale with the drawing (callouts inside the SVG) to ones gated on a breakpoint.

- **A cropped icon still reports the part it hides.** An icon cut down with a nested `<svg viewBox>` or a clipPath
  keeps its hidden paths in `getBoundingClientRect` and `isPointInFill`, so labels below it read as collisions and its
  drawing as 100 px taller than it is. Drop the paths whose control-point box lies wholly outside the window at build
  time and clip the rest; then measure label-to-shape overlap on what is painted (sample each label's box with
  `isPointInFill` / `isPointInStroke` through `getScreenCTM().inverse()`), with a negative control (a peptide explainer
  Figure 2, 2026-11-20: 72 of the IgG icon's 114 paths never showed; `check.js` compares text to text and dots only).
- **A drawing inside an overflow container passes every check while half of it is off-screen.** A
  figure authored 880 px wide in a `.scroll` box does not overflow the *page*, so `hscroll` is false,
  nothing is `wide` and no text is `tiny` — the checker measures the document, not the box. At 400 px
  the reader sees a cropped drawing and, on macOS, an overlay scrollbar that is invisible until it is
  dragged. Scaling is not the fix (880 into 400 renders 11 px labels at 5 px), so keep the scroll and
  make it visible: a sticky line in the box, scoped to the surfaces that actually overflow
  (`.scroll:has(> svg)`, not the tables that reflow). Measure it rather than trusting the rule —
  compare `scrollWidth - clientWidth` against which boxes carry the cue, and expect zero mismatches
  (peptide doc 1, 2026-11-05: 13 drawings overflowing by 512 px each, none of it cued, every check
  green).
- **Grouping wrapped items by their exact `top` invents rows.** Key swatches of different kinds
  (a hex, a ring, a 0-height line, a tick) sit on different `vertical-align`, so items on one visual
  row report tops 12 px apart and a "straggling last row" appears that nobody can see. Group by a
  tolerance, or read the left edges instead, and look at the render before shortening anything.

- Dark runs that report exactly the light numbers: the page's own theme script removed the `data-theme` the checker set (an "auto" mode that calls `removeAttribute` on load), so every "dark" run measured light. Let the page honour `?theme=` and an existing attribute, and compare the light and dark ratios before trusting a dark pass (a peptide explainer, 2026-11-05: identical 4.25 ratios in both themes; once fixed, dark showed one more miss).
- **oklch text goes unmeasured.** A colour written as `color-mix(in oklch, ...)` or `oklch()` comes back from Chrome as `oklch(...)`, which `check.js` lists under `unknown` and never tests, so a run can PASS with every hued word unchecked. Resolve those colours through a 1x1 canvas (`fillStyle` then `getImageData`) and compute the ratio against the painted ground yourself (a peptide explainer mist-plate pass, 2026-11-20: 65 peptide names, lowest 4.88:1).
- `check.js` read only `rgb()` colours; a colour set through `color-mix()` comes back from Chrome as `color(srgb r g b)` and every run threw on its first text (a DJ studio, 2026-11-03). It now parses both and lists any other form under `unknown`.

- SVG text below the fold reads as failing contrast (ratio near 1, dark ink "on" the card): `elementsFromPoint` returns nothing outside the viewport, so the checker falls back to the svg's own background and misses the bar under the label. Compute that pair's ratio by hand before changing a colour (stray_under page, 2026-11-05: "65%" in ink on a white bar flagged at 1.07; true ratio about 15:1).
- `bash check-page.sh` fails ("print: command not found", no output): it is a zsh script, so run it by its path and let the shebang pick the shell (2026-10-27).
- A headless driver will not click an SVG `<g>`: the parent `<svg>` intercepts pointer events and the group's
  own box has transparent gaps, so Playwright retries until it times out. Dispatch the event instead
  (`page.dispatchEvent('#id','click')`) and assert the state it should have set (`aria-expanded`) rather than
  trusting the screenshot. A card that only its script hides also needs the click: setting `display` in a copy
  of the page is undone by the script's own close-on-load (a peptide explainer structure cards, 2026-11-05).
- A screenshot that looks fine hides text sitting on a label: measure collisions with the checker.
- A narrowed desktop window is not a phone: check at a true 400 px viewport.
- Contrast computed against the CSS background misses text over images or gradients: measure against what is painted.
- Text legible on desktop and too small on a phone ("text a bit larger, maybe 20%"): the tiny-text check runs at phone width.

## Fonts actually rendered

Read each text node's computed font family; a fallback such as Times means a missing font or a broken wrapper. Case
(2026-10-26): a stray closing tag shut the font wrapper after page two of a print doc, so six pages fell back to Times
("why last page using serif font all of a sudden?"). Check div balance per section after any cut.

## What it catches beyond screenshots

- **Phone width is not 500 px.** Headless Chrome will not size a window below 500 px, so the script renders the page inside a 400 px iframe and posts results out.
- **Text over shapes.** Contrast is computed against the topmost painted element under each label (`elementsFromPoint`), not the page background.
- **Theme gaps.** Each run sets `data-theme`; a page that only reads `prefers-color-scheme` will not switch, so check that it honors `[data-theme]` (artifact pages must).

## Fixes that keep coming up

1. **Draw SVG figures at their true pixel width.** A fixed `viewBox` scaled to a 330 px phone panel shrinks 11.5 px labels to about 7 px. Measure the svg (`getBoundingClientRect().width`), set `viewBox="0 0 W H"`, lay out in pixels, and redraw from a `ResizeObserver` (guard on width so setting the height does not loop). Switch layouts below a width (side by side vs stacked).
2. **Labels first, then marks.** Place each label at the first free candidate around its anchor (right, left, above, below, diagonals, at growing distances), inside bounds, avoiding other labels and markers; draw a thin leader when it lands far away. Then place dots on a sunflower spiral (`angle = i·2.39996`, `r ∝ √i`) out from the true position until they clear the labels and each other. Merge 10+ marks at one spot into a numbered circle so labels never get starved.
3. **Collision math needs real font metrics.** DM Mono: advance 0.6 em; its text box runs 1.0 em above the baseline and 0.5 em below. Measure other fonts once with `getBBox`.
4. **Axes adapt with the data.** Pick the tick step so labels clear each other (`step × pitch ≥ 1.5 em + 2`), extend time axes to the latest data and today, and leave room below for the axis title's descenders.
5. **Tables overflow first on phones.** Drop a column into an inline marker (a colored dot already explained by a legend), let headers wrap, and wrap the table in `overflow-x:auto` as a backstop.
6. **`hidden` loses to `display`.** Any rule like `.legend span{display:inline-flex}` beats the browser's `[hidden]`; add `[hidden]{display:none!important}`.
7. **Look at a render before using a "free" corner.** Scripts draw things the HTML doesn't show (slide progress dots, overlays); a link placed there by reading the source collided with them.
8. **Class names collide across sections.** A new `.sub` inside a table inherited the header subtitle's 17 px and margin; prefix component classes.
9. **Keep every shape inside its viewBox.** A receptor pill drawn 4 px past the bottom of its svg was silently clipped and read as "cut off" next to the legend below it. `clipped` now catches this, including shapes marked as label backgrounds.
11. **Map marks belong on land.** When dots are nudged apart, test each candidate position with point-in-polygon against the land polygons (minus bays and lakes); a dot pushed into the water reads as an event at sea.
12. **Collapsed content still has boxes.** Chrome lays out the inside of a closed `<details>` without painting it, so a checker that reads `getBoundingClientRect()` sees phantom shapes under the text below. The checker now skips anything `checkVisibility()` says is not rendered. Run it once with every `<details>` closed and once on a copy with them all open (`sed 's/<details/<details open/'`).
10. **Explain once.** Captions that restate the figure ("last call to spray" under a 3:00 dial), tags that repeat the headline, agenda lines, and arrows between before/after columns add reading without adding meaning. Let the figure and the headline carry it.

13. **Legends and axes follow figure-design**: one legend row per kind of key, outside the plot; every axis labelled with its unit and direction.
14. **Measure what figure-design asks for**: no text on text or on marks, the legend clear of the data, text at or above the 11 px floor.
15. **Views that share a time axis share its pixels.** A scrub bar and the plots under it use one x-scale and one left gutter; verify t=0, a mid time and the end land within 1 px in every view.
16. **Explain in floating hover/tap cards.** Cards keep text large, cause no layout shift, stay inside the viewport beside the hovered thing; keyboard focus opens them; measure the table height before and after hover (shift must be 0).
17. **No separator dots, no repeated text.** Run a separator-and-repeat checker (design-practice has one, not in this repo) and judge each repeated phrase; separate inline items by space, weight or alignment.
18. **No transforms on figure text.** a path checker that reads `text.getBBox()` in the element's own coordinates, so a `translate` on a label's group (or a rotated label) reports `clipped` or checks the wrong spot. Draw labels and glyphs at absolute coordinates; keep axis words horizontal.
19. **Check with the hover open.** A hover ring (radius + 4) touches labels placed just outside the dot: make every label obstacle the ring's box (r + 5). Two points on one spot (one bpm, one energy) starve their labels: let a leader leave through its own neighbour, test leaders against the dots themselves (not their rings), and fall back to the nearest free spot on a grid over the whole plot.

For SVG figures with lines and curves (not just text and dots), add a checker that samples points along each path; this one tests text boxes only.

Provenance: a tracker page tracker (2026-10-15). The first render passed contrast but had 11 label collisions, a mislocated city, a 412 px table at phone width, a clipped axis title and colliding tick labels at 400 px; a stress run dropped city labels under a 30-dot cluster. Validated on a different page: a public-health deck (slides 5 and 17) passes at 1280 px in both themes.
Items 13 to 17: a DJ studio (2026-10-20): legends that mixed dots and lines, a map with unlabeled learned axes, a scrub bar 155 px off its plots, audit rows that jumped open, separator dots in a wordmark. See also the design-practice skill (composition, colour, interactivity) and field-vocabulary (words).
