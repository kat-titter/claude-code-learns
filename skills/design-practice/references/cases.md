# Design practice: the cases

The long form of each case in SKILL.md, grouped by the principle it shows, with the words it came from. SKILL.md keeps
the rule and a few words of each case; read this when a rule needs its full story, or when filing a new case
(capture-lesson §2: most new cases fold under one of these principles).

## P1. Every element earns its place

- **Passing every check is not a design** (Gotchas). a peptide explainer, 2026-11-05: five builds passed legibility while
  each fix added a device (a hint pill, a linked key, a rail, a boxed lede). The page had 55 colours, 9 sizes, 132
  classes and 17 shadows; rebuilt to 21, 6, 17 and 0. Then: "still a mess ... lots of great AI-designed front ends".
- **Three summary numbers at most** (Numbers). a DJ tool's set block, 2026-11-06: "avoid too many summary metrics. use
  maybe 3". For a DJ set: track count, length, tempo arc.
- **A number lives in its sentence** (Numbers). a peptide explainer, 2026-11-06: stat tiles on a page of chapters read as
  "more random summaries? okay to use these nice numbers, in the context storytelling paragraph".
- **A byline carries who, where, when** (Text). a peptide explainer, 2026-11-05: "author name and org ar usually
  sufficient. maybe contact email. and date published. fig count etc not necessary".
- **A mark earns its place by meaning** (Icons). an open call's about page, 2026-11-19: 48 dot glyphs were added to fill
  every screen; 31 were cut after "icons should be useful, helpful, add value. dont use an icon just to use an icon"
  and "these feel busy, not impactful. would be better to use real github icon for code".
- **Count every colour, the host's too** (Colour). claude-code-learns README, 2026-10-25: four colour families became
  three; Primer green matched the TIP alert; Mermaid's default lavender was replaced by set fills.

## P2. One thing, one form

- **Say each fact once** (Text). a DJ studio, 2026-10-24 and 10-26: "information should be revealed at the right
  place", "avoid figure redundancy", "transition numbers: appear multiple places?". A song's graph was drawn in its row
  and again in a list (the row kept it); play sat at the top and in a bottom bar (one kept); a transition's number sat
  on its node, title, player and tips (it gave way to its place and two tracks, the number kept for aria and keys).
  An "about" line under a switch already labelled human / algorithm went. A verdict told by chip, pressed button,
  letter and inset bar kept the one or two the reader acts on. The an essay, 2026-10-25: a result told five times,
  and the same geometry drawn twice in one tile.
- **A mark every row shares goes** (Text). a DJ tool's Recommended table, 2026-10-27: "to buy $ each rm this" for a "to buy
  $1.49 each" row over one list; "dont need to show dot for every song" for a to-buy ring on every recommendation.
- **A key carries only what the drawing does not label** (Text). a peptide explainer, 2026-11-05: "how to reduce
  information redundancy in figure?"; a label read "Gi/o not activated / inhibitory signalling absent", two lines
  saying one thing.
- **A thumbnail repeating the text beside it goes** (Text). a DJ tool, 2026-11-06: the studio title names both keys
  (4A → 4A), so the 55 px key wheel went: "the little key wheel is hard to see and read, too small. is it necessary?".
  The full wheel stays in the clash card.
- **Siblings share one form of words** (Text). claude-code-learns README, 2026-11-21: "i thought we talked about
  best practice table design: minimal column header, one line", then "titles need more format harmony. one col has
  parent, one has caps, one all lowercase". Four tables ran "practice (source)", "What it is for" and "you say" side
  by side; one header with a parenthesis among plain ones breaks the row as surely as one card in a different font.
  16 tables fixed. Before this line, "harmony" appeared only inside quotes, and sibling consistency only as lines on
  parts, size and colour.
- **One title and description style** (Text). an art doc, 2026-10-26: "use consistent title and desription style for
  sections".
- **Items in one list carry the same parts** (Text). an open call's about page, 2026-11-19: "why do some items have subtext
  and some dont? cosnistency".
- **Numbers in one style** (Text). an art doc, 2026-10-26: "when to spell vs write number. follow best/standard
  practice". a DJ tool's to-buy page, 2026-11-03: "keep units on same line as digits".
