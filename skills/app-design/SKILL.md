---
name: app-design
description: Designs apps people come back to - studios, tools, dashboards, games - and the interactive parts of any page, from the first screen to controls that look pressable, short hover cards, linked highlights, one code per state, waits and failures that show. Use when building or reviewing an app's UI, or a page's controls, hovers or states, or on "where do I click?", "not discoverable" or "is it still loading?".
when_to_use: Before building an app screen, or adding controls, hovers or states to a page. Composition, text and colour go to design-practice, responsive figures to interactive-figures.
---

# App design

How the apps people come back to (a studio, a tool, a dashboard, a game) and the interactive parts of any page behave.
Eight principles come first; every rule below is a case of one, tagged P1 to P8, with a few words of where it came
from. Long cases and the words behind them: [references/cases.md](references/cases.md). The sections run in the order a
person meets an app: the first screen (§1), its controls (§2), the hovers that explain them (§3), the states that answer
back (§4), and what makes great apps great (§5). Every screen also follows design-practice, whose P1 to P7 apply here as
written and are cited by name; figures that respond add interactive-figures.

## Principles

1. **The first screen is the work, in the order it is used.** Subject and main actions lead; process and totals sit lower.
2. **The control invites the action; no sentence explains it.** What responds looks pressable, what only reads stays still.
3. **A control takes the shape of its job and sits on its object.** Discrete or continuous as the thing is, on the thing.
4. **The frame holds still.** Only what the person moved moves: header, axis, widths and folds keep place in every state.
5. **A hover answers one question, short.** The item under the pointer and its one value; a card that teaches in a line.
6. **The system answers at once and never goes quiet.** A press answers at its control, a wait shows it is alive.
7. **The person keeps control.** What they asked for stays in view, a verdict can be taken back, stop means now.
8. **Borrow the conventions people already know.** A drawn star, a stop square, a frozen header row read at once.

The canon behind them, linked rather than copied (hci-principles §5): P2 is Norman's signifiers, P3 his mapping, P6
Nielsen's visibility of system status, P7 user control and freedom with Shneiderman's easy reversal, P8 Jakob's law and
consistency and standards; the laws of sizes and counts sit in [references/great-apps.md](references/great-apps.md).
Owned elsewhere: one state, one code on every view is design-practice P2 applied to states; work lands once
(work-practice §6).

## Gotchas

- **A bare spinner reads as broken** (P6): 4 to 7 s of empty skeletons, then a failure nobody saw coming. Name every
  wait and show a failure on its own card (a DJ tool, 2026-10-27; §4).
- **A filter hid what the person asked for** (P7): a full-track take they requested was folded away for departing from
  a guideline. Show it, flagged (a DJ tool; §2).
- **A state class named like a page component borrows its style** (P4): left-out rows as `tr.drop` took the file drop
  box's `.drop` (centred, padded, dashed), and a new row's `tk-new` wore the new-take flash's outline. Grep a class name
  before using it and name state classes apart (a DJ tool, 2026-11-16).

## 1. The first screen

- **Main actions first, in the order they are used** (P1): the thing to play, the way into the work, the progress in
  flight; tools quiet to one side, summary numbers lower (a DJ tool, 2026-10-27).
- **Where you are reads as one line of nested menus** (P1): who > what > which version, each its own drop-down (a DJ tool,
  2026-10-27).
- **Stack by importance, the tool's subject on top** (P1): a transitions tool draws its transitions above the sound they
  sit on, then the rest from most to least important; table columns run the same way, each one toggles. A workspace
  takes the full page width, a reading page its measure (a DJ tool, 2026-10-27).
- **A workspace shows the work** (P1): how it was made lives on the process or about page, its own page in the app's
  style and words, each concept linked to its place in the app and back (a DJ tool, 2026-10-26 and 10-27).
