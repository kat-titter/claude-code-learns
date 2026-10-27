---
name: html-slide-deck
description: Build, check and publish a slide deck as one HTML page (GitHub Pages or any static host) with click views, a talk layer and a reader's PDF layer, a printed PDF, rendered PNGs for review, stable rebuilds and a verified live publish. Use when making or editing a pitch or talk deck in HTML, adding a click view or a slide, printing a deck to PDF, publishing slides to GitHub Pages, or when a slide looks right in code but wrong on screen.
when_to_use: Starting a web deck; adding or moving slides, views or boards; before every publish of a deck; after any edit to a deck's build passes; when a deck rebuild changes things nobody edited.
---

# HTML slide deck

A deck as one HTML file travels well: one link, one PDF, every number traceable to code. What decks share with HTML
docs (choosing the medium, light interactivity, the static `light-audit.py --deck` check) lives in html-docs. These
guidelines come from building the Datum Line pitch (Oct 2026) through many review rounds; adapt names to the project.

## Shape of the deck

- **One template per slide, one list of views.** Each slide is a `<template id="tN">`; a `META` list gives each slide
  its views (`steps`). The page mounts slides in `META` order and looks templates up by id, so a slide's id is its
  position. Inserting a slide renumbers everything after it; a new *view* on an existing slide renumbers nothing.
  Example: the "how labs answer it today" board became slide 02's third view instead of a new slide 03.
- **One action moves forward.** Click, space, arrow or a presenter's clicker shows the next view, then the next slide.
  Dots in the corner show the views (one dot per view, the current one filled). Every slide advances the same way, so
  the speaker can forget which slides step.
- **The public reference is reveal.js**: its fragments are this skill's views, and it prints each fragment as its
  own page unless told not to (`pdfSeparateFragments: false`), with speaker notes as an overlay or a separate page
  (`showNotes`). Here the printed deck shows each slide's final view, and the reader's layer plays the notes' role.
- **Two layers from one build.** The talk view shows what the room reads; the reader's PDF adds sources, figure legends,
  reference numbers and exact statistics. Mark reader-only text with a class (`pdf` removes it on stage, `pdfv` keeps its
  space so nothing moves) and give the web page a key (D) that shows it. Print the PDF without the hiding rule. Add the
  mirror class (`talk`: stage only, hidden in print and under D) when the two layers want different layouts of the same
  slot, such as big record tiles on stage where the PDF lists papers (Datum Line 02a, 2026-10-25).
- **Every number from code.** Builders read results files and assert what they claim (for example "this lab is the one
  dosed at a sixteenth"); a typed number is a number nobody can check.
- **Public and private side by side.** Static hosts serve the whole repo. Keep the speaker script and Q&A in a folder
  the repo ignores (`private/`), and let the publish check confirm it returns 404.

## One grid for every slide

- **Each kind of element in one place on every slide**, so the reader knows where to look: the claim top left (line 2
  its consequence, in the accent colour), the section tag top right, the evidence in one full-width figure zone at the
  same top and height (on a light card on dark slides, on the page on light ones), the key bottom left of the figure,
  axis titles above their axis at its left edge, sources in the reader's line, document links bottom right. (Datum
  Line, 2026-10-26: "key elements should be in the same place, reader know where to look for information".)