- **One symbol per thing** (Text). A periodic table of loops first used Ck (clock), Cc and Pu. Ck and Cc already meant
  CaMKII and cell cycle in the essay's key, and Pu is plutonium, so they became Tk, Tw and Ps. check_symbols.py was
  validated on that table and on the essay's example key, where 7 of 23 codes were chemical symbols (Ag, Al, Am, Cr,
  Hg, Hs, Sg).
- **One outline style per role** (Text). an art piece, 2026-10-26: gold marked the new dream, and a moodboard pick wore the
  same colour: "orange outline for moodboard 01 then same orange for dream B?". The pick became a dashed bone outline.
- **One icon per thing** (Icons). Loop essay frame figure, 2026-10-25: a node listing remember, keep time, steer
  became a flag, a clock and a compass with the words beneath ("use symbols for each word? ... ex clock, below label
  keep time"); the icons travelled to the chips under each circuit. an art piece's feed, 2026-10-26: "iconography should
  be consistent, connect pieces"; one circled icon per step on the ring, the step's row and the intro, lit together.
- **A link shows where it goes** (Composition). 2026-10-26: "2 v[er]itas  example.github.io/still-life
  ↗", not "Still Life  open the site ↗" ("de-duplicated, link, show url. make sure using good fit url").
- **One meaning per colour** (Colour). a pitch deck: once pink meant lab 2, a pink label read "lab 2", with the word
  "you" spoken rather than written. an art piece's feed, 2026-10-26: gold was for scale, "chosen" and dream B, yet
  coloured callout rules, the loop ring and step markers. a pitch deck the same day, "pink for outlier // single point,
  green for larger field": headline accents, card stripes, corner glows and links had worn the outlier's pink.
- **A companion page wears the app's code** (Colour). a DJ tool's about page, 2026-11-03: the studio says rose = kept and
  slate = to review, yet the about page painted deck A slate, deck B rose and lit headline phrases in rose ("use same
  color as studio, balance colors, use colors logically"); four deck-coloured figures and seven lit headlines. The
  census there: `accent_census.py PAGE.html --accent ec3c6e=rose --accent 8da4bc=slate`.
- **Fit a palette inside its look** (Colour). a peptide explainer's palette, 2026-11-21: three families by biology, searched
  from the electric palette after a free fit drifted off it.
- **The person's chosen colours** (Colour). a pitch deck, 04c, 2026-10-26: "red ring: this is not color in guide"; the
  flagged batches' rings went to the guide's pink.

## P3. Nothing leaves the reader asking "of what?"

- **Every table says what it is** (Text). an essay, 2026-11-19: "what is this table describing? tables
  need headers"; "table column titles should fit in 1 line, minimal". The title became "Who has tried to tabulate
  biology, and how each attempt holds up"; headers "counts", "misses", "evidence", "disease", in place of "what it
  says about treatment".
- **A fraction names its whole** (Numbers). an open call's about page, 2026-11-19: "3/8 of what? what makes them
  different?".
- **Say where a derived number comes from** (Text). a pitch deck, 2026-10-25: "where do 'numbers' come from? dont assume
  reader knows what a plate is, illustrate key concepts use more iconography". "3,773 numbers" became "3,773
  measurements of each image: size, shape, brightness, texture".
- **Every timing says per what** (Text). an art piece: "about 3 s a dream", "0.76 s a frame"; a bare "about 3 s" left the
  reader asking.
- **Illustrate the nouns a stranger meets first** (Text). a pitch deck slide 04, 2026-10-25: well, "one dish of cells";
  plate, "384 wells, imaged together"; lab, "one site, its own cells". a drug-mechanism deck, 2026-10-27: "it needs to be clear
  N+ = charged nitrogen"; glossed where it first appears and drawn as N⁺H with its partner Asp147 carrying a minus.
  a DJ tool's process page, 2026-10-27: "secret sauce too wordy ... show dont tell. simple system reveal, icons"; four text
  cards became four drawn tiles.
- **A borrowed finding names its author** (Text). a pitch deck, 06a, 2026-10-25: the source lived only in the PDF, and a
  reader asked "who is the author?". On the slide: "not directly comparable between imaging sites", EU-OPENSCREEN,
  four sites, 2025.

## P4. Meaning in the medium that carries it, words last

- **Short ledes, data over prose** (Text). a DJ tool, 2026-10-26: "summary: show dont tell, simple plots"; 2026-10-27:
  "bold/highlight main 1 sentence takeaway, then elaborate", "redundant with figure summaries? more vibes and
  feeling". a DJ tool's swap list, 2026-11-03: "too much text. this is rank order? show dont tell".
- **A grid holds phrases** (Text). a peptide explainer, 2026-11-05: "redesign: too many words, colors"; "link to the vendor,
  sumamrize offerings, if itss legal. too many words in grid right now". Phrases that work in a cell: "no company name
  or address", "USPS, plain mailers", "in-house NMR and HPLC only".
- **A count repeated as words becomes marks** (Numbers). Loop essay, 2026-11-19: "consider just '# loops' text once,
  then bars showing 1, 2 or 3"; "show dont tell here: use axis labels".
- **A split names each share on its segment** (Text). an art piece, 2026-10-26: "numbers not linked to artist/an art piece clearly";
  the bar became "artist 60% $9,400 | an art piece 40% $6,266".
- **One phrase lit per headline** (Text). The a drug-mechanism deck's habit, taken into a pitch deck on 2026-10-25: "Does my
  control *look like yours*?", "Six questions, six tools. *Use all of them.*"
- **An icon carries only words it renders** (Icons). a DJ studio header, 2026-10-24: "overlay/combine waveforms? no
  the wordmark text please (too small). make bigger, maybe round?"

## P5. Nearness and alignment claim relation

- **Group by what the reader does with it** (Composition). a DJ tool, 2026-11-06: "tags should be closer to set
  description text, these are both things to be copied". a public-health dashboard, 2026-11-08: "things should be connected and
  close to each other"; a drawing became a thumbnail flush against its name.
- **Every line belongs to something** (Composition). a pitch deck deck, 2026-10-15 to 10-20: "minimize floating text".
- **Comparable items are rows** (Composition). 2026-11-05 and 11-06: "avoid cards, prefer interactive tables";
  "again, prefer rows in table to cards".
- **Air between, tight inside** (Composition). a pitch deck's one-pager, 2026-11-01: "dense and wordy, needs more
  negative space"; "geom elements should have less negative space inside, tight element"; "timeline ... need a tick?
  a little disjointed".
- **Shared alignment claims a relation** (Composition). Same one-pager: "elements arranged similarly should relate ...
  do not align in shared grid".
- **Vary the organisation, give it a centre** (Composition). a peptide explainer masthead, 2026-11-05: "consider diamond
  arrangement not just row"; "more varied organiztion, use central connecting element, diamon can create interesting
  negative space for eye flow".
- **Connect related elements with lines** (Composition). an art piece's ring, 2026-10-26: "connect yellow icon to line",
  "icons should be larger, easy to see". a pitch deck, 09's timeline dots carry 1 to 4 and drop to their cards; 05b's
  batch in the drop zone has a dashed leader to its dot on the map ("points should be labelled with number", "use
  lines to connect related elements").

## P6. Few measures, held exactly

- **Uneven cards on one row grid** (Gotchas). a pitch deck, A4, 2026-11-09: "gigantic block of cold white not good look";
  the cards went onto one subgrid and were tinted, green for what is shared, pink for what stays yours, a pitch deck on
  white between them.
- **One left edge, two measures, one rhythm** (Composition). a DJ tool's about page, 2026-11-06: "consistent margins".
  a peptide explainer, 2026-11-05: "consistent margins"; "fig 2 legend is indented from legend border?"; left edges at 200,
  220, 320 and 960 became 220. Same page: 640 px prose centred in 880 px figures still read uneven, since the keys'
  rules spanned 880 while their swatches began at 640, four vertical edges ("some elements much wider than others is
  visually weird").
- **A row fills its rows** (Composition). an MoA explainer, 2026-11-17: four identity entries fell to 3 + 1,
  because four 180 px columns plus three 32 px gaps did not fit a 740 px band ("prefer 2 x 2 is 1x4 (one row) here -
  avoid weird overhang element always"). a peptide explainer BPC-157 property cards, 3 + 1, 2026-11-20: "pet peeve
  overhanging cell: prefer 2x2 matrix of blocks". Counts no grid divides: 13 drawer cards, 19 glossary terms.
- **Balance in every view** (Composition). a pitch deck, 02a and 02c, 2026-10-25: "negative space a bit awkward" after
  half the words moved to the PDF. a DJ tool header, 2026-10-27: title, menus and links with matched centres looked "off"
  until baselines matched within a pixel ("be meticulous about pixel-perfect alignment, element harmony").
- **Break lines at the sense** (Composition). a pitch deck's one-pager, 2026-11-01: "weird line style. start sentence
  new line. or, fit on one line", after "Nobody / calibrates". Resume summary beside the contact list, 2026-11-08:
  "awkward negative space here"; line ends 351 to 480 px became 404 to 443 with balance. a public-health dashboard, 2026-11-08:
  "fit this on one line avoid awkward overhang". CV, 2026-11-09: the web container was 6.1 in against 7 in in print,
  so "AI" fell to its own line and a heading wrapped under the date column ("avoid weird text overhang"); "Coursework"
  went over "Undergraduate and graduate: Python, ...".
- **Type reads at a glance** (Composition). Loop essay, 2026-10-25: a dozen 11 px labels raised to 12 after "does this
  follow best practices about text size, variety?".
- **Hold a distance floor** (Colour). a peptide explainer, 2026-11-21: in light mode a hot pink became raspberry, since the
  hotter pink folded into the vermillion for tritan readers; the rule came with "measure only pairs that share a
  figure".
- **design_budget colour count** (Checkers). a peptide explainer, 2026-11-17: 29 hexes were 15 roles × 2 themes, so
  `--colours 30` was the honest line.
- **Prune, then prove** (Checkers). a peptide explainer, 2026-11-05: classes 43/40 became 26/40, 61 selectors dropped,
  1,703 elements identical. A comment naming "head.html" read as the class `.html` and killed rules; a control built
  minutes earlier was worthless while another session edited the shared head.

## P7. The real thing over an imitation

- **Three real examples beat a word list** (Text). a DJ tool's process page, 2026-10-27: "more professional, 1 table.
  three examples using real DJ words. specific what moves" A list of accepted words and a second table of
  history had read as clutter.
- **Generated prose reads its numbers** (Text). a DJ tool's about page, 2026-11-03, the worked transition on set C: "123 to
  123 bpm, a 0.0% jump" became "both at 123 bpm".
- **Warnings borrow safety signage** (Icons). a DJ tool flags, 2026-10-26: "warning sign with symbol, learn from
  chem/fire safety symbols ... click on horses go to process definition".
- **Draw the palette from the work** (Colour). a DJ tool, 2026-11-03: one re-measure wrote the art's hot pink and cyan
  over the studio's rose and slate in the live studio, because a "keep the hand value if close" rule could not hold
  picks far from the art.
- **Measure the colour the browser paints** (Colour). a peptide explainer, 2026-11-21: a diagnosis from the spec, that deep
  shades drift purple, was wrong; Chrome kept the hue. A second measure of the merged palette found three tritan
  pairs under the floor that the search had passed.
- **A material obeys its physics** (Colour). a cover's lettering, 2026-11-04: "not physics enough", then "too much
  like slime"; the drips live in `the type generator` drips().
- **A hero graphic gets three concepts** (Gotchas). a peptide explainer's masthead hook, 2026-11-17: one concept refined three
  times left "did we test different versions?" open.

## Work lands once (work-practice §6)

- **One doc, two media** (Composition). 2026-10-26: "submission and web should be one doc"; an art doc prints as
  the 8-sheet submission, and the old Submission file only forwards to it.

- **Anything public is read at its rendered width** (Gotchas, P7). A README's file map wrapped on 11 of its 13
  lines, worst 104 characters, so every second column folded under its first and "html-slide-deck" broke as
  "html-slide-" / "deck"; the same map in the agent-facing file wrapped on 21 lines, and a sample report on 5.
  Seven green checks had called the page fine, because none of them measured width. The fix was a check:
  `tests/formatting.py` flags an aligned line (two or more spaces between visible text) over 78 characters inside a
  fenced block, and leaves a plain long command alone, since a long curl has nothing to misalign. (2026-11-21: "for
  any public ocntent, avoid embarassment, check for weird formatting failures, design should be consistent and easy
  to read".)