- **Freeze the axis everything hangs on** (P4, P8): rows that share one axis (a timeline, a set's minutes) get it as a
  ruler that sticks to the top, like a spreadsheet's frozen header row; every row shares its x exactly, a crosshair runs
  through, and the axis gets the width, not the margins (a DJ studio, 2026-11-06).
- **A fold opens downward and moves nothing above it** (P4): label, chevron and summary keep their place shut and open,
  the label on the row's top in both; measure the boxes before and after a toggle (a DJ tool's checks fold, 2026-11-06).
- **A working panel keeps one width, and one thing keeps one shape through its states** (P4): a status list (render
  queue, uploads) floats as a tray that folds to a pill, never a column squeezing the panel. Made, being made and the
  row that makes more share one grid cell for cell, so a state changes the fill, not the outline; measure each row in
  every state (a DJ studio, 2026-11-16).
- **Pages of one app share one header, pixel for pixel** (P4): same width, height and positions on every tab,
  `scrollbar-gutter: stable`, space reserved for any element only one page has; measure both pages (a DJ studio and
  about, 2026-11-06).

## 2. Controls

- **Class honesty: a control has the shape of the quantity it sets** (P3): a switch or segmented toggle for states with
  nothing between them, a slider for a dose, a time or a rate. Read the claim the page makes, then pick the control
  (an essay Figure 1, 2026-11-19: a line-to-loop slider in an essay about all-or-nothing closure).
- **An action sits on the thing it acts on; app-wide help sits in a corner with its word** (P3): "export set" at the
  right end of the set's row; the guide as an icon plus "guide" at the header's right end, apart from the tabs (a DJ tool
  studio, 2026-11-06).
- **Whatever responds looks like it does** (P2): every control, drop-down arrows and tags included, shares one shaded,
  slightly raised style (soft fill, faint top highlight, small shadow). A way into a detail is that button, labelled
  with the thing, its state and a chevron, 34 to 44 px tall (a DJ tool, 2026-10-26 and 10-27).
- **The marks themselves are the way in** (P2): a mark that opens something is a raised disc that lifts under the
  pointer; its key stays a key, not buttons, and repeats no count the marks already show (a DJ tool, 2026-10-27).
- **An action is its symbol, its words in the hover and label** (P8): copy, stop ■, export with the service's mark; two
  actions that look alike stay two buttons, copy apart from export (a DJ tool).
- **A live tool steers by choice first, words second** (P3): hands are busy mid-performance, so each common change is
  one press on a named choice ("ease B in"), with a text field under them for the rest (a DJ tool, 2026-10-27).
- **Controls in one group are siblings** (design-practice P2): one height, one padding, none shaded alone; a legend's
  classes are one pill each with its own mark, an ordered class one gradient dot, and marks that are not classes take
  their own row (a DJ tool, 2026-10-27).
- **Two inputs doing one job are one element, and a control with nothing to choose goes** (design-practice P1): "more
  takes: prompt [field] auto" in one panel; a versions menu holding one version goes (a DJ tool, 2026-10-27).
