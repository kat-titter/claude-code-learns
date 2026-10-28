---
name: html-docs
description: Makes and shares a document as one HTML page - report, brief, explainer, white paper, proposal or one-pager - with light interactivity (hover notes, folds, step-through figures) that still reads whole and prints whole as a PDF. Use when writing or revising an HTML doc, choosing between a page, an Artifact, a shared doc or a deck, or when a page feels heavy, app-like or prints badly.
when_to_use: Starting any document meant to be read in a browser; before adding interactivity to a doc; before sharing or publishing a page.
---

# HTML docs, lightly interactive

An HTML doc is one file that reads like a document, prints like a paper and answers the reader's hand lightly. The
deck is its sibling (html-slide-deck); this skill holds what both share. Guidelines, each with a case.

## Gotchas

- Folds and hover notes that hide content print blank: print with every fold open and every note inline (§5).
- Hover-only notes stay shut on a phone: each one opens on tap too (§3).

## 1 · Pick the medium first

| the work | lives as |
|---|---|
| A page people read and link to, kept with its code, often public | one HTML file in the repo, served by GitHub Pages (github-practice) |
| A private link to share today, with comments on the spot | an Artifact (private by default; republish to the same URL keeps the link) |
| Text several people edit, comment on and export to Word or PDF | a shared doc (Claude Docs, Google Docs) |
| A talk | an HTML deck (html-slide-deck) |
| A .docx or .pptx | only when someone asks for that file |

- **Often two at once**: the editable doc for the words, and the styled page beside it for the look. Example: a private
  investor brief, an editable doc with a page in the project's style published beside it (2026-10-25).
- **HTML first, the PDF beside it.** A PDF alone does not reflow on a phone, is harder to make accessible and goes
  stale; publish the page and print the PDF from it (GDS, 2018).
- **Decide before the first line**, since moving a page into a doc later loses the layout, and a doc into a page loses
  the comments.

## 2 · Shape of a doc

