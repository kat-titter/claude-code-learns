---
name: interactive-figures
description: Designs, builds and audits interactive figures and explorables for posts, essays and reports - sliders, clickable diagrams, hover cards, 3D views and live simulations - with an audit script for targets, focus, click errors and reduced motion. Use when adding interactivity to a figure, or when a reader says it is "clunky", "jumpy", "hard to discover" or the text sits "in a weird position".
when_to_use: Before building an interactive figure; before publishing a page with controls, hover states or animation (run the audit with page-legibility-check).
---

# Interactive figures

Interactivity earns its place when it lets the reader do something that a still picture can't: push the system and
watch it answer. These are guidelines, each with an example. Break one when the figure is clearer for it.

## Gotchas

- A sentence telling the reader how to use the figure: make the control look pressable instead (§ on controls).
- A slider that drives a curve nobody measured: draw only what a source supports.
- A figure that is blank until the script runs: the markup carries a readable default frame.

## 1 · Decide what the reader should do

- **Let the reader push the system before you name the property.** In a three-gene ring, the reader flips an arrow
  from amplify to brake and watches a switch become a clock. Only then does the text say "odd brakes give a clock".
  Nicky Case's advice runs the same way: show what made you care, show, then tell.
- **Build the prediction from the page's own parts.** When a page predicts something that does not exist yet, assemble
  it live from pieces the reader has already pushed (the lac switch fed the running total of a pulse), with one control
  that makes the predicted behaviour visible (pulse length; a toggle that keeps the dose and doubles the strength), and a
  Python twin asserting the claim before the figure is drawn. Case: an essay's hypothetical element Sw∫
  (2026-10-25: "show example of hypothetical missing element").
- **Expose the model.** Bret Victor's reactive documents let readers skim, read, or change the author's assumptions
  and see the consequence. Put the real parameters on the slider (the hill's steepness, the ruler's length). This also
  keeps the author honest.
- **Let the reader point at the thing itself.** A table of elements works best when you point at a
  tile to read it. An earlier version built each circuit from segmented buttons, which felt clunky, and was replaced.
