# Numbers on cards and chips

Read when a page shows numbers on cards, chips or dashboards. Moved from SKILL.md, 2026-10-26.

- **Every number on a card or chip says its direction** (a score, a cost, a rank): its direction, its best value, and what it
  can be compared with, in the label or the hover ("fit -0.84, higher is better, 0 = matches your kept transitions;
  compare within this transition"). A bare "score -0.86" left a reader asking "lower is better?" (a DJ studio, 2026-10-20).
  Say what the better direction buys, not only which way it is ("lower: a screen sees smaller drug effects, a model learns
  cells, not labs"; a pitch deck, 06, 2026-10-26: "why less error better? implications for ML models, drug screens").
- **Show a model's raw score as a rank** among the real alternatives ("rank 4 of 3,069", 1 = best), with the raw value
  and its meaning on hover: a rank reads at a glance and compares across items; a raw score needs its scale explained.
  A rank can also expose a label that oversells (a "top pick" chosen by a rule ranked 4,481 of 4,606 on the score).

- **Stat tiles over sentence columns.** Beside a figure, a strip of two or three tiles (big number, a label, one line
  under it: "107 of 125 / batches agree more on the map / by chance: about 62") reads faster than the same facts as
  sentences, and a reader's extra decimals become one more tile in the PDF layer. (a pitch deck, 05b and 06a, in a drug-mechanism deck's shape,
  25 Oct 2026.) Sibling tiles share their rows: lay the strip out as a grid whose cards take
  `grid-template-rows: subgrid` (icon, who, claim, number, line, source), so every number sits on one baseline whatever
  wraps above or below it; stacked cards top-align so the number keeps one offset in each. Pushing the number down with
  `margin-top:auto` lets it ride with its caption (a pitch deck, 05a, 2026-10-26: "green numbers should be same pos vertical";
  21% sat above 86% and 2.2x because its caption wrapped once more).

- **A big claimed number shows its arithmetic.** "Functionally infinite" or "1.3 M" becomes the factors stacked as a
  sum, each with what it counts, the product, and what it means in time ("431 subject sets x 6 orders x 28 moods x 18
  lights = 1,303,344 prompts; x 2 min a dream = about 5 years"), with the rule that makes the factors (a generative
  piece's prompt grammar, 2026-10-26: "more specific how it's generated, math calculate total # of combinations, how
  long it could run"). An estimate shows its derivation where it stands, the assumption and a second route to it
  ("$150k: a site licence, or 4 cell lines x $10k a quarter (A22)" under a revenue chart; a pitch deck, 07, 2026-10-26:
  "always explain where core key numbers like est revenue per institution come from").

Figures (axes, keys, channels, spacing, diagrams) follow figure-design.
