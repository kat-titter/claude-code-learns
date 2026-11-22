---
name: figure-design
description: Designs figures that read at a glance - charts, plots, maps, timelines, diagrams and Mermaid flows, static or interactive - with labelled axes and units, a key outside the plot, nothing overlapping and one scale for spacing and size. Use when making or reviewing a figure, placing a legend, fixing overlapping labels or cramped panels, or drawing a flow diagram.
when_to_use: Before drawing any figure; when a legend covers data or does not say which mark is which; when a diagram's labels are unclear. Molecules, cells, micrographs and mechanisms go to science-figures.
---

# Figure design

A figure answers its question without the reader hunting: what is measured, which way is good, which mark is which.
Start from the defaults; depart from one only for a reason the figure itself shows. Drawing the science inside a
figure - molecules, proteins, cells, micrographs, mechanisms - is science-figures.

## Gotchas

- **Overlapping categories are lines under the total, never a stack.** When a source counts a death under every drug it involved (the CDC's opioid, fentanyl, methamphetamine and cocaine series), the categories sum past the total, so draw each as its own line beneath the all-cause line and let a hover card give the month's counts; say once that a death with two drugs counts under both (a public-health dashboard's trend charts, 2026-11-08: asked for "stacked, colour by drug", shipped as lines with the reason).
- Legend keys of different kinds in one row (dots beside a shaded band): one row per kind of mark (§2). Each row sits under its own minimal title ("fill", "left to right"), its keys below the title, never trailing it.
- A legend that shows colour when lines differ by dash: draw each key exactly as its mark is drawn (§2).
- An axis that names a quantity but not its meaning ("1 = perfect agreement", what each PC is): say it on the axis (§1).
- Mermaid defaults (dark fills, every label on a node): lighter fills, and decide which labels belong on edges (§5).
- A molecule, protein, cell, micrograph or mechanism in the figure: how the science itself is drawn is science-figures.
## 1. Defaults

- **A new plot form starts from three praised examples of it** (work-practice §2): read how each labels,
  colours and annotates before drawing the first one. Read them with computed styles, not a text fetch: a web fetch
  returns markdown and loses every size, colour and margin, so open the page in the browser pane and run one DOM probe
  (font sizes of body, headings, captions and svg text; fills and strokes used; column width; radii and shadows) plus
  one half-scale screenshot per page, and write a one-page table of URL, what it does and the technique to adopt
  (a peptide explainer, 2026-11-05: two fetch agents came back "not read" on type and colour for every site).

- **Every figure says what its marks are**: what a dot is (one well, one plate mean), n per group, what the error bar
  shows (SD, SEM, 95% CI), in the caption or a line under the title ("individual wells plotted, plate mean as the large
  dot; SD error bars"). (A 2023 screening talk annotated every plot this way.)

- **Axes with labels, always.** A line, ticks on round numbers (1, 2 or 5 × 10ⁿ) with values, and a label with its
  unit and which way is good: "agreement with first answers (1 = perfect)". Learned axes without units (PCA, t-SNE, a
  map) get a small two-arrow indicator in a corner naming each direction, and name their top loadings in plain words
  (full list on hover). A reader asked for "full axis with ticks" once a map's axes became real scores (a DJ tool, 2026-10-20).
  An axis title must be true for every series on it: "agreement with its June answers" fit two labs of eleven; "agreement
  with first batch" fits all (a pitch deck, 04b review, 2026-10-25). Same for a label beside a mark: anchor it to the marks it
  names, clear of others that do not qualify.
- **Every y axis names itself in plain words and says what one value means**, even on a talk slide and on each axis of a
  two-axis plot: a bold title along the axis, its colour matching its series, and a short second line "1 = as far as
  another lab", "1 = same as first batch". A long rotated title gets cut, so keep it short; placement follows the house style (a house-style skill may set it: rotated along the left axis). (a pitch deck, 04c,
  2026-10-26: "y axis should always be labelled, explain simply".)
- **Row and column labels sit outside the data region.** A table or heat map keeps one line per row: its label to the left of the cells, the column labels above them, never a label line between rows. Row labels are right-aligned to the data's edge, a short equal gap from what they name, and aligned to its line (a DJ tool's first screen, 2026-11-05: "transitions, sound labels right align closer to the thing"). When columns get narrow, stand the column labels upright rather than wrap the rows (a DJ tool's swap list, 2026-11-05: "table row and col labels should be outside of table region"). A heat map shades every step of its scale, low to high, so strong cells read as clearly as weak ones ("balanced heatmap").
- **Two units on one axis: the primary unit bold, right at the tick; the secondary small, one step further out.** No unit words repeated on every tick; name the units once in the legend (a DJ tool's takes table, 2026-11-05: "bar and time a bit cluttered, bold should be closer to axis tick"). Nothing clipped or cut with an ellipsis: wrap or shorten instead.
- **A sparkline or an arrow between numbers carries its axes, or says it in words.** A squiggle with no axes and "125 ~ 135 → 130" read as noise; say it in
  words, each number named ("125 in · 135 peak · 130 out bpm"), or draw a real figure with axes (a DJ tool's set cells, 2026-11-06:
  "this little squiggle, it's hard to read. It doesn't have axes ... I don't understand the 135 arrow to 130").
- **Label in place first; a legend goes below, two rows at most.** Name each part where it is drawn (stem names on their rows, A and B at
  the line's end, "switch" on the axis, the drop at its stick); only what cannot be named in place goes in a legend, under the figure,
  under it rather than above, at most two rows, with any explaining sentence moved to hover. A table of small
  pictures follows the same rule;
  unrendered or suggested items are empty rows of the same table, not separate cards. (a DJ tool's about page and takes table,
  2026-11-06: "oh god i hate this legend. should be below figure, think carefully about where each legend is needed (next to the
  thing it depicts), convention is below, 2 rows max"; replaces the 2026-11-05 header-band rule.)
- **A timeline is drawn to scale.** Time runs on a true axis (a pitch deck, 02a: 36 px a year, newest at the top), year
  labels at each boundary, one segment per stint sized by its years, the name and what was done there in a few words
  (the work, not the job title: "electrophysiology", "tau immunotherapy");
  a stack of equal rows with year ranges hides that one stint was a year and another four (2026-11-10: "use
  realistic y axis time scale. brief text role @ each institution okay").
- **A key shows, it does not explain.** Each entry is the mark drawn as it appears plus a name of a word or two;
  a sentence about a mark ("bar: distance, in plate spreads") means the figure is not carrying its own meaning, so
  put the meaning on the mark instead (ticks on a bar for its unit, the unit label above a scale bar) and cut the
  sentence. A key glyph stands for the whole class, so it carries no single item's label (a numbered ring in the key
  read as "lab 7") (a pitch deck, 04b, 2026-11-09).
- **Every figure has a legend, outside the plot region, below by default.** Its own band under the x-axis label,
  left-aligned with the plot, referred to by name ("the key below"); on the right only now and then, for a short, wide
  plot; two to four lines can be labelled at their ends in the right margin instead. The data area holds only data. A
  key in the reader's notes alone does not count on a slide (a pitch deck, 2026-10-26: "figures: always have legend,
  prefer position under plot, maybe on the right (rarer)"; 03b's shade key was reader-only, 04b and 04c had none).
- **Nothing overlaps**: text on text, text on marks, marks on the key, labels on guide lines. Reserve room first
  (margins sized for tick labels, axis titles and the legend band), then place; nudging afterwards drifts. An animated
  figure is measured over its whole cycle: size its box from the largest extent any frame reaches, and sweep the frames
  for the gap to its neighbours (a peptide explainer's hook, 2026-11-17: a 3D turn rose into the byline, "separation of
  elements is important"; the box now comes from the turn's extent, 66 px clear in every frame). Measure with
  page-legibility-check at 1280 and 400 px, light and dark.
- **Every element on one size and spacing scale** (section 3).

How the defaults look in common tools:
```python
# matplotlib >= 3.7
fig, ax = plt.subplots(layout="constrained")
ax.set(xlabel="dose (µM)", ylabel="cells per well")
# the legend gets its own band below the plot
fig.legend(loc="outside lower center", ncols=3, frameon=False)
```
```python
# plotly
fig.update_layout(xaxis_title="dose (µM)", yaxis_title="cells per well", margin=dict(b=120),
                  legend=dict(orientation="h", x=0, xanchor="left", y=-0.22, yanchor="top"))
```
In SVG or D3, size `margin = {top, right, bottom, left}` for the labels and the legend band, draw the plot in one `<g>`
and the legend in its own `<g>` translated below it. Mermaid diagrams have no axes; edge labels carry the meaning
(section 5).

## 2. Keys, titles and edges

- **One row (or group) per kind of key**: points, lines, shaded regions and glyphs each get their own, in the figure's
  order, each drawn exactly as in the figure (shape, size, colour, opacity, line style) beside a short plain label.
  A text note ("dashed: activity") is not a key: draw the dash in the series' own stroke. Stack rows on a narrow pane
  rather than letting one row run off the chart (an essay, 2026-10-25: "legend should show line style"). Take each
  swatch's colour from the same token as its mark (a DJ tool, 2026-10-27: "set path legend color does not match pink").
- **One word per legend label**: the mark's noun, singular ("vocal", "drop", "bar", "kick"); the rule behind it ("every 8th bar
  starts a phrase", "B minus A") goes in the item's hover card, never a second line (a DJ tool's takes legend, 2026-11-06:
  "prefer 1 word legend like bar, kick").
- **Every small figure keys itself**: a key under each repeated picture, naming only the marks that picture draws, in one
  line of short words; a shared key above a grid of them goes unread (a DJ tool's take cards, 2026-10-27: "even small plot need
  legend! legend move from above to associated with each take"; "2 line legend").
- **The key lives with its figure, never in a page-wide legend up front.** A strip of every mark the page uses (an
  evidence ramp, line styles, outlet boxes) before any figure is read before it means anything; each figure, plot or
  table keys only the marks it draws, beside it (a peptide explainer, 2026-11-06: "this legend probably not needed up here,
  figure/plot/table should be associated with the relevant item").
- **The key sits below the illustration, outside the plot, and out of the caption prose.** Its own strip between the
  drawing and the caption, with the hairline rule *under* the key so the key belongs to the picture and the line
  separates it from the text; swatches threaded through caption sentences make the caption unreadable and the key
  unscannable (a peptide explainer, 2026-11-05: "color and element legends should be below illustration, outside of plot
  region, not in figure legend text"; then "should actually be above the line").
- **Figure and slide titles are the takeaway, in scientific prose.** A declarative sentence naming the variable and the direction, supported by what the figure shows ("Skin permeability of peptides falls with molecular mass"), never a question or a play on words (a peptide explainer, 2026-11-20: "What crossed human skin in the lab" → "prefer scientific title: skin permeability of peptide(s) varies by x ... key takeaway which is supported by figure content"). Prose and chapter openings keep their voice; titles carry the finding.
  A rewritten title is checked against the heading above it: where a heading was written to carry the claim the
  title does not, the pair starts saying one thing twice (a peptide explainer, Figure 25, 2026-11-20: its chapter head
  already said "the label, not the molecule", so the title took the testing gradient instead). And check the
  claim against the drawing while rewriting: three of its titles named a variable the figure never drew (a cost
  on an evidence ladder) or the wrong model (rodent, where the panel was HUVEC and chick CAM).
- **Label collisions with a shape are invisible to a legibility checker**, which compares text to text. When a term
  must stay (the field's word), move the drawing, not the word: shift the ligand out of the label's lane, drop the
  signalling chain, right-anchor the side labels clear of the helices. Then look at the render.
- **A mark's shape says only what it means**: an arrow between two lanes reads as motion from one to the other, so an event on
  one lane is a plain stick (a DJ tool's drop, 2026-10-27: "arrow is confusing, looks like point up from track B to A"; "just glow
  stick"), flat, its glow on the edges rather than a shaded tube ("too 3d, edges glowier, more 2d").
- **Say what one mark is.** Every scatter, map or dot chart names its unit of observation in the key: "· one plate
  ● lab centre", and what a larger or ringed mark stands for. A reader of a map of eleven labs asked "one point = one
  lab centroid?" (a pitch deck, 25 Oct 2026). A count in the headline equals the marks drawn for it, and a different kind
  of thing gets its own mark and key row: a slide titled "three stations" drew the field hospital with the stations'
  cross (a drug-mechanism deck, 2026-10-27: "burn slide: actually shows 4 stations?"; Rampart became an H).
- **One colour per class, checked as a set.** No other key entry wears a class's colour (a "new" ring or a "deaths" size
  in the opioid red read as opioids), and the set is checked for distinguishable pairs on the surface the marks sit on, all
  pairs for a map or scatter; past three classes, a label in the list or popover carries what colour alone can't
  (a public-health dashboard, 2026-10-27: "distinct, unique choices ... each drug class diff color").
- **Swatches sit whole inside their box**, inset 1 to 2 px; a shape flush with the edge reads as cropped. A flat-based
  shape (a mound on an axis) gets its baseline drawn in the swatch. Re-check the exact spot a reader flagged, at real
  size (a DJ tool's set key, 2026-10-20: "this is 2nd time i ask avoid bottom row crop").
- **Group rows and space by group**: what the marks encode, then their states, then guides; a small gap inside a group
  and a clearly larger one between groups (8 and 21 px). A vertical guide gets its own row, or it reads as a separator.
- **Label lines directly when they share a plot**: each line's tag right-aligned at the plot's edge, level with where
  that line starts and in that order, nudged apart so none overlap; a strip's own name the same way; when the tags also
  toggle their lines, the tag is the key (a DJ tool's profile plot, 2026-10-26: "legend tags should be right aligned and close to
  line"; "sort top to bottom based on first song").
- **A breakdown by category is its own figure**: a pie or donut whose slices differ in colour and texture, its key
  naming each category's share and listing its members; hovering a category or a member lights them wherever else they
  are drawn. A per-item colour band along a time axis reads as a confusing legend (a DJ tool's genre view, 2026-10-26: "genre pi
  chart: color and texture legend, enlarge. list each song and highlight in set on hover").

- **One clear edge per figure block**: the key and the caption share a left edge and everything else flows inward
  from it; nothing sits proud of that edge. A key pinned to the figure box while the caption is inset gives the
  block two competing left edges and reads as misalignment. Measure it — compare each key's first swatch to its
  caption's left edge — rather than eyeballing (a peptide explainer, 2026-11-05: "vertical alignment of elements, 1 clear
  edge, everything else flowing inward. legend probably inward").
  The drawing's own labels obey the same edge: a figure that bleeds wider than the text column still starts its
  leftmost label on the caption's edge and clips nothing on the right. Measure every figure on the page (leftmost and
  rightmost text box against the caption's box) each publish, because fixing one figure leaves the rest (a peptide explainer
  Figure 17, 2026-11-06: "i thought we talked about width and margin management?").
  The caption and key run the figure's width too: left and right edges on the drawing's content edges, while running
  prose keeps its own measure. A 640 px caption under a 780 px drawing is two right edges. Check both sides per figure,
  and when a sibling document gets this fix, port it the same day (a peptide explainer, Figure 1, 2026-11-06: "for the love
  of god i thought we talked about figure text width managemnt 3x now", an hour after doc 1 got "fig legend text
  same width as figure"). Measure the text's own line extents (a Range's client rects), never the element's box:
  a caption box widened with padding passes an edge check while its words still stop short (a peptide explainer: the check
  reported every figure inside its caption while the reader saw two right edges).
- **A wrapped key fills its last row**: a run of key entries fills its last row at least half, or it reads as an
  orphan. Three levers, in order: give the key more width (align its left edge with the caption but let it run to
  the figure's right edge), move the repeated noun into one group label so each entry drops it ("regulated,
  trial-backed outlet / licensed, untested outlet" → label "outlet" + "regulated, trial-backed / licensed,
  untested"), and at phone width lay the key out as two even columns, where a last row of one is exactly half.
  Check it by counting items per row, not pixels (a peptide explainer, 2026-11-05: "avoid straggling rows. try to fill
  last row at least half of full"; 4 stragglers at 1280 px and 7 at 400 px went to 1 and 0).

- **A legend of several rows is a grid**: each row named in one column, so every row's first key starts at the same x, with
  a clear gap between rows, and the rows in the order their marks are stacked above them (a DJ tool, 2026-10-27: "first key
  should be aligned vertically"; "sound legend above transition legend since sound visual elements above transitions").

## 3. Spacing and sizing

- **One type scale**: title > axis label ≥ legend ≥ tick labels, nothing under 11 px as rendered on screen (7 pt in
  print). Check figure text as authored size × slot scale. Rendered px = authored size × block width ÷ viewBox width, so a wider
  viewBox makes labels smaller: the levers are the authored size or the block, and size the block to the type when a
  larger authored size would push labels off the drawing (a peptide explainer, 2026-11-20: a brief said "widen a viewBox
  rather than shrink type", which is backwards; 796 px was the narrowest block keeping every label ≥ 11 px at 1000 px).
- **One drawing hand per page**: author each panel at a viewBox width that renders at scale 1 in its slot; shared
  arrow markers; two stroke weights (about 1.4 for rims and guides, 2.2 for arrows and data lines); one node style.
  Case: labels drifted 11 to 18 px with slot scale and arrowheads differed 2.4× across panels (2026-10-24).
- **Margins hold what sits outside the plot**; the gap from plot to legend is about one tick-label height; tick steps
  clear their labels (`step × pitch ≥ 1.5 em + 2 px`).
- **Marks fit their density**: points shrink as the count grows and at phone width; guide lines break around marks and
  labels; a number label tries right, left, above, below, then further out, and takes the first clear place.
- **Figures share the reading column's left edge**: keys, controls and captions left-align with the text; a solo panel
  fills the content width. Case: captions at 274 px beside text at 281, a 460 px plot with 141 px empty each side.
- **Captions name, figures speak**: cut a caption to number and title when the figure and the sentence above already
  say the rest; keep clauses that carry an undrawn fact.

## 4. Many channels on one plot

- **One variable per channel**: shape for a category; size, colour and opacity each for one measure, its good end big,
  bright and solid, with both ends said in the key ("lower → rank 1"). Let the viewer pick each channel's measure when
  several compete.
- **A sequential ramp from the work's own tones**, ordered by lightness, so it reads as its own scale rather than as a
  colour with a meaning elsewhere; a symbol that means something elsewhere keeps its form.
- **Options scored on several features are a ranked heatmap table**, not a sentence per row: rank and score first, the
  sort named in the header ("fit ↓"); one square cell per feature with its value printed inside, in an ink that flips
  with the fill; one sequential scale whose good end is the same in every column (a cost flipped so high is good), its
  key below naming both ends ("0 = worst here, 1 = best"); the current choice as a reference row on top; the words on
  hover (a column head says what it measures, a cell its raw value). From the correlation matrix take square cells,
  printed values, like columns side by side and a diverging scale centred on 0 for signed values; and correlate the
  features across the options once, since two that move together count one thing twice (a DJ tool's swap list, 2026-11-03:
  "too much text. this is rank order?"; "cells (square) like table format or heatgraph figure. something learn from
  correlation matrix?").
- **Views that share time share one x-scale and one left gutter**, exact to a pixel at 0, a midpoint and the end.
- **Many measures as lines on one plot**: the three that matter most are on at first, ranked from the reader's own words
  where they said any, the rest a chip away; each line's own y axis appears for the line under the pointer, drawn in that
  line's colour and dash, with its unit; the hover names the item and its value with the unit, a dot on its point, the
  other lines dimmed (a DJ tool's profile plot, 2026-10-27: "clever, clear way to show multiple y axis (same design as line) with
  units"; "3 most important automatically toggled on"). Sort the points by x before smoothing: an order newer than its times
  drew a line that ran back on itself.
- **Merge before adding a panel**: two measures that share an x axis go on one plot with a y axis each side, each axis in
  its line's colour; one horizontal threshold line serves every series it applies to (a pitch deck, 2026-10-26: "clever
  design cohesion tricks like one plot two y axis, single horizontal threshold").
- **Variants that differ a little are drawn to be compared**: stacked on one shared time axis, the same marks in the same
  order, the stretch where they differ marked (a band over the bars where take B departs from take A), and every bar and
  shade named in the key (a DJ tool's take cards, 2026-10-27: "white bars are vocals, what each gray shaded region is
  unclear. how to best help user grok small differences between takes").
- **To show that one measure predicts another, stack them on one time axis.** The cause on top, the effect below, each
  series joined in time order, and the flagged span shaded across both so the eye sees them move together. A scatter of
  one against the other hides the order and the moment it happened. (a pitch deck, 04b, 2026-10-25: from a drift-vs-agreement
  scatter to two panels, controls' drift above and drug answers below; "nice update to that slide!")
- **One scale per drawing, and every enlargement says by how much.** In a mockup or elevation, measure each part's
  pixels per real unit (a person, a print, a sink) and bring them to one; an enlarged inset carries its factor, measured
  from the drawing ("× 4.6"), beside the lines that join it to what it enlarges (an art piece's sink mockup, 2026-10-26: "be as
  consistent with scale as possible, show when zoomed and by how much").
- **Open on the view the reader cares about**, a learned map one pick away; micrographs carry a scale bar with its
  true unit (controlled-comparisons).
- **Nested units, drawn nested and to scale, each level with its number.** When a figure leans on a hierarchy (cell in
  well in plate in lab), show the levels as concentric rings in one unit with the count or spread at each (a pitch deck, 04a,
  2026-10-26: "one well ~220 cells; 1x wells on a plate; 1.6x a lab's batches; 6x between labs", asked as "quantify all
  nested loops/space").
- **A projection for the eye carries the measured verdict beside it.** A 2-D map can put a point somewhere that looks
  wrong; draw the deciding numbers next to it as bars (a pitch deck, 04b: the new batch looked out of distribution on the
  PCA, so "own lab 2.8x, next lab 4.4x" became two bars in the certificate).
- **Time as a shade, a state as an outline.** Points in time order run light to dark in one hue, the same shade for the same
  item in every panel so it can be followed across; a flagged state is a ring around the point in a colour the palette
  already has, not a new fill. The key shows which way time runs: the ramp drawn as an arrow, with its first and last
  dates (a pitch deck, 04c: lab 2's batches by date, the key "a batch, June to October (13)" on a light-to-dark arrow, a
  pink ring where out of distribution; 2026-10-26: "red circles, no date flow direction indication?").

- **A pie's labels sit beside their own slices**: a slice facing right is labelled on the right, facing left on the left
  (rows balanced between the two), each header level with its slice's middle, the left column the right one mirrored so
  swatches and numbers line up next to the pie; leaders run level, or out to a knee, upright and across, never diagonal
  (a DJ tool's genre pie, 2026-10-27: "balance, alignment of similar elements, labels next to the thing"; "elbow connector or
  straight line, not diagonal"). A hovered slice pops in its own colour, pulled out a few px and brighter, rather than
  painted white ("pie chart highlight white feels unbalanced and jarring. have the piece pop").
- **Time is drawn to scale.** A timeline puts each event at its real date (1970, 2000, 2010, 2026 spaced by years), labels
  under their marks or a row lower when a neighbour is close, joined by the pie's leaders: straight, or a real knee, never a
  pixel's jog (a DJ tool's process page, 2026-10-27: "timeline use realistic spacing. learn from pie chart elbow/straight connectors").

## 5. Diagrams and flows

- **In a flow diagram, nodes are things and edges are what happens.** Actors, tools, files and stores are nodes;
  actions, triggers, conditions and timing label the edges; close the loop back to the actor it serves. Name the real
  thing (`feedback-nudge.py`, not "feedback hook"), give a category one real example, and leave a group title off when
  the edges already say what the group holds (claude-code-learns README, 2026-10-25). A person is drawn as a person
  (head and shoulders), not a box, placed where they act, so the reader sees each touch a human makes; when Mermaid
  cannot draw that, draw the SVG by hand (claude-code-learns, 2026-11-05: "show human in the loop ... pref as human";
  "something better than mermaid?").
- **When a process names several kinds of things, draw how they relate before showing examples of each.** One small
  diagram puts every kind in sequence with a distinct mark (solid, dashed, plain), and labels each with what made it
  (the input it came from); then the examples. (A generative pipeline, 2026-10-25: dreams, waypoints and walk frames,
  each labelled with its prompt or blend: "how are dreams, waypoints, walks related? how is prompt connected to image?"; then carry the same marks onto every example image, so a reader can match picture to role: solid silver for A, solid gold
  for B, a split outline for a blend; and box the region a close-up comes from, with its zoom.) When examples illustrate points on a line or path, set each image directly above its point and
  label once, on the line: a second row of the same labels under the images is redundant (2026-10-26: "redundant dream A,
  waypoint labels. image should be above line with points").
- **A second accent earns its place by carrying one meaning** everywhere it appears, named once in the key (loop table:
  lavender amplifies, amber brakes).
## Related

science-figures (molecules, cells, micrographs, mechanisms), page-legibility-check (measure overlaps, contrast and
size), design-practice (the page, colour), app-design (interaction), interactive-figures (figures that respond),
controlled-comparisons (fair scientific comparisons, scale bars), the person's style skill (taste).

## Provenance

Split from design-practice on 2026-10-25 when it passed 260 lines, with the legend, axis, channel and diagram
guidance moved here intact. Split again on 2026-11-21, when the molecule, cell, micrograph and mechanism guidance
went to science-figures and this skill kept the chart and diagram craft. The defaults in section 1 came the same day: "always show axis and labels, no overlapping
content, always show figure legend outside of plot region, refer below, consider spacing and sizing of all elements".