- **One type scale**: a short fixed set of sizes on stage, for example 22 (every label and line, the floor; the pitch
  skill says why), 28 (a second level), 44 (headlines and big numbers), 72 (the one hero number), display sizes on title
  slides only; figure titles bold at the label size, labels regular; icons 24 px or more and always beside a word. One
  font per role: the text face for words and numbers, mono only for small-capital labels, years and document links. Size
  SVG text in px through its figure's scale, or draw the figure 1:1 so a unit is a pixel: a figure scaled to its card
  shrinks every unit, so 25 units at 0.91 is a 22.8 px label beside 22 px HTML (Datum Line 05, 2026-10-26: "font types
  are too varied in size, font, format. especially the AMG slide"). Draw arrows, don't type them: web-font subsets carry
  no ↗ or →, so a typed one falls back to Menlo or Helvetica. Measure it: `scripts/type-audit.py stage.pdf --labels ...`
  fails any talk run off the scale or in a fallback font; `scripts/view-audit.py` lists each view's text sizes, icons
  under 24 px or without a label, bold and italic runs, and left edges 2 to 10 px apart.
- **Bold and colour on purpose**: bold for headlines, figure titles, the one key number and badge numerals; labels
  regular; italic only for a journal's name. Colour carries its one meaning (see design-practice).
- **Section tags read as chapters**, one form throughout ("The founder, The question, The gap, The test, The map ...
  The raise, The vision"), so the tags alone tell the story.

## Motion that tells the story

- **Each view plays in the order the speaker explains it, cause then effect.** Data first, then what it means: the wells, then
  each lab's numbered centre, then the distance drawn between two; a drift line traced through time, the flagged batches
  lighting as the line reaches them, then the drug answers' drop. A claim, then its number. Nothing moves that the story
  does not need. (Datum Line, 2026-10-26, the author: "animations: should add clarity, connect related elements. transitions add
  depth, tell story".)
- **Draw the claim instead of saying it.** A sentence that names a change becomes a small figure that performs it: three
  labs' clouds slide into one for "one aligned space"; a well flies onto the map and shrinks into its dot for "one well,
  one point". Ghost marks keep the start, so the printed end state still tells it. (Datum Line, 2026-10-26: "show not
  tell via figure, use animation creatively and cleverly".)
- **One vocabulary, few verbs**: rise (a card), pop (a mark or number arrives), draw (a line traced, `pathLength="1"`), pulse
  once (the protagonist's mark, lab 2's pink), drop (something arrives from above). A dashed line can't be drawn with a
  dash offset; grow it with scaleX or fade it.
- **Slide to slide, depth**: a scroll-linked scale and fade (`animation-timeline: view()`) lets each slide come forward at
  the centre and recede as it leaves; desktop only, off with reduced motion.
- **Pause each view's motion until it is on screen** (one helper builds the paused and running rules for every motion class),
  settle every animation at its end state in print, and check frames on a virtual clock (headless Chrome
  `--virtual-time-budget` at 0.4, 1.3, 2.2 and 4.5 s) before calling the order right.

## Edit passes that stay put

Build passes that rewrite a stored HTML file are powerful and drift easily. These patterns keep them honest:

- **Rebuild twice and compare bytes when a pass changes**, not on every edit or publish:
  `scripts/stable-build.sh index.html -- <build cmd>`. A second build that differs means a pass is still acting on its
  own output, so each build would drift further and diffs would show changes nobody made. A wording, content or style
  edit on an unchanged builder needs one build; its git diff shows anything that moved unasked (2026-10-26, the author: "why
  check deck build 2x? purpose of this? always necessary?").
- **Key a pass to structure, with a guard for absence.** A pass found its target by its old wording ("Untreated wells
  from 11 labs"); once a later pass renamed it, the first pass quietly stopped. Match both spellings, or a stable class.
- **Scope cleanup to the elements you added.** A cleanup that stripped `position:relative` from every tile also hit
  unrelated tiles; the next build then stretched them. Match the exact element (its alt text, its class).
- **Redraw generated pieces each build** (strip, then add) when a later pass recolours or rewrites them.
- **Templates a pass expects may move or go.** Let the shared helper return the deck unchanged when a template is
  missing, so moving a board into the talk is one function, not ten guards.
- **A slide kept as stored HTML and changed only by passes resists redesign.** Each edit patches the last patch, so
  edits stay small and a deep one breaks something (Datum Line 02 and 03: about 90 string replacements and ten regex
  passes over hand-built HTML; a grid regex swallowed the tiles twice). Before a deep pass, move such a slide into a
  builder that draws it from data, as the deck's other slides are. The safe move: write the built HTML to a template
  with `{{asset:mime:path}}` marks for its images, have the builder fill them (and draw any figure from data), hold the
  slide out of the passes, and prove two builds byte-identical before the first redesign (Datum Line 02 and 03, 26 Oct).

## Look at every view

- Print with `scripts/print-pdf.sh deck.html deck.pdf PROFILE_DIR`. Give each parallel print its own profile directory;
  a shared one silently prints nothing.
- Render with `scripts/render-pages.py deck.pdf out/ --labels 01,02a,02b,...` and read the PNGs of every slide you
  touched. Overflow, a caption crossing a column, text under an overlay and a label beyond its card show only rendered.
- **Check the printed reader layer on its own.** It prints captions and notes the stage never shows, so a stage check
  passes while a caption sits on a legend. `scripts/pdf-overlaps.py deck.pdf --labels ...` lists text on text in the PDF
  (Datum Line, 2026-10-26: the live deck's PDF had 70 such pairs on 05a, 08 and A22 that every stage check had passed).
- Measure with `scripts/deck-stats.py stage.pdf --floor 22`: words per page, smallest text, runs under the floor,
  decimals, separator dots. Use it before and after a pass so "less text" and "bigger text" are numbers.
- **Quote every attribute a builder writes.** In inline SVG parsed as HTML, `opacity=.55/>` takes the slash into the
  value, the element never closes, and what follows renders as its child, invisibly (Datum Line 04b, 2026-10-26: the
  "4.4×" label was in the page and on no screen). A scan of the built page for `=[^"' ]+/>` finds them.
- For figure legibility (contrast, label collisions, phone width), pair with the page-legibility-check skill.
- For weight and interactivity, run html-docs' `light-audit.py deck.html --deck`: script and embedded-image size,
  libraries, hover states without a focus twin, notes that only live in `title`, print and reduced-motion rules.
- Check the live page in a browser after publishing: step through the changed slides and read the console.

## Publish and confirm

1. Commit the built page and the printed PDF together.
2. Push, then `scripts/verify-live.sh https://USER.github.io/REPO index.html deck.pdf --private private/script.html`.
   It waits until each file is served byte-identical (cache-busted) and confirms private paths return 404.
   List only files Pages serves as they are: its Jekyll build turns Markdown into pages, so a `.md` path 404s and the
   wait never ends; compare those on `raw.githubusercontent.com` at the pushed commit (claude-code-learns, 2026-10-26).
3. Report the commit, the match and the 404, with the two links.

## Long runs on a shared machine

Rendering and analysis share the Mac with other jobs. Check `sysctl -n vm.loadavg` and swap before a long job, and see
macos-long-render for BLAS threads and keeping the machine awake.

## Rounds that change every slide

When asked to revise every slide, write the per-slide plan first (slide, the visible change, the reason) and show it;
after the round, render before and after and run `slide-diff.py`. A slide that changed under about 8% of its pixels was
not revised: change it or say why it stays. Report the count ("11 of 15 views changed visibly"). Consistency fixes
(type scale, bold, alignment) are worth doing but are not the redesign that was asked for.

- **Default to more edits, even when the request names a few.** Audit every view against the deck's current guidance
  (the pitch skill's beats, word budget, conclusion on the chart, type, icons) and change what fails; after a skill or
  research update, apply each of its sections to each view. Reshape the figure or the words that carry the idea rather
  than adding a strip beside them, and show the slide-diff table against the live deck with words before and after.
  Case: Datum Line, 2026-10-26, three beat fixes landed as three strips (3 of 15 views changed) right after research
  had rewritten the pitch skill ("debug why html slide edits seem too shallow, stable. prefer more edits!").

## Reviews that pay for themselves

A handful of reviewers, each with one lens (legibility, story, science, design), and one skeptic per finding that
changes a number, find what matters. Thousands of verification agents mostly re-confirm style notes: in one deck review,
7 reviewers × 94 findings × 3 verifiers reached the usage limit after 24 agents (narcan deck, 2026-10-17).

## Scripts

| script | does |
|---|---|
| `print-pdf.sh IN OUT [profile] [ms]` | headless Chrome print that waits for the file |
| `render-pages.py PDF OUT [--labels] [--only]` | one PNG per page, named by view |
| `deck-stats.py PDF [--css-width] [--floor]` | words, smallest text, runs under the floor, decimals, dots per page |
| `stable-build.sh OUT -- CMD` | two builds, byte-compare, shows the first difference |
| `verify-live.sh BASE [--private P] FILES` | live bytes match local; private paths 404 |
| `slide-diff.py BEFORE AFTER [--min 8]` | share of pixels each view changed; flags views under the bar as barely changed |
| `view-audit.py INDEX OUT` | per view: text sizes, icons under 24 px or without a word, bold and italic runs, near-miss left edges |
| `type-audit.py PDF --labels L [--talk N] [--scale S] [--fonts F]` | every talk run on the type scale and in the deck's own fonts; exits 1 on any miss |
| `pdf-overlaps.py PDF [--labels L]` | text on text in the printed deck, shadows and duplicate layers skipped; exits 1 on any pair |

PyMuPDF for the Python scripts: `python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf`.

## Related

html-docs (medium, light interactivity, `light-audit.py`), pitch-deck-story (what goes on the slides), design-practice (composition, legends, axes, colour),
controlled-comparisons (when a slide compares data), page-legibility-check, macos-long-render.

## Provenance

Datum Line deck, 2026-10-15 to 2026-10-20: one-button navigation ("They should all click"); the stage/PDF layers after
the "is it human?" review; a pass keyed to old wording that stopped matching after the DMSO renaming; a cleanup that
stretched A16's planted-fault tiles; the A25 board moved into slide 02 as a view ("appendix slide A25 should be in main
pitch"); prints and live checks after every push.
