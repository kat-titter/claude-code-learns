# A page that feels made (the audit checklist)

From a deep audit of a long essay page (seven lenses, 92 verified findings, 2026-10-24). Each item is a check with its case.

- **Budget the first screen before polishing anything.** Measure the masthead's share of 1280×900 and 400×800; put the
  figure's one instruction and the argument's first sentence above the fold; give screen one's only bordered object to
  the figure, not the links. Case: a 336 px masthead (37 %) with three pill buttons read as the call to action while the
  hero's "drag to turn" sat at y 897.
- **Check computed styles, not the stylesheet.** A rule on a parent selector can silently beat a label class. Case:
  `.text > p` (0,1,1) beat `.kicker` (0,1,0), so ten 12 px section labels rendered as 19 px serif second titles.
- **Audit colour by computed paint and by meaning.** Count every element in each hue and name what each means; colour
  that paints structure, chrome or "first of its row" is drift. Case: about 950 lavender elements against 55 amber, with
  only 37 "+" signs meaning amplify, and braking loops drawn lavender one caption after "lavender amplifies, amber brakes".
- **Meaning-carrying strokes and text use the contrast-safe token**; the pale token is for fills and wide shapes. Case:
  arrows in pale lavender on the plate were 2.66:1; the same arrows in the text token, 5.4:1.
- **Figures follow figure-design**: one drawing hand per page, the reading column's left edge, captions that name.
- **A hover card peeks, a tap card reads.** Hide the long sections unless pinned; measure the tallest card against its
  stage at both widths; on phones a pinned card is a fixed sheet (≤ 42vh, top or bottom by where the tap was) so the tapped
  thing stays visible; Escape and an outside tap dismiss. Case: 30 cards of 378 to 725 px in a 435 px stage.
- **Every pressable thing has rest, hover and pressed states** with the same mark, about 150 ms of ease, and swaps panels
  without changing height (stack panels in one grid cell, toggle a class). Case: funnel rows and loop nodes computed
  identical at rest and hover; the panel jumped 43 px per click.
- **Palette discipline includes browser controls.** Style range inputs with the page's tokens. Case: the UA slider track,
  rgb(59,59,59), was the darkest paint on the page.
- **Type uses tokens only**; phone overrides add no new sizes; figure text is checked as authored size × slot scale
  against the 11 px floor. Case: 10.5 px tile text; 18 and 26 px phone overrides; citation marks scaling 12 to 16.6 px.
- **Inline touch targets grow with a pseudo-element inside the line box** that never overlaps a sibling's glyph (aim for
  the 24 px inline floor; 44 px is for standalone controls). Case: −6 px vertical and −3 px between siblings gave 25×29 px
  citation targets without cross-talk; −14 px would have caught taps from the lines above and below.
- **Each fact once across prose, caption, key, panel and header** (Text); three parallel readings become a list with
  inline bold leads. Case: a result told five times, "2 × 2 = 4"
  three times on one screen.
- **A page ends with something to do**: a comment route and a way back to the top; a "draft for comment" token links to
  the venue. Case: the page ended on reference 38 and the token was a plain span.
- **Verify a proposed fix live** at both widths before recommending it; a fix can break the constraint it serves. Case: a
  50vh sheet covered the tapped tile; a nav inside a p was closed by the parser.

## Labels and styling

- **Labels in a set are even in length and fit on one or two lines**: column heads, legend entries, axis names and
  card titles in one group read as parallel phrases of about the same length ("measure cells", "normalise plates",
  "reference data", "every lab, over time"); rewrite any label that wraps to a third line, and keep the group on one line
  each when it fits. (a pitch deck, 08, 2026-10-26: "pay close attention to harmony text length. try to fit all text labels on
  1 or 2 lines".)
- **Styling balanced and intentional, edges aligned**: count bold, italic and coloured runs per view, and keep each for
  one job (bold for titles and the key number, not labels); line up near misses (two left edges 4 px apart read as a
  mistake); a key starts under the first column it describes, not at the row labels (a pitch deck, 05, 2026-10-26).
