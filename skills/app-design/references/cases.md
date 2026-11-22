# App design: the cases

The long form of each case in SKILL.md, grouped by the principle it shows, with the words it came from. SKILL.md keeps
the rule and a few words of each case; read this when a rule needs its full story, or when filing a new case
(capture-lesson §2: most new cases fold under one of these principles).

## P1. The first screen is the work, in the order it is used

- **Main actions first** (§1). a DJ tool, 2026-10-27: "make great first impression: play set, dive into transitions, see
  transition render progress".
- **Nested menus** (§1). Same day: "show user, set, version more clearly (nested drop down)".
- **Stack by importance** (§1). a DJ tool, 2026-10-27: "this is a transitions tool"; "tempo then vocals then metrics below
  set (most to least important)"; "organize columns roughly from most to least important, toggle columns on/off"; "use
  full page width".
- **A workspace shows the work** (§1). a DJ tool, 2026-10-26: "this should be covered in process not studio? studio is
  workspace". 2026-10-27, on the about page: "dont merge with studio, but use same style and concepts as studio,
  connect concepts and design principles".

## P2. The control invites the action; no sentence explains it

- **Whatever responds looks like it does** (§2). a DJ tool, 2026-10-26: "where to click to tunnel into transition?
  elements should be easily discoverable"; a quiet text line between rows was not found. 2026-10-27: "interactivity
  should be clear throughout studio: shaded button style, consider adding slight depth. applies to drop down arrows";
  tags "almost like buttons".
- **The marks themselves are the way in** (§2). a DJ tool, 2026-10-27: "transition legend why are these buttons?
  individual transition circle > see renders"; "2 kept 8 to review seems unnecessary, this is shown".
- **Let the real control show itself** (§2). an art doc, 2026-10-26: "touch the water → it follows ... telling, not
  showing", then "line and bubble icons not helpful". The 2 minutes of a loop became a dot that runs the ring in two
  real minutes, "2 min" written only at its centre.
- **Show rather than tell** (§2). a DJ tool, 2026-10-27: "press or drag to play from there: unnecessary text, please
  remove. interaction should be obvious from design".
- **A hover state promises a response** (§2). a compound explainer's property cards, 2026-11-20: "why is this a hover to
  highlight? unnecessary if not interactive". A matrix and a vial drawer had both control and target hovers;
  only the site pills kept one.

## P3. A control takes the shape of its job and sits on its object

- **Class honesty** (§2). an essay's Figure 1, 2026-11-19: a line-to-loop slider in an essay whose point is
  that closing is all or nothing. "line> loop is portrayed as continuous, should be discrete switch"; "class honesty.
  use discrete where discrete, continuous where continuous". A slider over a two-state choice claims states that do
  not exist, and a stepper over a real continuum hides them.
- **An action sits on its object** (§2). a DJ studio, 2026-11-06: "this is the export of the set ... maybe in the set
  space"; "some indication it's a guide should be a little bit more obvious ... top right ... a little sparkle button".
- **A live tool steers by choice** (§2). a DJ tool, 2026-10-27: "choice better than words? hands on UI/UX to make choices.
  hard to speak when DJ live!" Named choices: "ease B in", "ride the tempo up", "hit harder on the drop".
- **A label is its own control** (§2). a DJ tool's tracks table, 2026-10-27: "column toggle buttons redundant with column text
  labels"; "instead of put away, 'more' ... keep it positive".
- **One action for the selected row** (§2). a DJ tool's swap list, 2026-11-03: eight identical 'swap in' pills, "avoid
  having so many swap in buttons? consolidate design".

## P4. The frame holds still

- **Freeze the axis** (§1). a DJ studio, 2026-11-06: "I should always be able to orient myself in this x-axis space
  ... lock it at the top ... like how Excel will lock a row at the top".
- **A fold moves nothing above it** (§1). a DJ tool's checks fold, 2026-11-06: "when drop down checks, the position moves -
  please try to keep consistent".
- **One width, one shape through states** (§1). a DJ studio, 2026-11-16: "transition window should always be same
  width, renders in progress narrows window ... consistency in shapes important". Row cells: number, disc, name,
  buttons, a lane the picture's size, time.
- **One header across pages** (§1). a DJ studio's two pages, 2026-11-06: "weird jump when about is toggled".
- **Selection controls stay in place** (§2). a DJ tool's map gate, 2026-10-27: "default lasso always on, prevent jumping
  around"; the include/exclude row had appeared only on a selection.
- **State classes named apart** (Gotchas). a DJ tool: left-out rows were `tr.drop`, and the stylesheet's `.drop` (the
  file drop box) centred, padded and dashed them; 2026-11-16, a new row called `tk-new` wore the new-take flash's
  outline.