- **A label is its own control** (P3): a column's header is the pill that shows or hides it; hidden columns wait on one
  line named positively, "more columns" (a DJ tool's tracks table, 2026-10-27).
- **Let the real control show itself** (P2): the thing itself responds (hold the handle and the water drains), cued by a
  quiet pulse in the highlight colour that stops after first use, in place of an instruction line or a drawn gesture. A
  fact like a duration is told once, where the reader meets it (an art doc, 2026-10-26).
- **Show rather than tell, for interactions too** (P2): a pointer cursor or a ▶ riding the hover line invites the
  action; the how-to sentence goes, even behind a "?" (a DJ tool, 2026-10-27).
- **A hover state promises a response** (P2): only what acts on click, tap or focus changes on hover; a block that is
  only read keeps one look. In a linked view the control lights its targets, and the targets leave each other alone
  (a peptide explainer, 2026-11-20).
- **An interaction's note sits beside what you interact with** (design-practice P5): the handle's note by the handle,
  a key on the lines it explains, as an icon at the start of each line rather than a detached key row (an art doc,
  2026-10-26).
- **Two controls that sound alike get two names and two marks** (design-practice P2): a faucet handle and a wall power
  strip were both "the switch" until a reader asked which (an art piece, 2026-10-26).
- **A list of options has one action, for the selected row** (P3): a press selects (outline, rank in ink); one button
  under the list names the choice ("swap in Hyper Saw"), arms on the first press and acts on the second; arrows move,
  Enter arms and acts. A control repeats per row only when it does something different there, such as a preview
  (a DJ tool's swap list, 2026-11-03).
- **Controls that act on a selection stay in place** (P4): faded until there is one, so a selection leaves the page
  where it was; a mode group always has one mode on, the common one first (a DJ tool's map gate, 2026-10-27).
- **What the person asked for stays in view, whatever a filter says** (P7): it wears its warnings as flags, with the
  action to accept it anyway; filters are for the system's own extras (a DJ tool, Gotchas).
- **Generous hit areas** (P2): 44 px touch targets, wide invisible strokes on thin lines; on phones a tap shows the card.

## 3. Hovers and linked views

- **Hover or tap cards carry explanations** (P5): larger text and a steady layout, floating inside the viewport beside
  the item; keyboard focus opens them too.
- **A hover says what is under the pointer, short** (P5): the item and the one value pointed at, with its unit ("05
  Bloom Again, danceability 86 / 100"), never every field of the row (a DJ tool, 2026-10-27).
- **A measure's name opens a card in the docs' term format** (P5): figure, name, one line, the figure being the method,
  its parts as bars of their weights read from the code, titled for what it shows ("this set, song by song"). A key's
  explanation takes the same card: symbol, name, one line, then short value-meaning rows (a DJ tool, 2026-10-27).
- **A hover earns its highlight.** A mark that lights up and reveals nothing is decoration: either the hover shows what the mark is (its source, its number) and a click opens the verifiable source, or the mark takes no hover state at all. On a timeline each event links to the primary or news report it rests on (a peptide explainer, Figure 17, 2026-11-21: "hover and click should link to verifiable news source. right now highlighting nothing"). A card that repeats the label, the value or the axis adds nothing: it carries what the plot cannot show (the study, its n and method, what limits the number), and a click goes deeper, to the reference (a peptide explainer, Figure 12, 2026-11-21: "hover information is duplicate of information already on plot and axis. more useful to click out to link with references/citations here, go deeper on result").
- **A hover gloss teaches** (P5): one plain sentence, a small drawing when the idea is spatial, a link to the primary
  source; it stays open as the pointer moves in, and opens on tap.
- **Size a hover card's label column to the longest label** (P5): in `ch` (12 characters: 12.5ch), not a guessed `em`;
  measure label right edge against bar left edge (a 4.6em column ran "conversation" into its bar).
- **Linked highlights** (design-practice P5): hovering an item in one view lights it in the others. Position and order
  link too: a transition sits as a node where its two tracks' bars meet, and its hover lights that stretch in every plot
  (a DJ tool, 2026-10-26).
- **One number per item, the same on every view** (design-practice P2): a take's number is its order of creation, on
  its card and beside its mark on the map (a DJ tool, 2026-10-27).
- **An expanded view reads as a pop-up of what opened it** (design-practice P5): one edge shared by source and panel,
  a tail to the source; a preview shows the gist, and the detail's marks live in the expanded view or show while their
  chip is hovered (a DJ tool, 2026-10-27).

## 4. States and waits

- **A state has one code on every view** (design-practice P2): one colour and one glyph per state, defined once as
  tokens (`--kept`, `--work`) and used by path, marks, buttons, cards, map and key alike; a state in progress gets its
  own faded, dotted glyph rather than a colour already taken (a DJ tool, 2026-10-27).
- **The mark alone says a row's state** (design-practice P2): a left-out row keeps its alignment and type, with no
  strikethrough or fade (a DJ tool, 2026-11-16).
- **A toggle's icon is drawn, in the field's convention** (P8): inline SVG in `currentColor`, outline when off and
  filled when on (GitHub's and Gmail's star); a text glyph can fall back to another font (★ read as an asterisk; a DJ tool,
  2026-10-27).
- **One table per kind of thing, every state in it** (design-practice P2): each row wears its state's mark under a key
  of the same marks, each a pill that shows that state alone, never a second table for one state. Rows are one height
  (one line per cell, an ellipsis, the whole on hover); the row's own control wears the mark; a value states share
  reads the same in each, colour the only difference (a DJ tool's tracks table, 2026-10-27).
- **Glow means live** (P6): only what is happening now glows (the take in the mix; a new take not heard yet, as a slow
  soft gray pulse). A state at rest keeps its edge and glyph, a chosen item the size of the rest, and the rest a thin
  gray edge, never a heavy white. The glow wears the item's own state colour, never the chosen one (a DJ tool, 2026-10-27
  and 11-03).
- **A given verdict can be taken back** (P7): a pressed verdict button is a toggle; the second press or its key retracts
  it, its hover says so ("un-Keep  K"), the record keeps the retraction with its time and target, and the item returns
  to its to-review look everywhere; the button's geometry stays (a DJ tool, 2026-11-03; GitHub's star is the convention).
- **What is playing looks the same everywhere** (P6): filled in the accent, a bar running along it, a second press
  pauses. In a table the playing row is the player: its lower edge the bar (press to seek), its title cell the clock;
  the played fill is the position, so no dot repeats it (a DJ tool, 2026-10-27).
- **Anything that waits shows it is alive** (P6): elapsed time and an estimate ("drawing 0:23, about a minute"); new
  work appears at once as grayed cards that fill as they load; a failure says so on its own card, with the reason and a
  retry (a DJ tool, 2026-10-27).
- **Stop means now; a queue takes any number** (P7): stop is a square that ends the running job too. A queue bounds only
  what runs at once (the machine's slots), nearest the person first; a press that finds nothing left draws afresh; the
  column ends in one control that empties it, waiting first, then running on a second press that says how many (a DJ tool,
  2026-11-03).
- **Something generated says why, how many, and can be made again** (P7): tags or takes show why they were chosen and
  their count, regenerate with a chosen count, remake themselves when their inputs change, and default to the
  platform's own limit held in one place (a DJ tool tags, 2026-11-03).
- **A working view carries no build stamps** (design-practice P1): "updated" lines go (a DJ tool, 2026-10-27).
- **Cache-bust changed assets** (P6): `?v=...`, so open tabs show the change on reload.

## 5. What makes great apps great

Read [references/great-apps.md](references/great-apps.md) when building or reviewing an app people come back to: the
primary action, one affordance per kind, answers within 400 ms, the plain story first, fewer choices first, entry points
at the top, a stable frame, true phone layouts, momentum without tricks, a switch between versions, borrowing the
conventions people already know. Before a publish, run design-practice's page audit (first screen, states, touch
targets) and page-legibility-check at desktop and phone widths.

## Related

design-practice (composition, text, icons, colour, the page audit), hci-principles (design rationale, heuristics,
affordances: the canon for P2, P3, P6 to P8), interactive-figures (figures that respond), figure-design (axes and
legends), page-legibility-check (measure), field-vocabulary (labels), the person's style skill.

## Provenance

Split from design-practice on 2026-10-27 at 251 lines, by task: pages and slides stayed there, apps and interaction came
here ("Split design-practice by task: pages/slides vs apps/studios, keep one owner per guideline"). Cases from the
a DJ studio (2026-10-14 to 2026-10-27, from "hover to explain flags instead of drop down (more legible text, less
jumpy)" on), the an art doc and an art piece (2026-10-26) and the 2026-10-24 studio design audit behind great-apps.md.
2026-11-21: restructured principle-first, eight principles with every rule tagged to one or to design-practice's,
long cases and quotes moved to references/cases.md ("the skills seem a little bit too literal").
