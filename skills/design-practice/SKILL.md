---
name: design-practice
description: Guides the design of pages, documents and slides - composition and balance, short text with each fact once, one meaning per colour, one symbol and icon per thing, numbers on cards and true phone layouts. Use when designing, reviewing or polishing any page, deck or screen layout, or on "cluttered", "too much text", "redundant", "not aligned" or "show, don't tell".
when_to_use: Before building a page or slide; in a design review or audit. Apps go to app-design, figures to figure-design, measuring to page-legibility-check.
---

# Design practice

How any page, document, deck or screen is laid out and worded. Seven principles come first; every rule below is a
case of one, tagged P1 to P7, with a few words of where it came from. Long cases and the words behind them:
[references/cases.md](references/cases.md). Apps and interactive parts add app-design. Start with a quick critique
(first impression, usability, hierarchy, consistency, accessibility), write the plan, then build; measure with
page-legibility-check. For a person with a style profile, read it too (`<name>-style`).

## Principles

1. **Every element earns its place.** Say in a sentence what it tells the reader; if another element says it, one goes.
2. **One thing, one form.** Each fact, colour meaning, symbol, icon and style appears once and means one thing everywhere.
3. **Nothing leaves the reader asking "of what?"** Every number, table, fraction, timing and new term names its whole.
4. **Meaning in the medium that carries it, words last.** Position, marks, plots and icons show; words add the rest.
5. **Nearness and alignment claim relation.** What is used together sits together; what is unrelated gets its own shape.
6. **Few measures, held exactly.** One left edge, one spacing scale, one type scale, full rows; measure the paint.
7. **The real thing over an imitation.** Real marks, real examples, real physics, the colour the browser paints.

The canon behind them, linked rather than copied: P1 is Tufte's erase (tufte-principles §3), P3 his "compared to
what?" (§1), P4 words on the data (§6), P7 drawn truthfully (§2); P5 is Gestalt proximity (hci-principles §5). Owned
elsewhere: order follows how the reader builds understanding (storytelling); work lands once (work-practice §6).

## Gotchas

- **A hero graphic gets three or four concepts side by side** before one ships (P7); refining one concept three times
  leaves "did we test versions?" open (a peptide explainer masthead, 2026-11-17).
- **Passing every check is not a design** (P1). Checks fail only on contrast, overlap and size, so each fix can add a
  device. Set a budget before building: two faces, five or six sizes, ink plus one highlight plus the data hues, a few
  component kinds, one drawing style, no shadows or gradients. Subtract until it holds; run `design_budget.py`
  (a peptide explainer, 2026-11-05: 55 colours to 21).
- **Uneven cards leave cold white blocks** (P6): put them on one row grid (CSS subgrid) so rows line up and the figure
  row takes the spare height, and tint each card by its meaning (a pitch deck, A4, 2026-11-09).
- **Fine at 1280 px, broken at 400 px** (P6): measure both widths with page-legibility-check before calling it done.
- **Anything public is read at its rendered width before it ships** (P7). A checker measures contrast, overlap and
  size, not whether a two-column block folded its second column under its first or a name broke mid-word. Where the
  width is fixed, make it a check rather than a habit (a README file map, 2026-11-21).
- **One fact told by a chip, a pressed button and a letter** reads as polish to the builder and clutter to the
  reader (P2): keep the one or two the reader acts on (Text).
- **Invented symbols collide** with chemistry or a nearby key (Ck, Cc, Pu) (P2): run check_symbols.py (Text).
- **One outline colour doing two jobs** (P2): one style per role (Text).
- **After a deploy, a browser may show the cached page** for up to ten minutes: say so, and that Cmd+Shift+R loads it.

## Composition

