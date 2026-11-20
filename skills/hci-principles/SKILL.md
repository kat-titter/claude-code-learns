---
name: hci-principles
description: Applies the HCI classics to any screen, page or tool - design space analysis in QOC (questions, options, criteria), Nielsen's heuristics, Shneiderman's golden rules, Norman's affordances and signifiers - so a design is judged against the designs it could have been. Use when choosing between designs, writing a design rationale or reviewing a UI.
when_to_use: On "why did we choose this?", "what were the alternatives?", "design rationale", "QOC", "usability heuristics", "affordance" or "is this usable?".
---

# HCI principles

You understand a design best by comparing it with the designs it could have been. Most design documents record what
was decided and never why. Design Space Analysis draws the map around an artifact: the choices that had to be made, the
alternatives at each, and the reasons for preferring one; its notation is QOC, Questions, Options and Criteria, and it
works with pencil and paper (MacLean, Young, Bellotti and Moran, 1991). In the order the work runs: open the space with
questions (§1), fill it with options (§2), judge with criteria (§3), record and reuse the rationale (§4), take the canon
as ready-made criteria (§5), and let it show in the work (§6). The full lists with sources are in
[references/canon.md](references/canon.md).

## Gotchas

- **A doc with the what and no why cannot tell a rejected option from an unconsidered one.** When a better design turns
  up later, the rationale says whether it was weighed and lost or never seen (UCT design-rationale notes); without it
  the team argues from zero again.
- **A criterion worded as a feature is an option in disguise.** "Has a wide scroll bar" judges nothing; "ease of hitting
  with a mouse" does, and more of it is always good, so every option can be scored against it.
- **A question that judges closes the space.** "Should we use the obviously better narrow bar?" has one answer; "How
  wide should the scroll bar be?" has several. Questions open, criteria judge.
- **Rationale written after the decision is advocacy.** QOC is a co-product of designing (the paper's own test of a
  good notation): draw it while the choice is open, and the losing options stay on the page.
- **The built design is one option, not the root of the tree.** Hang it beside the alternatives under the question it
  answers, or the analysis only ever confirms what exists.

## 1. Questions open the space

- **A question is a key issue phrased so it splits the design into choices**: "How wide should the scroll bar be?", "How
  does the user know where they are in the menus?" A good question has two or more live options; one with a single
  answer is a decision already made, so record it as one.
- **Find questions by asking "what else could this have been?" of each visible decision**: every control, layout,
  default, wording and omission on a screen answers a question somebody could have answered differently.
- **Consequent questions hang off an option**: "if narrow: how is it found?" A screen's space is a tree of a dozen
  questions, not a list of hundreds.

## 2. Options fill it

- **An option is one possible answer, named as a noun phrase**: wide, narrow; flatten menus to depth three, show the
  path as text, stack the menus visibly (the UCT phone-menu example).
- **Always add the three alternatives the room forgot**: the contrary of what was built (wide against narrow), the
  field's convention (what the leading apps do; Jakob's law in app-design), and the null option (no scroll bar: drag to
  scroll). The analysis is only as good as the options it compares.
- **Rejected options stay on the page**, with the criterion that sank them; they are the memory of the design.

## 3. Criteria judge

- **A criterion is a reason to prefer one option over another, worded so that more of it is good**: ease of hitting
  with a mouse, screen space left for content, accuracy of the user's sense of place, learnability for a novice.
- **An assessment is a line from an option to a criterion, solid for supports and dashed for challenges**: a sign, not
  a weight; QOC is argument, not arithmetic. Flatten-to-three supports "sense of place" and challenges "number of
  functions"; path-as-text supports both and costs screen space. The trade-off is visible when an option's lines go
  both ways.
- **The same criterion scores every option under its question**; a criterion that touches one option is a feature of
  that option, so reword it or drop it.
- **General criteria sit behind specific ones**: "ease of hitting with a mouse" serves "speed for the experienced
  user", which serves "efficiency". Name the chain once so a new specific criterion finds its parent.

## 4. Record and reuse

- **The rationale lives beside the design**, as a QOC block in the design doc, README or page: the question as a
  heading, one row per option with the built one marked, one column per criterion holding + or −. A diagram is three
  columns with lines; a table is the same thing in text. (A guideline in this library is a QOC line: what to do, the
  example, the reason; capture-lesson §4.)
- **Same context, same rationale; changed context, re-score.** A later design in the same setting reuses the analysis
  as is; a new setting (phone, novice, touch) keeps the questions and options and re-draws the lines.
- **After shipping, the criteria are predictions to check**: did the option chosen for "ease of hitting" get hit? A
  criterion that predicted wrong is the lesson, and goes to the matching skill.

## 5. The canon as ready-made criteria

The classics are lists of criteria somebody already worded so that more is good; take them off the shelf when scoring
options. Full lists and sources: [references/canon.md](references/canon.md).
- **Nielsen's ten heuristics** (1994, reviewed 2024): visibility of system status; match between the system and the real
  world; user control and freedom; consistency and standards; error prevention; recognition rather than recall;
  flexibility and efficiency of use; aesthetic and minimalist design; help users recognize, diagnose and recover from
  errors; help and documentation.
- **Shneiderman's eight golden rules** (sixth edition, 2016): strive for consistency; seek universal usability; offer
  informative feedback; design dialogs to yield closure; prevent errors; permit easy reversal of actions; keep users in
  control; reduce short-term memory load.
- **Norman's vocabulary** (The Design of Everyday Things): an affordance is what the thing can do (a door can be pushed
  or pulled); a signifier tells you which (a flat plate says push, a bar says pull); the gulf of execution is the
  distance between what the person wants and the sequence the thing demands, the gulf of evaluation the distance
  between the thing's state and what the person can see of it. A design closes both gulfs.
- **The laws of sizes and counts** (Fitts, Hick, Doherty, Gestalt, Jakob) are applied with their cases in
  app-design/references/great-apps.md; cite them there rather than here.

## 6. Where it shows

- **In a design review, each finding names the criterion it scores and the option it prefers**: "cluttered" becomes
  "challenges aesthetic and minimalist design: the badge grid competes with the six flags" (app-design's quiet tick).
- **In a design doc or essay, the decisive question gets its QOC table**, not every question; the reader sees the
  space around the one choice that mattered.
- **In an app, the choices the user makes are a design space too**: a studio's takes are options, the verdict buttons
  are assessments, and the person's taste is the criteria column; show the criteria and the choices read as reasons
  instead of preferences.

## Provenance

2026-11-05: "add to skills: HCI greats design principles", with a page on Design Space Analysis (the scroll bar example:
Q how wide, O wide or narrow, C ease of hitting with a mouse). Sources retrieved that day: the QOC paper's summary
(AcaWiki), UCT's design-rationale notes (the phone-menu example), Nielsen Norman Group's ten heuristics, Shneiderman's
eight golden rules (cs.umd.edu), Wikipedia on The Design of Everyday Things.
