---
name: design-practice
description: Guides the design of pages, documents and slides - composition and balance, short text with each fact once, one meaning per colour, one symbol and icon per thing, numbers on cards and true phone layouts. Use when designing, reviewing or polishing any page, deck or screen layout, or on "cluttered", "too much text", "redundant", "not aligned" or "show, don't tell".
when_to_use: Before building a page or slide; in a design review or audit. Apps go to app-design, figures to figure-design, measuring to page-legibility-check.
---

# Design practice

Guidelines for how any page, document, deck or screen is laid out and worded, each with the case it came from; apps
and the interactive parts of a page (the first screen, controls, hovers, states) add app-design on top. Start with a
quick critique (first impression, usability, hierarchy, consistency, accessibility), write the plan, then build. Measure with
page-legibility-check (no overlaps, WCAG AA contrast, no sideways scroll, desktop and phone widths). When the work is for
a person with a style profile, read it too (`<name>-style`).

## Gotchas

- A hero or hook graphic, the one picture that has to sell the page, gets three or four different concepts drawn side
  by side on one comparison page before one ships; refining a single concept three times still leaves the question
  "did we test different versions?" unanswered (a peptide explainer's masthead hook, 2026-11-17). After a deploy, say that a
  browser may show the cached old page for up to ten minutes, and that a hard refresh (Cmd+Shift+R) loads the new one.
- A board of cards with uneven content leaves a block of empty white under the short ones ("gigantic block of cold white
  not good look"): put the cards on one row grid (CSS subgrid, the same rows in each card) so rows line up and the figure
  row takes the spare height, and tint each card by its meaning rather than leaving them all white (a pitch deck, A4,
  2026-11-09: green for what is shared, pink for what stays yours, a pitch deck on white between them).
- **Group by what the reader does with it.** Things used together sit together: the set's description and its tags are
  both copied when publishing, so they are adjacent and share one copy control (a DJ tool, 2026-11-06: "tags should be closer to
  set description text, these are both things to be copied"). A drawing and its name share one cell, the drawing a thumbnail
  flush against the name (a public-health dashboard, 2026-11-08: "things should be connected and close to each other").
- **Any page or document opens with three summary numbers at most.** Pick the ones that describe the whole (for a DJ set: track
  count, length, tempo arc); every other figure lives in the section it summarises, as that section's folded line, or goes (a DJ tool's set block,
  2026-11-06: "avoid too many summary metrics. use maybe 3").
- **One left edge, one measure, one rhythm.** Every section's heading, text, lists, tables and figures start at the same x;
  gaps come from the space scale and repeat the same way for every section; measure the left x and gaps per section rather than
  trusting the eye (a DJ tool's about page, 2026-11-06: "consistent margins").
- **Comparable items are rows in a table, not a grid of cards.** Takes, methods, flags, songs, glossary terms, export files:
  one row each, the same element at the same x down the column, hairlines between rows, labels outside the data. Cards only for
  one-off content that is not compared. (repeated 2026-11-05 and 11-06: "avoid cards, prefer interactive tables"; "again,
  prefer rows in table to cards".)

- Passing every check is not a design: legibility checks fail only on contrast, overlap and size, so a page can pass for five builds while each fix adds a device (a hint pill, a linked key, a rail, a boxed lede). Set a budget before building (two faces, five or six sizes, ink plus one highlight plus the data hues, a few component kinds, one drawing style for every figure, no shadows or gradients), subtract until it holds, and run `design_budget.py` (a peptide explainer, 2026-11-05: 55 colours, 9 sizes, 132 classes, 17 shadows rebuilt to 21, 6, 17, 0; then "still a mess ... lots of great AI-designed front ends").
- Fine at 1280 px, broken at 400 px: measure both widths with page-legibility-check before calling a page done.
- One fact told by a chip, a pressed button and a letter reads as polish to the builder and clutter to the reader: keep the one or two the reader acts on (Text).
- Invented symbols collide with chemistry or a nearby key (Ck, Cc, Pu): run check_symbols.py where they are generated (Text).
- One outline colour doing two jobs (orange for a moodboard pick and for dream B): one style per role (Text).

## Composition

- **Negative space separates groups**; a generous buffer surrounds every element and keeps it clear of the edges.
- **A row of entries fills its rows, or it is one row.** Pick a column count that divides the number of items:
  four entries go 1 x 4 or 2 x 2, six go 1 x 6, 2 x 3 or 3 x 2, never a count that leaves one hanging under an empty
  half-row. `repeat(auto-fit, minmax(Npx, 1fr))` chooses the count from the width and so produces exactly that
  straggler (four identity entries fell to 3 + 1 because four columns at 180 px plus three 32 px gaps did not fit a
  740 px band). Set the count explicitly, `repeat(4, minmax(0, 1fr))`, shrink the gap until it fits, and change the
  count at a breakpoint to another divisor. Count the items per row in the render, not in the CSS (an MoA
  explainer, 2026-11-17: "prefer 2 x 2 is 1x4 (one row) here - avoid weird overhang element always"; the same rule
  for a figure's wrapped key is figure-design, A wrapped key fills its last row). Caught again on a compound explainer's
  property cards, 3 + 1 (2026-11-20: "pet peeve overhanging cell: prefer 2x2 matrix of blocks"). A count no grid divides (13 drawer cards, 19 glossary terms) becomes rows with the name in its own column; set the count per list with a quantity rule (`dl:has(> div:nth-child(4):last-child)`) rather than one column count for every list.
- **One spacing scale and one type scale**, used as tokens, and a few deliberate proportions for the main splits
  (picture to text, main to side column, row to gap). A proportion near 1 : 1.6 reads as calm.
- **Balance** visual weight left and right, top and bottom, in every view; share left edges; align label columns.
  After a cut, re-balance: when text leaves a view (to a handout layer, or deleted), let what stays grow into the room,
  pictures flexing to fill their cards and side columns spanning the full content height, rather than leaving a hole
  where the text was. Text on one line shares one baseline, measured, not one box centre: a header's title, menus and
  links with matched centres still looked "off" until the baselines were set within a pixel (a 0-height inline probe's
  top) (a DJ tool, 2026-10-27: "be meticulous about pixel-perfect alignment, element harmony"). Give both halves of a paired card the same parts (a big value and a line under each). (a pitch deck
  02a and 02c, 25 Oct 2026: "negative space a bit awkward" after half the words moved to the PDF.)
- **Vary the organisation, and give the group a centre.** A row of equal cards is the default, not a design: when
  several things share one idea, set them at the points of a diamond (or another non-grid arrangement) around a small
  central element that names what they share, with a hairline from each into it. The gaps the diamond leaves are the
  point — the eye travels the empty quadrants from one item to the next instead of scanning a line — and the centre
  stops the group reading as a list. Keep the arrangement off the items themselves: shrink the central shape until its
  edges run through empty space, never across a drawing (a peptide explainer's masthead, 2026-11-05: "consider diamond
  arrangement not just row"; "more varied organiztion, use central connecting element, diamon can create interesting
  negative space for eye flow").
- **One left edge on every screen.** When a page has a reading measure and a wider band for drawings, do not centre the text inside the band: that puts four vertical edges on a desktop screen. Start every element on the line where the drawings' own content starts (a fixed inset inside the band), headings, prose, captions, keys, lists, tables and the rules drawn under them; words stop at the measure, keys and tables run on to the drawings' content edge. A rule that must start on that line is drawn (a pseudo-element) rather than a border on a wider box, and a key inset with padding is still a wider box: inset it with a margin. Measure every block's left edge at both widths and expect one number (a peptide explainer, 2026-11-05: "consistent margins"; "fig 2 legend is indented from legend border?"; 200, 220, 320 and 960 became 220).
- **Every line belongs to something**: inside a card, directly under its figure aligned to the figure's left edge, or
  in a fixed header or footer slot. When a block is cut, move what remains next to what it describes.
- **Air between elements, tight inside them.** A box hugs its content (small padding, width to its text) and the
  sections around it get the space; a timeline is one continuous line with a tick per stage, the label above and the
  plan below, never separate bars (a pitch deck's one-pager, 2026-11-01: "dense and wordy, needs more negative space";
  "geom elements should have less negative space inside, tight element"; "timeline ... need a tick? a little disjointed").
- **A rule spans exactly the content it underlines, and a page keeps few measures.** Insetting a strip's content
  with `padding-left` leaves its box, and so its `border-bottom`, at the old width: the line then runs past the
  swatches it belongs to and reads as a ragged edge. Use a margin, so the box starts where the content starts. More
  generally, settle on two content measures (a reading column and a wider band for figures and data), put every
  element unambiguously in one of them, and write the rule down where the styles live; measure the painted edges to
  check, since the intended ones are not what the eye sees. Case: a page with exactly two bands, 640 px prose
  centred inside 880 px figures, still read as uneven because the keys' rules spanned 880 while their swatches began
  at 640, giving four vertical edges (a peptide explainer, 2026-11-05: "some elements much wider than others is visually
  weird").
- **Shared alignment claims a relation.** Rows or columns that line up read as one table, so give unrelated blocks
  their own shape: a stat row of three, then the reasons as a term list, not a second row under the stats
  (a pitch deck's one-pager, 2026-11-01: "elements arranged similarly should relate ... do not align in shared grid").
- **Break lines at the sense.** A headline or lead fits on one line, or breaks at a sentence or clause, never mid-phrase:
  no `max-width` or `text-wrap: balance` that splits "Nobody / calibrates" (a pitch deck's one-pager, 2026-11-01:
  "weird line style. start sentence new line. or, fit on one line"). A short paragraph set beside another column is
  the opposite case: give it `text-wrap: balance` so no short line leaves a hole beside the column (resume summary
  beside the contact list, line ends 351 to 480 px became 404 to 443; 2026-11-08: "awkward negative space here"). A dek that
  strands one word on a second line is cut until it fits one line at the page measure, and balanced where a phone must
  wrap it (a public-health dashboard, 2026-11-08: "fit this on one line avoid awkward overhang"). A page viewed on screen takes its printed measure, or its breaks differ from the PDF (the CV's web
  container was 6.1in against 7in in print, so "AI" fell to its own line and a heading wrapped under the date
  column; 2026-11-09: "avoid weird text overhang"); a heading that wraps under a right-hand column is shortened
  and its detail moves to the line below ("Coursework" over "Undergraduate and graduate: Python, ...").
- **Body text breathes** (line-height about 1.5), headings sit tighter, label-value gaps come from the spacing scale.
- **Type reads at a glance**: body 17 to 19 px on a 45 to 75 character measure, one modular scale of five or six sizes
  carried as tokens, two families at most (a sans or serif for reading, a mono for labels, readouts and ticks), and
  figure labels at 12 px or more so a phone's slight downscale keeps them above 11. Case: an essay's cell panes had
  a dozen 11 px labels, raised to 12 after "does this follow best practices about text size, variety?" (2026-10-25).
- **Art pieces** (a pair that mirrors, like A and B covers or a diptych; museum wall labels; a piece drawn to scale
  beside a person): read [references/art-pieces.md](references/art-pieces.md).

- **A link shows where it goes.** Next to a name, link with the address itself (short, stable, the home that fits) instead of repeating the name as "open X"; on paper the address still works. Example: "2 v[er]itas  example.github.io/still-life ↗", not "v[er]itas  open veritas ↗" (2026-10-26: "de-duplicated, link, show url. make sure using good fit url").
- **One doc, two media.** When a page also has to exist as a PDF or handout, give the page a print layout (`@media print`, `@page` size and running footers, live parts printing as stills, hover notes as a word list) instead of keeping a second document; two copies drift. Example: an art doc prints as the 8-sheet submission, and the old Submission file only forwards to it (2026-10-26: "submission and web should be one doc").
- **Connect related elements with lines.** A short leader from a callout or thumbnail to the mark it describes, and numbered points on a timeline with a line dropping to each card, beat matching by colour alone. Use them where the two things sit close; a leader that would cross a whole figure adds clutter. Start each leader on the mark itself, wherever it is now (on a turning or moving figure, redraw it every frame), and draw icons large enough to read at a glance (an art piece's ring, 2026-10-26: "connect yellow icon to line", "icons should be larger, easy to see"). Example: a pitch deck, 09's timeline dots carry 1 to 4 and drop to their cards; 05b's batch in the drop zone has a dashed leader to its dot on the map (2026-10-26: "points should be labelled with number", "use lines to connect related elements").

## Text

- **Every table says what it is, and every column title fits on one line.** A title or lead-in above the table names what
  its rows are ("Who has tried to tabulate biology, and how each attempt holds up"); each column gets a header, one or two
  plain words ("counts", "misses", "evidence"), never a phrase that wraps ("what it says about treatment"); a first column
  of row names gets its header too ("disease"). The headers are siblings, so they take one form between them, below.
  (an essay, 2026-11-19: "what is this table describing? tables need headers"; "table column titles should fit in 1
  line, minimal".)

- **One title and description style for every section**: the same title size and face, its description stacked beneath
  at one measure; facts a table already gives leave the description (an art doc, 2026-10-26: "use consistent title and
  desription style for sections").
- **Items in one list carry the same parts**: every item has a subtext, or none does; one card with a caption among
  bare cards reads as an error (an open call's about page, 2026-11-19: "why do some items have subtext and some dont?
  cosnistency").
- **Siblings share one form of words, not just one size.** Labels that sit beside each other — a table's column
  headers, a card grid's titles, a nav's items, a figure's key rows — agree on capitalisation, on part of speech
  (all nouns or all verb phrases) and on whether they carry a qualifier: one header with a parenthesis among plain
  ones breaks the row as surely as one card in a different font. Read the labels across, not down, before calling a
  page done. (A README's four tables ran "practice (source)", "What it is for" and "you say" side by side,
  2026-11-22: "titles need more format harmony. one col has parent, one has caps, one all lowercase". The length
  rule for table headers is above; this is the form rule, and it holds for every set of sibling labels.)
- **Numbers in one style, the field's standard** (APA for technical and science writing): words for zero to nine in
  prose counts, numerals from 10 up, numerals always with units and time (2 minutes, 3 s, 16 GB) and for every number
  in a comparison that reaches 10 (3 of 10 steps), a word or a recast at a sentence start; labels, versions and display
  figures keep their form (an art doc, 2026-10-26: "when to spell vs write number. follow best/standard practice").
  A number and its unit never break across lines: join them with a no-break space (`123&nbsp;bpm`) or `nowrap`
  (a DJ tool's to-buy page, 2026-11-03: "keep units on same line as digits").
- **Say each fact once, in one element**, where it is most useful (the set name in the header; the sample size in the
  caption). Controls, figures and geometry too: a line repeating its neighbouring control goes (an "about" line under a
  switch already labelled human / algorithm); a verdict said four ways on one card (chip, pressed button, letter, inset
  bar) keeps the one or two the reader acts on; three identical panels with different labels become one panel with the
  labels as rows; a small copy of a later figure goes; the verb matches the gesture (drag, tap, click) and appears once;
  a group label repeating what each row's card and the total say goes, and a group label shows only where two groups meet;
  a mark every row shares goes (a DJ tool's Recommended table, 2026-10-27: "to buy $ each rm this" for a "to buy $1.49 each" row
  over one list; "dont need to show dot for every song" for a to-buy ring on every recommendation).
  In a figure, a key carries only the marks the drawing does not already label where they sit (line styles, a fill pattern); a molecule, receptor or cell named on the drawing gets no key row, and a label never has a second line restating its first ("Gi/o not activated / inhibitory signalling absent") (a peptide explainer, 2026-11-05: "how to reduce information redundancy in figure?").
  A thumbnail that repeats what text beside it already says goes, above all when it is too small to read: the studio title names both keys (4A → 4A), so its 55 px key wheel was cut and the full wheel stays in the clash card (a DJ tool, 2026-11-06: "the little key wheel is hard to see and read, too small. is it necessary?").
  A fact sits on the element it describes (a flag about one take of one transition on that take, never on the song row);
  one graph, one control and one name per thing on a page (a song's graph drawn in its row and again in a list keeps the
  row; play at the top and in a bottom bar keeps one; a transition's number on its node, title, player and tips gives
  way to its place and its two tracks, the number kept for aria and keys). (a DJ studio, 2026-10-24 and 2026-10-26:
  "information should be revealed at the right place", "avoid figure redundancy", "transition numbers: appear multiple
  places?"; an essay, 2026-10-25: a result told five times, and the same geometry drawn twice in one tile.)
- **A byline carries who, where to reach them, and when — not counts.** Author and organisation, a contact or the
  author's own site, and the publication date; a reference count, a figure count or a word count is bookkeeping the
  reader never needs and the page already shows (a peptide explainer, 2026-11-05: "author name and org ar usually
  sufficient. maybe contact email. and date published. fig count etc not necessary").
- **Short ledes, data over prose**; a caption adds what the figure cannot show. A summary is a few small plots on the
  page's shared axis, not a sentence of adjectives and a row of numbers (a DJ tool, 2026-10-26: "summary: show dont tell,
  simple plots"). Text beside those plots leads with one bold sentence, the takeaway, then a short line of what the plots
  can't show (for a set: its feeling, its story, how it was seeded), leaving the numbers to the plots (2026-10-27:
  "bold/highlight main 1 sentence takeaway, then elaborate"; "redundant with figure summaries? more vibes and feeling").
  A list of options with a reason sentence on each row becomes a ranked table of scored cells, the reasons on hover
  (a DJ tool's swap list, 2026-11-03: "too much text. this is rank order? show dont tell"; the form in figure-design §4).
- **A grid holds phrases; sentences in cells are prose wearing a table's clothes.** A definition list, card grid or
  matrix earns its form when each value is a fact the eye can take whole: "no company name or address", "USPS, plain
  mailers", "in-house NMR and HPLC only". Once a cell runs to a sentence or two, the grid is costing the reader the
  scan it promised, and a column whose rows repeat the same line is carrying one fact and a lot of noise: say that
  once under the figure and mark only the exception. Where a block describes an outside party, link its name and say
  what it offers, which is the thing a reader came for (a peptide explainer, 2026-11-05: "redesign: too many words,
  colors"; "link to the vendor, sumamrize offerings, if itss legal. too many words in grid right now").
- **Three real examples beat a word list.** Where a page shows what someone can say or do, one table of three cases in the
  field's own words, each with exactly what changes, reads as professional; a list of accepted words and a second table of
  history read as clutter (a DJ tool's process page, 2026-10-27: "more professional, 1 table. three examples using real DJ words.
  specific what moves").
- **One phrase lit per headline.** Set the headline in the page's ink and light the phrase that carries the claim in the
  accent ("Does my control *look like yours*?", "Six questions, six tools. *Use all of them.*"); the eye lands on the
  claim before reading the line. (The a drug-mechanism deck's habit, taken into a pitch deck on 25 Oct 2026.)
- **A borrowed finding names its author on the slide.** When a chart shows someone else's result, the source stands
  under the figure in plain words, on stage and not only in the reader's layer: their own words, then who and when
  ("not directly comparable between imaging sites", EU-OPENSCREEN, four sites, 2025). A reader asked "who is the
  author?" when the attribution lived only in the PDF (a pitch deck, 06a, 25 Oct 2026).
- **The field's own words** (field-vocabulary, which also words checks as guidance); a person's own names for their things stay as they named them.
- **Separate items with space, weight, size or alignment** when a style asks for a quiet page; the bundled checker
  lists separator characters and repeated phrases.
- **Illustrate the nouns a stranger meets for the first time.** A small icon and a two-word gloss where a term first appears
  (a pitch deck, slide 04: well, "one dish of cells"; plate, "384 wells, imaged together"; lab, "one site, its own cells"),
  drawn once in a shared set and reused on every later slide. Symbols too: N⁺ is glossed "charged nitrogen" where it
  first appears and drawn on the structure itself (N⁺H, its partner Asp147 with a minus), so gloss and mark match
  (a drug-mechanism deck, 2026-10-27: "it needs to be clear N+ = charged nitrogen"). Caught again on a DJ tool's process page (2026-10-27: "secret sauce too wordy ... show dont tell. simple system reveal, icons"): four text cards became four even drawn tiles in a row, a title and a few words each.
- **Say where a derived number comes from.** "3,773 measurements of each image: size, shape, brightness, texture" reads;
  "3,773 numbers" leaves the reader asking what was counted.
- **One symbol per thing, checked.** When a page invents symbols or short codes (element symbols, legend codes, track
  tags), give each a unique one that differs from codes already standing nearby: the companion page's key, or the field
  the page borrows its look from. Example: a periodic table of loops first used Ck (clock), Cc and Pu; Ck and Cc already
  meant CaMKII and cell cycle in the essay's key, and Pu is plutonium, so they became Tk, Tw and Ps. Assert uniqueness
  where the symbols are generated and run `${CLAUDE_SKILL_DIR}/scripts/check_symbols.py`.

- **Explaining a process, a method or a long argument** (a loop of steps, an overview kept beside its details, a
  methods tutorial, the hero figure, a scorecard, how many examples and where): read
  [references/explainers.md](references/explainers.md).

- **One outline style per role, on every image.** If gold marks the new dream, a moodboard pick gets a different mark
  (a dashed bone outline) rather than the same gold (2026-10-26: "orange outline for moodboard 01 then same orange for dream B?").

- **Every timing says per what** ("about 3 s a dream", "0.76 s a frame"); a bare "about 3 s" left the reader asking.
- **Generated prose reads its own numbers.** A sentence a page builds from data handles its edge values: two decks at one tempo
  read "both at 123 bpm", never "123 to 123 bpm, a 0.0% jump"; a count of zero reads "none" (a DJ tool's about page, 2026-11-03,
  the worked transition on set C).
- **A split names each share on its own segment** (a bar: "artist 60% $9,400 | an art piece 40% $6,266"), rather than as a ratio
  followed by a list of numbers (2026-10-26: "numbers not linked to artist/an art piece clearly").

## Icons and thumbnails

- **A mark earns its place by meaning.** Draw one only where it shows what the words cannot: scale, a mechanism, a
  value, a state, the thing's own behaviour, or a convention a reader already knows (the GitHub mark on a code link,
  the SoundCloud mark on a track link). A pictogram beside every noun, a glyph per list row or a decorative loop beside
  a sentence reads as busy, not impactful; a screen of strong type or numbers can stand without a picture. Before
  adding one, say in a sentence what it tells the reader; if the words already say it, cut it. (an open call's about page,
  2026-11-19: 48 dot glyphs added to fill every screen; 31 were cut after "icons should be useful, helpful, add
  value", with "dont use an icon just to use an icon" and "these feel busy, not impactful. would be better to use
  real github icon for code".)
- **One icon per thing, its word beneath.** A node that lists several functions as words (remember, keep time, steer)
  becomes one small icon per function with the word under it (a flag planted, a clock face, a compass), and the same
  icon travels to wherever that function is named again (the chip under each circuit). Case: an essay's frame
  figure (2026-10-25: "use symbols for each word? ... ex clock, below label keep time"). Caught
  again in an art piece's feed (2026-10-26: "iconography should be consistent, connect pieces"): one circled icon per step
  on the overview ring, on the step's own row and in the intro, lit together as the reader reaches it.
- **An icon carries no words it can't render legibly at its size.** Make the mark itself say it: combine the artwork (overlay
  two sets' waveforms in one round mark, the current one lit, the other faint) rather than tiling two covers with captions
  too small to read. A round crop reads as an identity mark; the state it shows (which set is open) comes from emphasis, and
  hover previews where a click goes. (a DJ studio header, 2026-10-24: "overlay/combine waveforms? no the wordmark text
  please (too small). make bigger, maybe round?")
- **Warnings borrow safety signage**: a broken rule is a warning triangle (ISO 7010), a place to look a diamond (GHS), one
  pictogram per kind, one home for each kind's sign and words; hover shows where it was found, a press opens its
  definition (a DJ tool flags, 2026-10-26: "warning sign with symbol, learn from chem/fire safety symbols ... click on horses
  go to process definition").

## Numbers on cards and chips

Direction, best value, units and comparisons on a card: read [references/numbers-on-cards.md](references/numbers-on-cards.md) before putting a number on a card, chip or dashboard.

- **In a document read as prose, a number lives in the sentence that gives it meaning.** Stat-tile rows belong on
  slides and dashboards; on a page of chapters they read as random summaries, cut off from the story. Keep the striking
  numbers, cited, inside the paragraph whose context, tension and payoff they serve (a peptide explainer, 2026-11-06: "more
  random summaries? okay to use these nice numbers, in the context storytelling paragraph").
- **A fraction names its whole and what sets the parts apart**: "3 of 8 presets hold the water still", never a bare
  "3/8" (an open call's about page, 2026-11-19: "3/8 of what? what makes them different?"). A count repeated as words in
  every row becomes marks: the word once in the header, then one to three bars per row, and axis labels over sentences
  (an essay, 2026-11-19: "consider just '# loops' text once, then bars showing 1, 2 or 3"; "show dont tell here: use
  axis labels").

## Colour

- **One meaning per colour**, inside a figure and across a deck; a verdict colour travels with a glyph. Once a colour means
  something, let it say so alone: a pink label reads "lab 2", with the word "you" spoken rather than written.
  The meaning binds every mark in that colour, strokes, rules, rings, carets and icons as much as words: before calling
  a page done, list each use of the accent (grep its hex) and move every use outside its meaning to neutral ink
  (an art piece's feed, 2026-10-26: gold was for scale, "chosen" and dream B, yet coloured callout rules, the loop ring
  and step markers; again in a pitch deck the same day, "pink for outlier // single point, green for larger field": headline
  accents, card stripes, corner glows and links had worn the outlier's pink).
  A companion page wears the app's own state code and nothing of its own: where the studio says rose = kept and slate =
  to review, its about page may not paint deck A slate and deck B rose, nor light headline phrases in rose; decks and
  series are told apart by position and value (A above B, two grays), the lit phrase by value. Count the accents per
  figure first, `python3 ${CLAUDE_SKILL_DIR}/scripts/accent_census.py PAGE.html --accent ec3c6e=rose --accent 8da4bc=slate`:
  a rose count on a figure whose meaning has no "kept" in it is the finding (a DJ tool's about page, 2026-11-03: "use same
  color as studio, balance colors, use colors logically"; four deck-coloured figures and seven lit headlines).
- **Draw the palette from the work itself** when there is hero art or a brand image: sample it (k-means in OKLab plus a
  pass for rare accents), use each colour about as often as it appears there, keep text neutral. Once the person has picked a
  colour away from the art, the pick becomes the source in the palette tool (a named pick per token, and the person's later
  calls as steps on it: "a bit more red" = a hue step in OKLCH with lightness and chroma kept), so a re-measure reproduces
  their palette instead of the art's; a "keep the hand value if close" rule does not hold a pick that sits far from the art
  (a DJ tool, 2026-11-03: one re-measure wrote the art's hot pink and cyan over the studio's rose and slate in the live studio).
- **Fit a palette inside its look.** Start from the palette the person chose, and hold the bounds that keep its look:
  each family's hue band and its lightness and chroma ranges. Then let a search push the pairs apart inside those
  bounds; a search left free to maximise distance wrecks the look. Give each category one hue family, with its members
  as lightness steps, and turn deep oranges brick red, since a dark orange reads brown (a peptide explainer's palette,
  2026-11-21: three families by biology, searched from the electric palette, after a free fit drifted off it).
- **Hold a distance floor on the pairs that meet.** List where colours appear together (one figure, table or strip),
  and require every pair that meets to clear a floor (0.12 in OkLab, say) under normal vision and protan, deutan and
  tritan simulation, in light and dark. Pairs that never share a figure need no floor. Name each item in every figure
  that colours it, so nothing relies on colour alone, and state what the floor cost: in light mode a hot pink became
  raspberry, because the hotter pink folded into the vermillion for tritan readers (same project and day; the rule
  came with the person's go-ahead to search: "measure only pairs that share a figure").
- **Measure the colour the browser paints**, from the computed style or a pixel sampled over its real background, not
  the CSS token. A diagnosis worked out from the spec, that deep shades drift purple, was wrong: Chrome kept the hue.
  A second measure of the merged palette found three tritan pairs under the floor that the search had passed. When
  two measures disagree, find which reads the painted colour and which simulation each uses before shipping (same
  project and day).
- Keep to the colours the person has chosen for a project (their style profile lists any they set aside). An alarm or a
  flag takes the guide's colour for its meaning (an outlier wears the outlier's colour), never a new red (a pitch deck, 04c,
  2026-10-26: "red ring: this is not color in guide"; the flagged batches' rings went to the guide's pink).
- **Count every colour the reader sees, including the host's.** On GitHub the link blue, the alert colours and code
  syntax highlighting are fixed, so build on them: take the accent from the host's palette (Primer green matches the
  TIP alert), leave arrows and containers to the theme's greys, and use plain code fences when highlighting adds a
  colour. Set a generated diagram's colours yourself (Mermaid's default is lavender): fill, stroke and text per class,
  text AA on its own fill, outlines 3:1 on both the light and dark page. Case: claude-code-learns README, 2026-10-25,
  from four colour families to three.
- **An effect that imitates a material obeys its physics and optics.** Water is clear, so it shows as refraction and
  glints with no colour of its own, and its runs are few, each from a drop pooled at a glyph's lowest foot; a
  solid-colour run reads as slime or paint (a cover's lettering, 2026-11-04: "not physics enough", then "too much
  like slime"; `the type generator` drips()).

## Checkers

- `python3 ${CLAUDE_SKILL_DIR}/scripts/design_budget.py PAGE.html [--faces 3 --sizes 6 --colours 24 --classes 40 --shadows 0 --gradients 0]`
  The colour count is raw hexes in the CSS, so a page with a dark theme pays double: every role is written
  twice. Resolve the roles before calling it over budget (a peptide explainer, 2026-11-17: 29 hexes = 15 roles x 2
  themes, so `--colours 30` is the honest line), and say which number you ran.
  counts the system itself (faces, base type sizes, colours in both themes, CSS classes, shadows, gradients) and exits 1
  over budget. Raise `--gradients` only for one shared shading recipe in biology drawings.
  It counts class selectors **as written, not as used**, so a page that inherits a shared head is over
  budget for components it does not have. Rather than stripping by hand or waving the number away, prune
  at build time, dropping a rule only when every one of its selectors names a class the markup never
  carries (element, id and attribute selectors, custom properties, at-rules and keyframes stay, and a
  class a script adds at runtime counts as carried), and rewrite each selector list to its survivors so
  a dead name leaves the file. **Prove it changed nothing**: build an unpruned control from the same
  inputs and diff every element's full computed style and box at both widths in both themes — identical,
  or the prune is wrong. Two traps, both real (a peptide explainer, 2026-11-05: 43/40 to 26/40, 61 selectors
  dropped, 1,703 elements identical): a comment counts as selector text, so "head.html" in one reads as
  the class `.html` and kills the rules under it, and a control built minutes earlier is worthless when
  another session is editing the shared head — build both in the same run.
- Before publishing a long page, read [references/page-audit.md](references/page-audit.md): fourteen checks, each with its case (first screen, computed styles, colour by paint and meaning, states, touch targets, an ending, even labels, balanced styling).
- `python3 ${CLAUDE_SKILL_DIR}/scripts/check_symbols.py PAGE.html --class CLASS [--chem] [--reserved "codes"] [--base]`
  lists duplicate symbols and collisions with chemistry's 118 symbols or codes used nearby; elements marked `sample`
  are skipped. Validated on the loop table (caught Ck, Cc, Pu) and the essay's example key (7 of 23 codes are chemical
  symbols: Ag, Al, Am, Cr, Hg, Hs, Sg).
- `python3 ${CLAUDE_SKILL_DIR}/scripts/accent_census.py PAGE.html --accent HEX=name ...` counts each accent per
  figure block of a page (generated `<!--fig:NAME-->` markers), so a colour used outside its meaning shows as a number (Colour).
- `python3 ${CLAUDE_SKILL_DIR}/scripts/check_design.py PAGE.html ...` lists separator dots in visible text
  and short phrases repeated on the same page (candidates for saying a fact once; judge each). Exit 1 when dots are found.

## Related

app-design (apps, controls, hovers, states), figure-design (axes, keys, spacing, diagrams), science-figures (molecules, cells, micrographs), page-legibility-check (measure), field-vocabulary (words), html-slide-deck and pitch-deck-story (decks),
controlled-comparisons (scientific figures), the person's style skill.

## Provenance

A DJ studio's notes, 2026-10-14 to 2026-10-20: "less text"; "negative space, element balance and positioning follow
standard visual harmony practices ex golden ratio, buffer space around elements"; "separate rows for separate legend key
elements (dots vs shaded region)"; "x and y axis for projection bottom left corner"; "pca ... what each PC axis is should
be clear"; "hover to explain flags instead of drop down (more legible text, less jumpy)"; "scrub-able time bar should
align with plot visualization"; "check for redundant text"; "first principles color from album art ... use at same
frequency as in image"; "check symbols for each element should be unique". A pitch deck, 2026-10-15 to 2026-10-20:
every line anchored ("minimize floating text"), "y axis clarity 1 = perfect agreement", "cell scale bars ... should have
um units", one colour one meaning across a deck; "where do 'numbers' come from? dont assume reader knows what a plate is, illustrate key concepts use more iconography" (25 Oct). Personal taste (golden-ratio scale, separators, palette choices)
lives in jo-style since 2026-10-20. Apps and interaction moved to app-design on 2026-10-27, when this skill reached 251 lines.