- **Pick the format by what the information is** (P5). A result to see is a numbered figure; a key the reader looks things up in is a table caption or legend beside what it decodes; a definition is a hover; an aside is a fold; a comparison is a table row. A drawing that only explains a scale used elsewhere is a legend, not a figure (a peptide explainer ladder of proof, 2026-11-21: "this should be table, not figure? its more of a whole-text legend then a standalone result figure ... remember to choose right place and format to convey information").
- **Group by what the reader does with it** (P5). Things used together sit together and share one control; a drawing
  and its name share one cell, flush. Every line belongs to something: inside a card, under its figure at the figure's
  left edge, or in a fixed header or footer slot; after a cut, move what remains next to what it describes (a DJ tool set
  tags, 2026-11-06; a public-health dashboard, 2026-11-08; a pitch deck, 2026-10-15).
- **Shared alignment claims a relation** (P5): unrelated blocks get their own shape, such as a stat row of three and
  then the reasons as a term list (a pitch deck's one-pager, 2026-11-01).
- **Comparable items are rows in a table, not cards** (P5): one row each, the same element at the same x, hairlines
  between rows, labels outside the data. Cards only for one-off content (a DJ tool, 2026-11-05 and 11-06).
- **Air between elements, tight inside them** (P5): a box hugs its content and the sections around it get the space;
  negative space separates groups and keeps every element clear of the edges. A timeline is one line with a tick per
  stage, the label above and the plan below (a pitch deck's one-pager, 2026-11-01).
- **Vary the organisation, and give the group a centre** (P5). Things sharing one idea sit at a diamond's points
  around a small element naming what they share, a hairline from each. The empty quadrants carry the eye; shrink the
  centre until its edges run through empty space (a peptide explainer masthead, 2026-11-05).
- **Connect related elements with lines** (P5): a short leader from a callout to its mark, numbered timeline points
  dropping to their cards, which beats matching by colour alone. Only where the two sit close; start each leader on the mark where it is now, redrawn every
  frame on a moving figure; icons large enough to read (an art piece's ring and a pitch deck, 09, 2026-10-26).
- **One left edge, two measures, one rhythm** (P6). Every heading, paragraph, caption, key, list, table and rule starts
  on the line where the drawings' own content starts. Words stop at the reading measure; keys and tables run to the
  figure band's content edge. Gaps come from the space scale, the same in every section. Inset with a margin, never
  padding, so a box and its border span only its content; a rule that must start on the line is a pseudo-element.
  Write the two measures down where the styles live, and measure each block's painted left edge at both widths,
  expecting one number (a DJ tool's about page, 2026-11-06;
  a peptide explainer, 2026-11-05: four edges became one).
- **A row of entries fills its rows, or it is one row** (P6). Pick a column count that divides the items: four go
  1 x 4 or 2 x 2, six go 1 x 6, 2 x 3 or 3 x 2. `repeat(auto-fit, minmax(Npx, 1fr))` makes the straggler; set
  `repeat(4, minmax(0, 1fr))`, shrink the gap until it fits, switch to another divisor at a breakpoint, and count per
  row in the render. A count no grid divides becomes rows with the name in its own column, set per list with a
  quantity rule (`dl:has(> div:nth-child(4):last-child)`) (AMG 900 explainer, 2026-11-17; a peptide explainer, 2026-11-20;
  wrapped keys: figure-design).
- **One spacing scale and one type scale** (P6), as tokens, plus a few deliberate proportions for the main splits
  (picture to text, main to side column, row to gap); near 1 : 1.6 reads calm.
- **Balance weight in every view** (P6): share left edges, align label columns. After a cut, let what stays grow into
  the room, pictures flexing and side columns spanning the full height. Paired cards get the same parts. Text on one
  line shares one baseline, measured with a 0-height inline probe, not one box centre (a pitch deck, 02a, 2026-10-25;
  a DJ tool header, 2026-10-27).
- **Break lines at the sense** (P6). A headline fits one line or breaks at a clause, so no `max-width` or
  `text-wrap: balance` splits a phrase. A short paragraph beside another column takes `text-wrap: balance`. A dek
  that strands one word is cut to fit, and balanced where a phone wraps it. A screen page takes its printed measure;
  a heading wrapping under a right-hand column is shortened, its detail on the next line (a pitch deck FRO, 2026-11-01;
  resume, 2026-11-08 and 11-09; a public-health dashboard, 2026-11-08).
- **Body text breathes** (P6): line-height about 1.5, headings tighter, label-value gaps from the scale.
- **Type reads at a glance** (P6): body 17 to 19 px on a 45 to 75 character measure, five or six sizes as tokens, two
  families at most (a reading face, a mono for labels and readouts), figure labels 12 px or more so a phone's downscale
  keeps them above 11 (an essay, 2026-10-25).
- **A link shows where it goes** (P2): beside a name, link with the address itself (short, stable, the home that fits)
  rather than repeating the name as "open X"; on paper it still works (an art piece, 2026-10-26).
- **One doc, two media** (work lands once): a page that must also be a PDF or handout gets a print layout (`@media
  print`, `@page` size, running footers, live parts as stills, hover notes as a word list) in place of a second
  document, since two copies drift (an art piece Web doc, 2026-10-26).
- **Art pieces** (a mirrored pair or diptych, museum wall labels, a piece drawn to scale beside a person): read
  [references/art-pieces.md](references/art-pieces.md).

## Text

- **Break where the meaning breaks, at every scale** (P5). Chunk lines, blocks and pages along their natural separations. A two-line title breaks at its phrase boundary, after a colon or before a prepositional phrase ("Peptides: / messages, mechanisms, & money", "Frontier biotech / in first-class mail"), never inside a compound: use a non-breaking hyphen (`&#8209;`) so "first-class" is not split. At page scale (a PDF or print render) a page turns between sections, never between a heading and its first paragraph, a figure and its caption, or a table's header and its rows (`break-after: avoid`, `break-inside: avoid`); open the PDF and look at every page turn (a peptide explainer, 2026-11-21: "carefully consider where to make new line, in text, whole page ... such as in pdf render ... how things are chunked. try to follow natural separation").

- **Say each fact once, in the element where it is most useful** (P2): the set name in the header, the sample size in
  the caption, a fact on the element it describes (a flag about one take on that take). The same holds for controls,
  figures and geometry:
  - a line repeating its neighbouring control goes; the verb matches the gesture (drag, tap, click) and appears once;
  - three identical panels with different labels become one panel with the labels as rows; a small copy of a later
    figure goes, and so does a thumbnail repeating the text beside it;
  - a group label shows only where two groups meet; a mark every row shares goes;
  - in a figure, a key carries only marks the drawing does not label in place, and a label never restates itself;
  - one graph, one control and one name per thing on a page, and one look for that name wherever it appears, in
    text, chips, tables and figures (a peptide explainer, 2026-11-21: peptide names were chips in the intro and
    underlines in the figures; "consistency and formatting is super important")
  (a DJ studio, 2026-10-24 to 11-06; an essay, 2026-10-25; a peptide explainer, 2026-11-05).
- **One title and description style for every section** (P2): one size and face, the description stacked beneath at
  one measure; facts a table gives leave the description (an art doc, 2026-10-26).
- **Items in one list carry the same parts** (P2): every item has a subtext, or none does (an open call, 2026-11-19).
- **Siblings share one form of words, not just one size** (P2): labels that sit side by side (table headers, card
  titles, nav items, key rows) agree on capitalisation, part of speech and whether they carry a qualifier; read them
  across, not down (a README's tables, 2026-11-21).
- **Numbers in the field's standard style** (P2), APA for science: words for zero to nine in prose counts, numerals
  from 10, numerals always with units and time (2 minutes, 16 GB) and for every number in a comparison reaching 10, a
  word or a recast at a sentence start; labels, versions and display figures keep their form. A number and its unit never
  break apart: a no-break space (`123&nbsp;bpm`) or `nowrap` (an art doc, 2026-10-26; a DJ tool to-buy, 2026-11-03).
- **One symbol per thing, checked** (P2): each invented code is unique and differs from codes standing nearby (the
  companion page's key, the field the look borrows from). Assert uniqueness where symbols are generated and run
  `check_symbols.py` (loop table: Ck, Cc, Pu became Tk, Tw, Ps).
- **One outline style per role, on every image** (P2): if gold marks the new dream, a moodboard pick gets a dashed
  bone outline (an art piece, 2026-10-26).
- **Every table says what it is** (P3): a title naming its rows, a header of one or two plain words on every column
  (the row-name column too), never a header that wraps. The headers are siblings, so they take one form between them
  (an essay, 2026-11-19).
- **Say where a derived number comes from** (P3): "3,773 measurements of each image: size, shape, brightness,
  texture", not "3,773 numbers" (a pitch deck, 2026-10-25). **Every timing says per what**: "about 3 s a dream" (an art piece).
- **Illustrate the nouns a stranger meets first** (P3): a small icon and a two-word gloss where a term first appears,
  drawn once in a shared set and reused; a symbol is glossed and drawn on the structure itself, so gloss and mark
  match (a pitch deck, 04, 2026-10-25; a drug-mechanism deck and a DJ tool's process tiles, 2026-10-27).
- **A borrowed finding names its author on the slide** (P3): their words under the figure, then who and when, on
  stage and not only in the reader's layer (a pitch deck, 06a, 2026-10-25).
- **Short ledes, data over prose** (P4): a caption adds what the figure cannot show; a summary is a few small plots on
  the page's shared axis. Text beside them leads with one bold takeaway, then what the plots can't show (feeling,
  story, how it was seeded). Options with a reason sentence each become a ranked table of scored cells, reasons on
  hover (a DJ tool, 2026-10-26 to 11-03; the form in figure-design §4).
- **A grid holds phrases** (P4): a grid earns its form when each value is a fact the eye takes whole; once a cell
  runs to a sentence it is prose in a table's clothes, costing the scan it promised. A column repeating
  one line says it once under the figure and marks the exception; an outside party's name is linked, with what it
  offers (a peptide explainer, 2026-11-05).
- **A split names each share on its own segment** (P4): "artist 60% $9,400 | an art piece 40% $6,266", not a ratio and then a
  list (an art piece, 2026-10-26).
- **One phrase lit per headline** (P4): the headline in ink, the phrase carrying the claim in the accent, so the eye
  lands on the claim first (a drug-mechanism deck habit, a pitch deck, 2026-10-25).
- **A byline carries who, how to reach them and when** (P1): author, organisation, contact or site, date; reference,
  figure and word counts are bookkeeping (a peptide explainer, 2026-11-05).
- **Separate items with space, weight, size or alignment** when a style asks for a quiet page (P1); `check_design.py`
  lists separator characters and repeated phrases.
- **Three real examples beat a word list** (P7): one table of three cases in the field's own words, each with exactly
  what changes, reads as professional; a word list beside a history table reads as clutter (a DJ tool's process page,
  2026-10-27).
- **The field's own words** (P7, field-vocabulary); a person's own names for their things stay as they named them.
- **Generated prose reads its own numbers** (P7): edge values read like a person wrote them, "both at 123 bpm" and
  "none" (a DJ tool's about page, 2026-11-03).
- **Explaining a process, a method or a long argument** (a loop of steps, an overview beside its details, a methods
  tutorial, the hero figure, a scorecard): read [references/explainers.md](references/explainers.md).

## Icons and thumbnails

- **A mark earns its place by meaning** (P1): draw one only where it shows what words cannot (scale, a mechanism, a
  value, a state, a behaviour) or is a convention readers know (the GitHub mark on a code link). A pictogram beside
  every noun or a glyph on every row reads as busy, not impactful. Say in a sentence
  what it tells the reader; if the words already say it, cut it. Strong type can stand alone (an open call, 2026-11-19:
  31 of 48 glyphs cut).
- **One icon per thing, its word beneath** (P2): one small icon per function, and the same icon wherever that
  function is named again, lit together as the reader reaches it (an essay, 2026-10-25; an art piece's feed,
  2026-10-26).
- **An icon carries only the words it renders legibly** (P4): make the mark say it, such as two sets' waveforms
  overlaid in one round mark with the current one lit. A round crop reads as an identity mark; state comes from emphasis, and hover previews the click
  (a DJ tool header, 2026-10-24).
- **Warnings borrow safety signage** (P7): a broken rule is an ISO 7010 triangle, a place to look a GHS diamond, one
  pictogram and one home per kind; hover shows where it was found, a press opens its definition (a DJ tool flags,
  2026-10-26).

## Numbers on cards and chips

Direction, best value, units and comparisons on a card: read [references/numbers-on-cards.md](references/numbers-on-cards.md)
before putting a number on a card, chip or dashboard.

- **A page opens with three summary numbers at most** (P1), the ones that describe the whole (for a DJ set: track
  count, length, tempo arc); every other figure lives in its section or goes (a DJ tool's set block, 2026-11-06).
- **In a document read as prose, a number lives in the sentence that gives it meaning** (P1): stat-tile rows belong
  on slides and dashboards; keep striking numbers, cited, in their paragraph (a peptide explainer, 2026-11-06).
- **A fraction names its whole and what sets the parts apart** (P3): "3 of 8 presets hold the water still", never a
  bare "3/8"; the written form (3/8 or 3 of 8) is a house-style call (an open call, 2026-11-19).
- **A count repeated as words in every row becomes marks** (P4): the word once in the header, one to three bars per
  row, axis labels over sentences (an essay, 2026-11-19).

## Colour

- **One meaning per colour** (P2), inside a figure and across a deck, binding every mark in it: strokes, rules, rings,
  carets and icons as much as words. A verdict colour travels with a glyph; once a colour means something, it says so
  alone. Before calling a page done, grep the accent's hex and move every use outside its meaning to neutral ink
  (an art piece's feed and a pitch deck, 2026-10-26).
- **A companion page wears the app's state code and nothing of its own** (P2): series are told apart by position and
  value (A above B, two greys), the lit phrase by value. Count accents per figure with `accent_census.py`; an accent on a figure whose
  meaning lacks it is the finding (a DJ tool's about page, 2026-11-03).
- **Fit a palette inside its look** (P2): start from the palette the person chose and hold each family's hue band and
  lightness and chroma ranges, then let a search push pairs apart inside those bounds; a search left free to
  maximise distance wrecks the look. One hue family per category,
  members as lightness steps; deep oranges go brick red, since dark orange reads brown (a peptide explainer, 2026-11-21).
- **Keep to the person's chosen colours** (P2; their style profile lists any set aside): an alarm takes the guide's colour for its meaning, so an outlier wears
  the outlier's colour, never a new red (a pitch deck, 04c, 2026-10-26).
- **Hold a distance floor on the pairs that meet** (P6): list where colours appear together and require each meeting
  pair to clear a floor (0.12 in OkLab, say) under normal, protan, deutan and tritan vision, light and dark; pairs
  that never share a figure need no floor. Name each item in every figure that colours it, so nothing relies on
  colour alone, and state what the floor cost (a peptide explainer, 2026-11-21).
- **Count every colour the reader sees, the host's too** (P1). On GitHub, build on the fixed link blue, alert colours
  and syntax highlighting: the accent from the host's palette, arrows and containers in the theme's greys, plain code
  fences. Set a generated diagram's colours yourself (fill, stroke and text per class, text AA on its fill, outlines
  3:1 on light and dark) (claude-code-learns README, 2026-10-25).
- **Draw the palette from the work itself** (P7) when there is hero art: sample it (k-means in OKLab plus a pass for
  rare accents), use each colour about as often as it appears, keep text neutral. Once the person picks a colour away
  from the art, the pick becomes the source (a named pick per token; "a bit more red" is an OKLCH hue step with
  lightness and chroma kept), so a re-measure reproduces their palette (a DJ tool, 2026-11-03).
- **Measure the colour the browser paints** (P7), from the computed style or a pixel over its real background, not the
  token. When two measures disagree, find which reads the paint and which simulation each uses before shipping
  (a peptide explainer, 2026-11-21).
- **An effect that imitates a material obeys its physics and optics** (P7): water is clear, so it shows as refraction
  and glints with no colour of its own, and its runs are few, each from a drop pooled at a glyph's lowest foot; a
  solid-colour run reads as slime (a cover's lettering, 2026-11-04).

## Checkers

- `python3 ${CLAUDE_SKILL_DIR}/scripts/design_budget.py PAGE.html [--faces 3 --sizes 6 --colours 24 --classes 40 --shadows 0 --gradients 0]`
  counts the system (faces, base type sizes, colours in both themes, CSS classes, shadows, gradients) and exits 1 over
  budget. Raise `--gradients` only for one shared shading recipe in biology drawings.
  - Colours are raw hexes, so a dark theme pays double: resolve the roles first and say which number you ran
    (a peptide explainer, 2026-11-17: 15 roles x 2 themes, `--colours 30`).
  - Classes count as written, not as used, so a page sharing a head is over budget for components it lacks. Prune at
    build time: drop a rule only when every selector names a class the markup never carries (element, id and
    attribute selectors, custom properties, at-rules, keyframes and script-added classes stay), and rewrite each
    selector list to its survivors.
  - Prove the prune changed nothing: build an unpruned control in the same run and diff every element's computed
    style and box at both widths in both themes. A comment counts as selector text, so "head.html" reads as the class
    `.html` (a peptide explainer, 2026-11-05).
- Before publishing a long page, read [references/page-audit.md](references/page-audit.md): fourteen checks, each with
  its case (first screen, computed styles, colour by paint and meaning, states, touch targets, an ending, even labels,
  balanced styling).
- `python3 ${CLAUDE_SKILL_DIR}/scripts/check_symbols.py PAGE.html --class CLASS [--chem] [--reserved "codes"] [--base]`
  lists duplicate symbols and collisions with chemistry's 118 symbols or codes used nearby; elements marked `sample`
  are skipped.
- `python3 ${CLAUDE_SKILL_DIR}/scripts/accent_census.py PAGE.html --accent HEX=name ...` counts each accent per figure
  block (generated `<!--fig:NAME-->` markers), so a colour used outside its meaning shows as a number.
- `python3 ${CLAUDE_SKILL_DIR}/scripts/check_design.py PAGE.html ...` lists separator dots in visible text and short
  phrases repeated on one page (candidates for saying a fact once; judge each). Exits 1 when dots are found.

## Related

app-design (apps, controls, hovers, states), figure-design (axes, legends, spacing, diagrams), science-figures
(the science inside a figure), page-legibility-check
(measure), field-vocabulary (words), storytelling (order), tufte-principles (data-ink and chartjunk: P1 for
charts), hci-principles (design rationale, heuristics, affordances), html-slide-deck and pitch-deck-story (decks),
controlled-comparisons (scientific figures), the person's style skill.

## Provenance

a DJ studio notes, 2026-10-14 to 2026-10-20: "less text"; "negative space, element balance and positioning follow
standard visual harmony practices ex golden ratio, buffer space around elements"; "separate rows for separate legend key
elements (dots vs shaded region)"; "x and y axis for projection bottom left corner"; "pca ... what each PC axis is should
be clear"; "hover to explain flags instead of drop down (more legible text, less jumpy)"; "scrub-able time bar should
align with plot visualization"; "check for redundant text"; "first principles color from album art ... use at same
frequency as in image"; "check symbols for each element should be unique". a pitch deck deck, 2026-10-15 to 2026-10-20:
every line anchored ("minimize floating text"), "y axis clarity 1 = perfect agreement", "cell scale bars ... should have
um units", one colour one meaning across a deck; "where do 'numbers' come from? dont assume reader knows what a plate is, illustrate key concepts use more iconography" (25 Oct). Personal taste (golden-ratio scale, separators, palette choices)
lives in jo-style since 2026-10-20. Apps and interaction moved to app-design on 2026-10-27, when this skill reached
251 lines. 2026-11-21: restructured principle-first, seven principles with every rule tagged to one, long cases and
quotes moved to references/cases.md ("the skills seem a little bit too literal").