- **Pick and select on the figure itself.** An axis's own label is its measure picker (press "danceability" to swap it),
  not a separate x-versus-y menu. To select many points, use flow cytometry's gates: a point, a lasso, a rectangle, a
  threshold line, a diagonal, with points inside in the accent and the rest quiet (a DJ tool playlist map, 2026-10-27:
  "learn from single cell flow, 'gates' ... lasso, point, linear, diagonal gate select"; "instead of x vs y drop down,
  should be able to interact with legend label").
- **Use one representation per question, and several only when they answer different questions.** A 3D spiral shows the
  shape of the whole; a flat grid shows which cells are full. Give both the same card, so reading one teaches the other.
- **Follow the information-seeking mantra (Shneiderman, cited by Distill): overview first, zoom and filter, then
  details on demand.** The tile shows a symbol and a trace; the card gives the detail.

## 2 · Draw in the field's own language

- **Use the notation specialists already read.** For gene circuits: named nodes (X, Y, Z), → activates, ⊣ represses,
  and an integrator marked ∫. Keep the drawing abstract, but make it recognisable.
- **Show behaviour as a small trace.** A sine for "keeps time", two diverging lines for "holds two states",
  a step that returns for "adapts exactly". Dash the trace when it is a prediction.
- **Give a shorthand a key, the way chemistry does.** Draw a worked tile with each part labelled (number, loops, symbol,
  what it does, how many found). Place it in the table's empty space, as periodic tables do. Keep symbols unique and
  clear of nearby codes (design-practice: one symbol per thing).

## 3 · Make it feel smooth

- **Draw a complete first frame without JavaScript**, server-side, then let the script take over at the true pixel
  width (ResizeObserver). Readers on slow phones, print, and crawlers still see the figure.
- **Use one card for every view.** app-design owns the guideline (hover or tap cards instead of drop-downs). The
  craft that makes cards feel calm: place the card beside the thing you point at, leaving it in view (try right, left,
  below, above), fade it in over about 140 ms, pin it on tap or click, close it on Esc, and let Tab and the arrow keys
  reach every item.
- **Give motion weight.** A dragged object coasts and slows (inertia). Automatic rotation eases in and out, pauses
  while the reader points at something, stops when the figure is off screen (IntersectionObserver), and holds still
  under prefers-reduced-motion.
- **Make targets generous** (app-design: 44 px). For thin marks, add an invisible wide stroke (stroke="transparent",
  stroke-width 44) on arrows and a transparent circle around small dots; make sliders 44 px tall.
- **The control shows itself, with no instruction line.** A sentence telling the reader how to use a figure ("point at a
  part of the cell to light the peptides", "drag the lactose up slowly") is cut: the cursor changes over a hit target,
  the focused item outlines, and a gesture nobody would guess gets a quiet pulse in the highlight colour that stops after
  first use (app-design). Where a control truly needs a word, the word is the control's own label. Row labels sit beside
  what they label. A hover card peeks (name, glyph, one line); a tap pins the full card; on phones the pinned card is a
  fixed sheet that leaves the tapped thing visible. (Loop-table audit, 2026-10-24; a peptide explainer, 2026-11-06: "we
  discussed removed extraneous text like this, is this in a skill?" - this file and the person's style skill still asked for one.)
- **Make state visible.** Pressed controls carry `aria-pressed`, the focused item has a visible outline, and the
  current selection stays highlighted in the figure while its card is open.

## 4 · Gotchas

- Text revealed only by interacting is "too hard to discover and play": show the first state, and let the control invite the action.
- A control's explanation far from the control ("text in weird position"): put it right above or beside the control.
- An effect that arrives too suddenly ("comes in too suddenly, stands out too much"): ease it in.
- **A slider over a relationship nobody has measured says so, in the caption, in bold.** Driving a mechanism figure
  from a control implies a dose-response the reader will read off it. Where none is published, label the input in
  relative units and state that the mapping is schematic and shows direction, not fitted data (a peptide explainer,
  2026-11-05: "slide amount of bioactive up/down, see how chem flux in cell changes" - no dose-response curve exists
  for that compound). Draw only curves you can cite.
- **A shared hover script embedded beside a page's own needs a scope.** Bound page-wide, it re-binds the host's
  figures and adds tab stops the host never named; give it a block to work in (`<script data-scope="#chapter">`)
  and diff the audit against the host page alone, which should match exactly (a peptide explainer 09b, 2026-11-05: 8
  unnamed controls from linked.js until scoped). The audit exempts links only inside p, li, td or figcaption, so
  a cited `dd` wraps its text in a `p`.
- **Chrome tabs to any svg element with a focus listener.** A linked-figure script that binds focus to every `data-k`
  mark makes each twin (a drawing group, a hit stroke) a silent, unnamed tab stop. Only the mark that carries the card
  gets `tabindex="0"`; give every twin an explicit `tabindex="-1"` and walk the Tab order once (a peptide explainer Figure
  2, 2026-11-20: 10 named stops plus 3 bare `<g>` stops until the twins said -1).
- **SVG arrowheads grow with the line.** `markerUnits` defaults to `strokeWidth`, so a marker on a line whose width is
  driven balloons; set `markerUnits="userSpaceOnUse"` and size the marker in user units.
- **The figure reads at the markup's default value** even if the script fails, and in-figure labels assert only
  changes the control is showing ("mRNA up" at zero exposure).

From Hohman, Conlen, Heer and Chau, "Communicating with Interactive Articles" (Distill, 2020):

- **Interactivity that no one needs distracts.** If a still figure says it, keep it still.
- **Accessibility gaps:** give text alternatives (aria-label on the figure, a card read by `aria-live`) and full
  keyboard access.
- **Cost and decay:** interactive pages are closer to building software than writing. Keep them self-contained (no
  external requests) so they keep working.

## 5 · Audit before publishing

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_interactions.py PAGE.html --width 400
```

The script needs Playwright. It reports:

- controls under 44 px;
- controls with no accessible name;
- controls that show no change when reached with Tab;
- page errors raised by clicking each control;
- figures that keep moving under reduced motion;
- figures that are empty with JavaScript off.

Treat each finding as something to look at. Pair it with page-legibility-check (contrast, overlaps, phone width) and,
for animated pages, verify-animated-page.

Validated on two pages:

- **The loop-table post:** after one round of fixes it reports zero on every check; before, three sliders were 32 px
  tall, and arrows in a loop toy were 24 px targets.
- **Its companion essay:** chips are 32 px tall, a slider is 16 px, and three torus figures are blank without JavaScript.

## Provenance

Built 2026-10-20 while retitling and rewriting an essay The author said
"interactivity is a little clunky", asked for hover cards that show examples, behaviour and attributes ("illustrate,
show don't tell"), for drawings that follow molecular-biology conventions, and for a periodic-table shorthand.

Sources:

- [Bret Victor, Explorable Explanations](https://worrydream.com/ExplorableExplanations/)
- [Hohman et al., Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles/)
- [Data Stories 103 with Nicky Case](https://datastori.es/103-explorable-explanations-with-nicky-case/)
- [How To Explain Things Real Good](https://href.leiden.digital/entry/38), a third-party summary of Case's talk
- [awesome-explorables](https://github.com/blob42/awesome-explorables)
- [Red Blob Games](https://www.redblobgames.com)

Posts on X were not reachable through search engines.