## P5. A hover answers one question, short

- **What is under the pointer** (§3). a DJ tool, 2026-10-27: "one big string of text is too much, opt for short, what is
  being hovered over".
- **A measure's card** (§3). Same day: "love the hover metric blurbs!"; then "i dont understand graphs? is this summary
  of this metric for this set?", which titled the figure in words. A key's card: "one long line hard to read, use
  symbol and brief text descriptors".
- **Label column in ch** (§3). A 4.6em column let "conversation" run into its bar; 12 characters became 12.5ch.

## P6. The system answers at once and never goes quiet

- **Anything that waits shows it is alive** (§4, Gotchas). a DJ tool, 2026-10-27: 4 to 7 s of empty skeletons; "spinning
  circles of doom with no progress indicator then failed"; "cards appear, grayed out, show load progress".
- **Glow means live** (§4). a DJ tool, 2026-10-27: "careful not to overuse. ex. unselected render blue dont need glow";
  "pulsing (soft) glow, not dot. dot can be confused with transition"; "kept transition ... not larger than other
  takes"; "more prominent pink highlight with glow border ... the white is a little thick and strong". 2026-11-03: "in
  mix pink != keep pink"; the in-the-mix glow went from rose to slate, and rose stayed the Keep's.
- **What is playing** (§4). a DJ tool, 2026-10-27: "play version in the mix not clear. a play bar should be moving
  somewhere"; the table row as player, "creative use of table"; "current playfill pink sufficient, dont need pink dot
  above it".

## P7. The person keeps control

- **What the person asked for stays in view** (§2, Gotchas). a DJ tool: the full-track take the person asked for was
  folded away for departing from a guideline, and they asked to see it.
- **A verdict can be taken back** (§4). a DJ tool, 2026-11-03: "option to unselect keep, go from pink to open blue for
  transition again".
- **Stop means now; a queue takes any number** (§4). a DJ tool, 2026-10-27: "use pause/stop symbol and behavior", in
  place of "stop after this one". 2026-11-03: "allow infinite renders in que, ability to clear renders"; a second press
  on a queued transition had added nothing.
- **Something generated can be made again** (§4). a DJ tool, 2026-10-27: "ability to change # of tags and re-generate";
  "how many takes to render". Tags after a song swap, 2026-11-03: "limit 30, default 30, copy and paste, auto
  re-generate as songs swapped".

## P8. Borrow the conventions people already know

- **A toggle's icon is drawn** (§4). a DJ tool, 2026-10-27: the row's ★ fell back to another font and read as an
  asterisk, "star symbol should be star not astrisk".
- **An action is its symbol** (§2). Copy to clipboard and export to SoundCloud looked alike and stayed two buttons, the
  export wearing the service's mark.

## design-practice principles, applied to apps

- **Controls in one group are siblings** (P2 there; §2). a DJ tool, 2026-10-27: "why set has shade region not other two?";
  "why two buttons classes? ... each unique"; an ordered class became one gradient dot, not three dots and "1 to 13".
- **A control with nothing to choose goes** (P1 there; §2). A versions menu holding one version: "no user interaction,
  element not necessary".
- **An interaction's note beside it** (P5 there; §2). an art doc, 2026-10-26: the handle's note next to the handle, the
  water's note under the live water, rather than in a strip below; an icon at the start of each headline line beat a
  detached key row ("this is a little unclear").
- **Two controls, two names** (P2 there; §2). The faucet handle (the power symbol, rests the GPU while held) and the
  wall's power strip (turns the piece off): "behavior of switch on wall vs sink?".
- **Linked highlights, position and order** (P5 there; §3). a DJ tool, 2026-10-26: "position and order of elements should
  be connected better".
- **One number per item** (P2 there; §3). a DJ tool, 2026-10-27: "rendered takes should be easier to see where each take
  is in cue map: larger? numbers?"; "cards have numbers, not letters? in order of creation".
- **A pop-up of what opened it** (P5 there; §3). Same day: "should show popping out of red check"; "simplify take
  preview ... this is in expanded view only".
- **One code per state** (P2 there; §4). a DJ tool, 2026-10-27: "pink - keep and blue = being worked on. use consistent
  color everywhere"; "third symbol for being rendered": a light-gray dotted ring that fills.
- **The mark alone says a row's state** (P2 there; §4). "excluded songs should always be left-aligned, no
  strikthrough".
- **One table per kind** (P2 there; §4). a DJ tool, 2026-10-27: the Recommended table folded into the tracks table, "one
  table for songs. show all classes. clearly label same dot and style as playlist"; "row height should be consisten";
  "same consistent formatting for reccommended position" (a recommended place "#02" as the set's "#01", not "after
  01").
- **No build stamps** (P1 there; §4). "dont show updated text".