- **Plan before code**: the subject, the reader, the page's one job, a few colour and type tokens, and a sketch of the
  sections; then check the plan for choices that would fit any page (Anthropic's frontend-design skill).
- **One self-contained file, no build step.** Inline CSS, figures as inline SVG, at most one font link; a library, when
  one earns its place, loads from a CDN with its version in the URL. It opens straight from disk, and a footer links
  to its source (Willison, 2025). Photographs go beside the page as compressed files rather than data URIs: a deck with 3.7 MB of embedded images
  weighs 4.5 MB on every load and every diff (a pitch deck, 2026-10-26).
- **Masthead, then a contents rail** once the doc runs past about three screens: title, a one-line lead, date and byline;
  the rail is anchor links to each section.
- **Every section carries an id** (`<section id="method">`). Deep links work, and an edit can name its target ("tighten
  #method") instead of quoting a sentence that a later pass rewords.
- **A lead sentence per section**; the rest supports it. Reading width about 65 to 75 characters; one type scale; colour
  tokens on `:root` with a dark set (design-practice).
- **Print rules from the start**: `@page` margins, every fold open, controls hidden, motion at its end state, figures
  kept whole (`break-inside: avoid`). The PDF is the doc's second reader.

## 3 · Light interactivity

The page reads whole with no clicks. Each interaction adds a layer the reader asked for; nothing essential hides
behind one. When the reader should push a system and watch it answer, that is an explorable: use interactive-figures.

| move | for | built with |
|---|---|---|
| **Term card** | a word a stranger trips on | a dotted underline, `tabindex="0"`, a card that opens on hover, focus and tap |
| **Fold** | the method, the proof, the long list | `<details>`; open in print |
| **Click to step** | a figure built in the order you explain it | one click or key shows the next state; the last state is the printed one |
| **Layer key** | a second reader (sources, exact statistics) | one toggle or key that shows the reader's layer, as D does on a deck |
| **Linked highlight** | the same item in two views | hover or focus on one lights the other |
| **Anchor and copy** | sharing a spot, reusing code | a link on each heading; a copy button on each code block |

- **About one ask per screen.** A light doc carries under about 40 KB of script, in plain DOM calls rather than a
  framework; thirty hand-written lines beat a library. Example: a policy deck runs on 40 KB with no library and passes the audit clean.
- **Every hover has a tap and a focus twin.** Put each note in a focusable term with its card; a `title` attribute
  shows only to a mouse. Example: three dotted terms in a web essay kept their explanation only in `title` (2026-10-26).
- **HTML before script**: `<details>`, anchor links, `:target`, `scroll-margin-top`; script only for what markup can't do.
- **Motion answers the reader**: at most one orchestrated moment per page, the rest moving in response to a click or
  hover (frontend-design). Reduced motion and print show each animation at its end state.
- **The reader keeps the controls**: the page scrolls as they expect, snapping stays off a doc, sound and dialogs wait
  for their click, and prose sits on the page rather than inside dashboard chrome.
- **Shareable state in the URL** (`#method`, `?layer=sources`), so a view can be bookmarked and sent (Willison);
  browser storage only for conveniences like a remembered fold.

## 4 · Working on one with Claude

- **Name the section, see the render.** Ask for a change by section id; the answer is the edit plus a render of that
  section (`render-pages.py` on the printed PDF, or a screenshot), not a description.
- **Start from a page by name.** "Built like the white paper" lets Claude reuse that page's code and look instead of
  inventing a new one (Willison's remix pattern).
- **One visible change per pass**, small enough to steer. A round that touches every section gets a plan first and a
  before and after render (`render-pages.py` each printed PDF, then `slide-diff.py` the two PNG folders; works on any
  page).
- **One source.** When a build writes the page, edit the source and rebuild. Rebuild twice and compare
  (`stable-build.sh`) only when a build pass changed, not on every edit or publish (html-slide-deck, Edit passes that
  stay put).
- **Comments where the reader is.** On an Artifact or a shared doc, comment on the spot; Claude answers in that thread
  and republishes to the same link.

## 5 · Check before sharing

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/light-audit.py page.html        # add --deck for a deck, --json for tooling
```

It reads the file without a browser and reports weight (file, script, style, embedded images, outside hosts),
libraries loaded, what the page asks of the reader per 1,000 words, and care (print rules, reduced motion beside any
motion, dark mode, section ids, hover states with a focus twin, notes that only live in `title`). Then the browser
checks: interactive-figures' `audit_interactions.py` (targets, focus, clicks, no-JS frames), page-legibility-check
(contrast, overlaps, phone width), and a printed PDF read page by page (html-slide-deck's `print-pdf.sh`,
`render-pages.py`). After publishing, `verify-live.sh` confirms the live bytes.

Calibrated on 11 pages, 2026-10-26:

- **Clean**: a 40 KB policy deck, the reference for density.
- **Section ids missing**: a white paper (9 headings), a public explainer (14 headings, and no print rules).
- **Title-only notes**: a web essay (3 terms), with 47 KB of script.
- **Embedded images**: a pitch deck (3.7 MB).
- **An explorable, not a doc**: an interactive essay (653 KB of script, 47 buttons), which interactive-figures governs.

## Public examples this follows

- **Simon Willison, "Useful patterns for building HTML tools"** (2025-12-10): single files with no build, CDN
  libraries with versions, GitHub Pages hosting, copy buttons, state in the URL, a source link, remixing by name.
- **GDS, "Why GOV.UK content should be published in HTML and not PDF"** (2018-07-16): HTML by default; a PDF
  only beside an HTML version.
- **reveal.js, PDF export**: the deck reference; html-slide-deck maps its print options onto views and layers.
- **Anthropic's frontend-design skill** (github.com/anthropics/skills): ground the page in its subject, plan the
  tokens and layout before code, spend boldness in one place, motion sparingly, visible focus.

## Related

html-slide-deck (decks: views, talk and PDF layers, publishing scripts), interactive-figures (explorables),
design-practice (composition, colour), app-design (hover cards, controls, cache-busting), page-legibility-check, storytelling (the arc), github-practice
(Pages, READMEs).

## Provenance

Written 2026-10-26, then checked against the public examples above, from the request "how to best use and work with html slide decks and docs; design preference for
light interactivity", and from the pages above: hover notes on methods ("love the hover explain methods/words",
2026-10-25), hover or tap cards ("more legible text, less jumpy"), the private brief beside the editable doc
(2026-10-25), and the audit run on 11 of the author's pages.
