---
name: app-design
description: Designs apps people come back to - studios, tools, dashboards, games - and the interactive parts of any page, from the first screen to controls that look pressable, short hover cards, linked highlights, one code per state, waits and failures that show. Use when building or reviewing an app's UI, or a page's controls, hovers or states, or on "where do I click?", "not discoverable" or "is it still loading?".
when_to_use: Before building an app screen, or adding controls, hovers or states to a page. Composition, text and colour go to design-practice, responsive figures to interactive-figures.
---

# App design

Guidelines for the apps people come back to (a studio, a tool, a dashboard, a game) and for the interactive parts of any
page, each with the case it came from. Every screen also follows design-practice for composition, text, icons and colour;
figures that respond add their craft from interactive-figures. The sections run in the order a person meets an app: the
first screen (§1), the controls on it (§2), the hovers that explain them (§3), the states that answer back (§4); the
principles behind them, with their cases, are in [references/great-apps.md](references/great-apps.md) (§5).
Why one design over the designs it could have been (QOC) and the heuristics canon: hci-principles.

## Gotchas

- A how-to sentence under a control is telling, even behind a "?": cut it and let the control invite the action (§2).
- A bare spinner reads as broken (a DJ tool: 4 to 7 s of empty skeletons; "spinning circles of doom ... then failed"): name every wait and show a failure on its own card (§4).
- A filter folded away the take the person had asked for: what they asked for stays in view, flagged (§2).
- A row's state class named like a page component borrows its style: a DJ tool's left-out rows were `tr.drop`, and the
  stylesheet's `.drop` (the file drop box) centred, padded and dashed them. Name state classes apart (grep the name first: a new row called `tk-new` wore the new-take flash's outline, 2026-11-16); let the mark alone
  say a row's state, with no strikethrough or fade ("excluded songs should always be left-aligned, no strikthrough").

## 1. The first screen

- **The first screen is the main actions, in the order they are used**: the thing to play, the way into the work, the
  progress of the work in flight; tools quiet to one side, counts and summary numbers with the summary further down
  (a DJ tool, 2026-10-27: "make great first impression: play set, dive into transitions, see transition render progress"). Where
  you are reads as one line of nested menus, who > what > which version, each its own drop-down ("show user, set, version
  more clearly (nested drop down)").
- **Stack by importance, the tool's subject on top.** What a tool is for leads (a transitions tool draws its transitions
  above the sound they sit on), then the rest from most to least important (tempo, vocals, then the other measures);
  table columns run the same way, each one toggles. A workspace uses the full page width; a reading page keeps its
  measure. (a DJ tool, 2026-10-27: "this is a transitions tool"; "tempo then vocals then metrics below set (most to least
  important)"; "organize columns roughly from most to least important, toggle columns on/off"; "use full page width".)
- **A workspace shows the work**; how it was made (run steps, definitions) lives on the process or about page (a DJ tool,
  2026-10-26: "this should be covered in process not studio? studio is workspace"). The about page stays its own page in the app's own style and words, each concept
  linked to where it lives in the app and back (2026-10-27: "dont merge with studio, but use same style and concepts as studio,
  connect concepts and design principles").

- **Freeze the axis everything hangs on.** When a page's rows share one axis (a timeline, a set's minutes), make that axis
  a ruler that sticks to the top when scrolled past, like a spreadsheet's frozen header row, and let every row share its x exactly,
  with a crosshair through it; give the axis the width, not the margins (a DJ studio, 2026-11-06: "I should always be able to
  orient myself in this x-axis space ... lock it at the top ... like how Excel will lock a row at the top").
- **A fold opens downward and moves nothing above it.** Its label, chevron and summary keep their place shut and open (label
  aligned to the row's top in both states); only what is below moves down. Measure the boxes before and after a toggle (a DJ tool
  checks fold, 2026-11-06: "when drop down checks, the position moves - please try to keep consistent").
- **A working panel keeps one width, and one thing keeps one shape through its states.** A status list (a render queue, uploads)
  floats as a tray that folds to a pill; it never takes a column that squeezes the panel being worked in. What is made, what is being
  made and the row that makes more sit on one grid, cell for cell (number, disc, name, buttons, a lane the picture's size, time), so
  a state changes the fill, not the outline; measure each row's width and height in every state (a DJ studio, 2026-11-16: "transition
  window should always be same width, renders in progress narrows window ... consistency in shapes important").
- **Pages of one app share one header, pixel for pixel.** Switching tabs moves nothing in the header: same width, height and
  element positions, `scrollbar-gutter: stable` so a scrollbar on one page does not shift the other, space reserved for any element
  only one page has; measure the boxes on both pages (a DJ studio's two pages, 2026-11-06: "weird jump when about is toggled").

## 2. Controls

- **Class honesty: a control has the shape of the quantity it sets.** Discrete where the thing is discrete, continuous where
  it is continuous: a switch or segmented toggle for states that have nothing between them (line or loop, on or off), a
  slider for a dose, a time or a rate. A slider over a two-state choice claims states that do not exist, and a stepper over
  a real continuum hides them. Read the claim the page makes, then pick the control (an essay's Figure 1,
  2026-11-19: a line-to-loop slider in an essay whose point is that closing is all or nothing; "line> loop is portrayed as
  continuous, should be discrete switch"; "class honesty. use discrete where discrete, continuous where continuous").

- **An action sits on the thing it acts on; app-wide help sits in a corner with its word.** Export of a set goes at the right end of
  the set's own row as "export set", not in the page header; a guide is a small icon plus the word "guide" at the header's right end,
  apart from the tabs, never a bare icon among them (a DJ studio, 2026-11-06: "this is the export of the set ... maybe in the set
  space"; "some indication it's a guide should be a little bit more obvious ... top right ... a little sparkle button").
- **Whatever responds looks like it does**: every control shares one shaded, slightly raised style (a soft fill, a faint
  top highlight, a small shadow), drop-down arrows and tags included. A way into a detail is
  that button with a label naming the thing, its state and a chevron, 34 to 44 px tall; a quiet text line between rows is
  not found (a DJ tool, 2026-10-26: "where to click to tunnel into transition? elements should be easily discoverable";
  2026-10-27: "interactivity should be clear throughout studio: shaded button style, consider adding slight depth.
  applies to drop down arrows"; tags "almost like buttons"). The marks themselves are the way in: each transition's circle
  is a raised disc that lifts under the pointer, and the key beside them is a key, never a row of buttons, nor counts the
  marks already show ("transition legend why are these buttons? individual transition circle > see renders"; "2 kept 8
  to review seems unnecessary, this is shown"). An action is its symbol (copy, stop ■, export with the service's mark), its
  words in the hover and the label; two actions that look alike stay two buttons (copy to clipboard apart from export to
  SoundCloud).
- **A tool used live steers by choice first, words second.** Hands are busy and talk is hard mid-performance, so each common change is
  one press on a named choice that acts at once ("ease B in", "ride the tempo up", "hit harder on the drop"), with a text field
  under them for the rest (a DJ tool, 2026-10-27: "choice better than words? hands on UI/UX to make choices. hard to speak when DJ live!").
- **Controls in one group are siblings**: one height, one padding, no single one shaded (a DJ tool, 2026-10-27: "why set has
  shade region not other two?"). A legend's classes are all the same pill, each with its own mark (an ordered class is one
  gradient dot, not three dots and "1 to 13"); marks that are not classes sit on their own row ("why two buttons classes?
  ... each unique"). Two inputs that do one job are one element: "more takes: prompt [field] auto", not two
  panels. A control with nothing to choose goes (a versions menu holding one version: "no user interaction, element not
  necessary").
- **A label is its own control.** A column's header is the pill that shows or hides it, and what is hidden waits on one line
  named positively ("more columns"), never a second row of chips repeating the headers (a DJ tool's tracks table, 2026-10-27: "column
  toggle buttons redundant with column text labels"; "instead of put away, 'more' ... keep it positive").
- **Let the real control show itself.** Make the thing itself respond (hold the handle and the water drains) and cue it
  with a quiet pulse in the highlight colour that stops after first use; neither an instruction line nor a drawing of the
  gesture (an art doc, 2026-10-26: "touch the water → it follows ... telling, not showing", then "line and bubble icons
  not helpful"). Tell a fact like a duration once at most, where the reader meets it (the 2 minutes of a loop: a dot
  that runs the ring in two real minutes, "2 min" written only at its centre).
- **Show rather than tell, for interactions too**: no sentence explains a control, not even behind a "?"; the control invites
  the action itself (a pointer cursor, a ▶ riding the hover line on a sound bar). (A DJ tool, 2026-10-27: "press or drag to play
  from there: unnecessary text, please remove. interaction should be obvious from design".
- **A hover state promises a response.** Only an element that does something on click, tap or focus changes on
  hover; a card, row or block that is only read keeps one look (a compound explainer's property cards, 2026-11-20: "why is
  this a hover to highlight? unnecessary if not interactive"). In a linked view the control lights its targets, and the targets (rows, cards) do not light each other on their own hover: the matrix and the vial drawer had both, and only the site pills kept a hover (same day).
- **An interaction's description sits beside the thing you interact with**: the handle's note next to the handle, the
  water's note under the live water, rather than in a separate strip below (an art doc, 2026-10-26). A key belongs on the lines it
  explains: an icon at the start of each headline line beat a detached key row ("this is a little unclear").
- **Two controls that sound alike get two names and two marks.** The faucet handle (marked with the power symbol, rests
  the GPU while held) and the wall's power strip (turns the piece off) were both called "the switch" until a reader asked
  "behavior of switch on wall vs sink?".
- **A list of options has one action, for the selected row**: a press on a row selects it (an outline, its rank in ink),
  one button under the list names the choice ("swap in Hyper Saw"), arms on the first press and acts on the second;
  arrows move the selection, Enter arms and acts. A control repeats per row only when it does something different on
  each row, such as that row's own preview (a DJ tool's swap list, 2026-11-03: eight identical 'swap in' pills, "avoid having
  so many swap in buttons? consolidate design").
- **Controls that act on a selection stay in place**, faded until there is one, so a selection never moves the page; a
  mode group always has one mode on, the common one first (a DJ tool's map gate, 2026-10-27: "default lasso always on, prevent
  jumping around"; the include/exclude row had appeared only on a selection).
- **What the person asked for stays in view, whatever a filter says**: a thing made on their request shows its
  warnings on it as flags, with the action to accept it anyway. Filters are for the system's own extras. (a DJ tool: the
  full-track take the person asked for was folded away for departing from a guideline, and they asked to see it.)
- Generous hit areas (44 px touch targets; wide invisible strokes for thin lines); on phones a tap shows the card.

## 3. Hovers and linked views

- **Hover or tap cards** for explanations: larger text and a steady layout. Cards float inside the viewport beside the
  hovered item; keyboard focus opens them too.
- **A hover says what is under the pointer, short**: the item and the one value being pointed at, with its unit ("05 Bloom
  Again, danceability 86 / 100"), never every field of the row. A measure's name opens a card in the docs' own term format
  (figure, name, one line) whose figure is the method: its parts as bars of their weights, read from the code that computes
  it, titled in words for what it shows ("this set, song by song") (a DJ tool, 2026-10-27: "one big string of text is too much,
  opt for short, what is being hovered over"; then "love the hover metric blurbs!"; "i dont understand graphs? is this summary
  of this metric for this set?"). A key's explanation takes the same card: its symbol and name, one line, then short rows of value
  and meaning, never one long sentence (a DJ tool, 2026-10-27: "one long line hard to read, use symbol and brief text descriptors").
- **A hover gloss teaches**: one plain sentence, a small drawing when the idea is spatial (a curve through points, 3 of
  10 steps), and a link to the primary source (the paper, the docs, the code); it stays open while the pointer moves
  into it and opens on tap.
- **Hover cards: size the label column to the longest label** in `ch` (12 characters: 12.5ch), not a guessed `em`, and
  measure label right edge against bar left edge; a 4.6em column let "conversation" run into its bar.
- **Linked highlights**: hovering an item in one view lights the same item in the others (card and map dot). Position
  and order link too: a thing between two others sits where they meet (a transition as a node on the link where its
  two tracks' bars meet), and its hover lights the same stretch in every plot (a DJ tool, 2026-10-26: "position and order
  of elements should be connected better").
- **One number per item, the same on every view**: a take's number is its place in the order it was made, on its card and
  beside its mark on the map, for the items shown as cards only (a DJ tool, 2026-10-27: "rendered takes should be easier to see
  where each take is in cue map: larger? numbers?"; "cards have numbers, not letters? in order of creation"). An expanded view
  reads as a pop-up of what opened it: one edge shared by the source and the panel, and a tail from the panel to its source
  ("should show popping out of red check"). A preview shows the gist; the detail's marks (bands, swap lines, flag stretches)
  live in the expanded view or appear while their chip is hovered ("simplify take preview ... this is in expanded view only").

## 4. States and waits

- **A state has one code on every view**: one colour and one glyph per state, defined once as tokens (`--kept`, `--work`)
  and used by the path, the marks over the plot, the buttons, the cards, the map and the key alike; a state in progress
  gets its own glyph, faded and dotted rather than a colour already taken (a DJ tool, 2026-10-27: "pink - keep and blue = being
  worked on. use consistent color everywhere"; "third symbol for being rendered": a light-gray dotted ring that fills).
- **A toggle's icon is drawn, in the field's convention**: an inline SVG in `currentColor`, outline when off and filled
  when on (GitHub's and Gmail's star), rather than a text glyph, which can fall back to another font and read as a
  different symbol (a DJ tool, 2026-10-27: the row's ★ read as an asterisk; "star symbol should be star not astrisk").
- **One table per kind of thing, every state in it**: each row wears its state's mark and a key of the same marks sits above,
  each a pill that shows that state alone, with one table carrying every state rather than a second table for one (a DJ tool, 2026-10-27: the Recommended table
  folded into the tracks table, "one table for songs. show all classes. clearly label same dot and style as playlist").
  Every row is one height (one line per cell, an ellipsis, the whole on hover); the row's own control wears the mark (the
  play button in its class's colour, not a dot beside the title); a value several states share reads the same in each, its
  colour the only difference (a recommended place "#02" as the set's "#01", not "after 01": "row height should be consisten";
  "same consistent formatting for reccommended position").
- **Glow means live.** Only what is happening now glows: the take in the mix, a new take not heard yet (a slow soft
  gray pulse on its border); a state at rest keeps its edge and glyph, and a chosen item is the size of the rest, told by its
  outline and tag (a DJ tool, 2026-10-27: "careful not to overuse. ex. unselected render blue dont need glow"; "pulsing (soft)
  glow, not dot. dot can be confused with transition"; "kept transition ... not larger than other takes"). The glow takes the
  item's own state colour, never the chosen colour: a live item that is not chosen glowing in the chosen colour reads as chosen
  (a DJ tool, 2026-11-03: "in mix pink != keep pink"; the in-the-mix glow went from rose to slate, rose stayed the Keep's).
- **A given verdict can be taken back.** A pressed verdict button is a toggle: the second press (or its key) retracts it, the
  hover on the pressed button says so ("un-Keep  K"), the record keeps the retraction with the time and what it retracts, and
  the item returns to its to-review look everywhere at once; the button's own geometry and look do not change (a DJ tool,
  2026-11-03: "option to unselect keep, go from pink to open blue for transition again"; GitHub's star is the convention).
- **What is playing looks the same everywhere**: filled in the accent, a bar running along it, a second press pauses (a DJ tool,
  2026-10-27: "play version in the mix not clear. a play bar should be moving somewhere"). In a table the playing row is the
  player: its lower edge the bar (press to seek), its title cell the clock, no separate strip ("creative use of table"). The played fill is the position; a
  dot on the playhead repeats it ("current playfill pink sufficient, dont need pink dot above it").
- **Anything that waits shows that it is alive**: elapsed time and an estimate ("drawing 0:23, about a minute"), never a
  bare spinner. New work appears at once as grayed cards that fill as they load, and a wait that fails says so on its own
  card, with the reason and a retry (a DJ tool, 2026-10-27: "cards appear, grayed out, show load progress"; "spinning circles
  of doom with no progress indicator then failed"). Stop means now: a square that ends the running job too, not "stop after
  this one" ("use pause/stop symbol and behavior"). A queue takes any number of requests and bounds only what runs at once
  (the machine's slots), nearest to where the person is first; a press that finds nothing left draws afresh rather than refusing;
  and the queue's column ends in one control that empties it, waiting first, then the running ones on a second press that says
  how many it stops (a DJ tool, 2026-11-03: "allow infinite renders in que, ability to clear renders"; a second press on a queued
  transition had added nothing). Something generated (tags, takes) says why it was chosen, how many,
  and can be made again with a chosen count ("ability to change # of tags and re-generate"; "how many takes to render"); it is
  made again by itself when its inputs change, and its count defaults to the platform's own limit, held in one place (a DJ tool's
  tags after a song swap, 2026-11-03: "limit 30, default 30, copy and paste, auto re-generate as songs swapped").
  What is live (the take in the mix) carries its state's colour with a soft glow; the rest a thin gray edge, never a heavy white
  ("more prominent pink highlight with glow border ... the white is a little thick and strong"). A working view carries no
  build stamps ("dont show updated text").
- Cache-bust changed assets (`?v=...`) so open tabs show the change on reload.

## 5. What makes great apps great

Read [references/great-apps.md](references/great-apps.md) when building or reviewing an app people come back to: the
primary action, one affordance per kind, answers within 400 ms, the plain story first, fewer choices first, entry points at
the top, a stable frame, true phone layouts, momentum without tricks, a switch between versions, borrowing the
conventions people already know. Before a publish, run design-practice's page audit (first screen, states, touch
targets) and page-legibility-check at desktop and phone widths.

## Related

design-practice (composition, text, icons, colour, the page audit), interactive-figures (figures that respond),
figure-design (axes and keys), page-legibility-check (measure), field-vocabulary (labels), the person's style skill.

## Provenance

Split from design-practice on 2026-10-27 at 251 lines, by task: pages and slides stayed there, apps and interaction came
here ("Split design-practice by task: pages/slides vs apps/studios, keep one owner per guideline"). Cases from a DJ studio (2026-10-14 to 2026-10-27, from "hover to explain flags instead of drop down (more legible text, less
jumpy)" on), an art doc and an art piece (2026-10-26) and the 2026-10-24 studio design audit behind great-apps.md.
