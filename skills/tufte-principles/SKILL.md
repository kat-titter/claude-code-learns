---
name: tufte-principles
description: Applies Edward Tufte's principles for showing data - show the data above all, maximize the data-ink ratio and erase chartjunk, keep the lie factor near 1, layer and separate (1 + 1 = 3), build small multiples, micro/macro readings in one eyespan, sparklines in text and tables. Use when editing or reviewing a chart, or when someone says "chartjunk", "data ink", "lie factor", "small multiples", "sparkline" or "Tufte".
when_to_use: After the figure-design defaults, before publishing; when a chart's ink is mostly frame, grid and fill. Axes and legends go to figure-design, colour to the house-style skill.
---

# Tufte's principles

"Above all else show the data." Edward Tufte's The Visual Display of Quantitative Information (1983) and Envisioning
Information (1990) are the canon for statistical graphics: graphical excellence "gives the viewer the greatest number of
ideas, in the shortest time, with the least ink, the smallest space", and tells the truth about the data. figure-design
holds the defaults a figure starts from; this skill holds Tufte's editing passes, in the order the work runs: name the
comparison (§1), draw it truthfully (§2), erase (§3), layer and separate (§4), multiply and shrink (§5), and put the
words on the data (§6). Definitions, formulas and sources are in [references/canon.md](references/canon.md).

## Gotchas

- **A 53% rise drawn as a 783% rise.** The New York Times fuel-economy chart (Tufte 1983, p. 57) had a lie factor of
  14.8. Fix: the length of each mark proportional to its number, and the ratio checked before publishing (§2).
- **Area or volume for a one-dimensional number.** A doubled quantity drawn as a doubled width is a quadrupled area
  (the "shrinking family doctor", p. 69, lie factor 2.8). Fix: length for a quantity, or the scaling stated.
- **Rubber-band time axes.** A Washington Post chart of doctors' incomes spaced its early years far apart and its late
  years a year apart, so exponential growth read as linear; redrawn to scale it showed two slopes around Medicare
  (Wainer 1997, via Friendly). Fix: equal pixels per unit of time, every time.
- **Erasing past the data.** Tufte's own minimalist bar chart lost the implied 20% line when its top border went, and
  readers preferred the fuller chart (Inbar 2007). Fix: erase the ink that decorates and keep the ink that quantifies,
  a tick, a scale, a baseline (§3).
- **"Chartjunk" used as a verdict.** Few found the term too loose; Kosara sorts it into harmful (busy backgrounds),
  harmless (borders) and helpful (annotations); embellishment helps recall (Bateman 2010) and meaningful icons helped
  readers with intellectual disabilities (Wu 2021). Fix: judge each mark by whether it competes with reading the data
  or carries meaning for the reader at hand.
- **Moiré.** Closely spaced lines vibrate, worst when line and gap are about equal and contrast strongly. Fix: thinner
  data lines and a muted contrast between data and background (Tufte's before-and-after sparklines).
- **Heavy frames.** Around a grid of small charts the dominant visual element becomes the stripes of negative space
  between the frames. Fix: let the position of the numbers and graphics imply the grid; frames whisper or go.
- **Design minimization mistaken for data minimization.** The 2014 Apple Watch sparkline was smoothed to a curve and
  lost the data's texture. Fix: minimize the design, keep the data: max[data], min[design].
- **The deciding number buried on a slide.** The Columbia accident board reproduced a NASA slide where the engineering
  detail that mattered sat in small type under six bullets. Fix: the number that decides goes in a sentence or a table,
  at body size, on a page the room can read.

## 1. Compared to what?

- **Name the comparison before drawing.** "At the heart of quantitative reasoning is a single question: Compared to
  what?" (Envisioning Information, p. 67). A figure enforces a comparison: changes, differences among objects, the
  scope of alternatives. A raise of $1000 means nothing until it stands beside last year's, the past raises and the
  company's (Tufte's course, 1994).
- **A few numbers go in a sentence or a table.** "Tables are preferable to graphics for many small data sets", and a
  table "is nearly always better than a dumb pie chart", since pies fail to order numbers along a visual dimension
  (1983, p. 178). A share of a whole with two or three parts may be a pie; past that, a sorted bar or the table.
- **Density is the figure's asset.** Data density is the entries in the data matrix per area of the graphic; the eye
  resolves 0.1 mm, so a page can carry tens of thousands of distinctions. Graphics are at their best with dense,
  multivariate, comparative data; "to clarify, add detail". Minard's march to Moscow carries six variables in two
  dimensions.
- **Low density forces sequence.** A screen or slide that shows a little at a time makes the reader hold comparisons in
  memory; adjacent in space beats stacked in time (§5).

## 2. Draw it truthfully

- **Marks proportional to numbers.** "The representation of numbers, as physically measured on the surface of the
  graphic itself, should be directly proportional to the quantities represented." The lie factor is the size of the
  effect shown in the graphic over the size of the effect in the data; 0.95 to 1.05 is honest drawing, above 1
  overstates, below 1 understates (1983, pp. 57-69).
- **Design variation never stands for data variation.** One scale per axis, held along its whole length; a cycle shown
  whole; equal periods compared with equal periods (ten-year bins beside a five-year bin exaggerated the last one,
  p. 60); money in constant dollars, counts per population.
- **Every mark quantified.** A line with no scale is dequantified; at least one point is tied to a printed number, and
  the normal range or reference is drawn, so the reader can read values as well as shape.
- **Document on the graphic**: the source, n, the data's limits and the exceptions, and labels on the events in the
  data; a reader should be able to check the figure without the text (controlled-comparisons holds the scientific
  side).
- **Four questions before publishing**: does the display tell the truth; is the representation accurate; are the data
  documented; are the right comparisons, contrasts and contexts shown.

## 3. Erase

- **Data-ink is "the non-erasable core of a graphic, the non-redundant ink arranged in response to variation in the
  numbers represented."** The data-ink ratio is data ink over total ink; raise it toward 1 without removing anything
  the reading needs. Sparklines sit at 1.0: no frame, no ticks, context from the words and numbers beside them.
- **Two erasing passes, then revise.** First erase non-data ink: frames, backgrounds, heavy grids, shadows, a third
  dimension that carries no data, ornament on the axes. Then erase redundant data ink: the two sides and top of a bar
  that one line can carry, a value printed and plotted and gridded. Then edit again.
- **Chartjunk is the ink that tells the viewer nothing new.** "The interior decoration of graphics generates a lot of
  ink that does not tell the viewer anything new ... it is all non-data-ink or redundant data-ink, and it is often
  chartjunk." Of Holmes's 3-D Diamonds chart: "who would trust a chart that looks like a video game?" Tufte allows
  that "decoration can help editorialize about the substance", and draws the line at distorting the data measures.
- **The quiet moves**: white space instead of grid lines across bars; ticks placed at the actual data values; a range
  frame, the axis drawn only over the span of the data; scale information present but muted; solids or greys instead
  of crosshatching; the data, not the data containers, carrying the weight.

## 4. Layer and separate

- **1 + 1 = 3.** Two marks close together make a third visual element, the gap or vibration between them; it fatigues
  and shows "data that is not there" (Envisioning Information, p. 60). Separate the layers by weight and value so each
  reads alone: data forward, structure back.
- **Smallest effective difference.** Make every distinction as light as it can be and still be read: thin grey for
  guides, the thinnest rule that separates, a tint rather than a hue for a region. The data then stands forward
  without being louder.
- **Colour as a layer, quiet underneath.** Muted grids and bands give context; pure bright colour is kept for small
  highlights and almost never for backgrounds; colour spots read well on light grey; subtle shades are delimited by
  fine contour lines; surrounding colour shifts a colour's reading, and 5 to 10% of readers see colour differently.
  The house-style skill picks the palette; figure-design keeps one meaning per colour.
- **Test the clutter.** "Do the prominent visual effects convey relevant content?" If the loudest thing in the figure is
  a frame, a background or the space between lines, the design is at fault: clutter and confusion are failures of
  design, not properties of the information.
- **Wider than tall, banked to 45°.** Statistical graphics run moderately longer than high; for time series the aspect
  ratio that averages the slopes to 45° (Cleveland) gives a lumpy profile where rise and decay can be read, where a
  spiky or flat one hides them (the sunspot cycles rise fast and decay slowly only in the lumpy drawing).

## 5. Multiply and shrink

- **Small multiples answer "compared to what?" directly.** "Illustrations of postage-stamp size are indexed by category
  or a label, sequenced over time like the frames of a movie, or ordered by a quantitative variable not used in the
  single image itself" (Envisioning Information). The same measures, scale and axes in every panel; once the eye has
  learned one, all the others are read at a glance. Panels side by side beat flipping pages ("one damned thing after
  another") and beat animation for comparing times (Griffin 2006).
- **Micro and macro in one eyespan.** Up close every mark has a value; stepping back, the pattern shows. Consumer
  Reports' grid of car faults: the mass of black ink names the troubled cars at a glance, each cell a specific fault
  (1983, p. 174); the Vietnam memorial's names in date order carry the war's shape, where alphabetical order would not.
- **A sparkline is "a small, intense, simple, word-sized graphic with typographic resolution"**: a glucose reading
  becomes a number beside the last 80 readings, the normal range as a grey band, the latest point tied to the number by
  one colour; a stack of them compares hundreds of variables in parallel. "Approximately right rather than exactly
  wrong" (Tukey): the sparkline table beside a mutual-fund list showed 5,000 more numbers in 21% more area. Sparklines
  "improve the attention span of tables" by setting the recent change against a year of changes.
- **Shrink from large.** Draw the graphic at full size and shrink it three to five times to fit a sentence or a cell
  (the shrink principle); keep the maximum vertical space the word-like shape allows, then stretch time until the
  profile is lumpy (§4); 5:1 for a year of prices, 20:1 for a season. One colour, or two flat colours, so thin lines
  stay clean; an outlier gets a log scale or a table.
- **The idea in one line**: max[data], min[design].

## 6. Words on the data

- **Label the data where it sits.** Names attached to the parts, small messages next to the data, the note on the
  graphic itself; a line is tagged at its end where it has room (figure-design §2 keeps the end tags right-aligned and
  clear of each other). A key below carries what a label cannot: many marks, shaded regions, a mark's meaning.
- **Words, numbers and pictures in close proximity**, horizontal text, few abbreviations, the explanation beside the
  mark rather than in a caption two inches away; the typeface and sizes come from the house-style skill.
- **A technical argument lives in sentences and tables.** A bullet hierarchy at six words a line thins the evidence and
  hides the number that decides (The Cognitive Style of PowerPoint, 2003); a page of prose with the table in it is the
  form for a decision.

## Provenance

Sources retrieved 2026-11-05: edwardtufte.com's pages for The Visual Display of Quantitative Information (1983, second
edition 2001) and Envisioning Information (1990), its "Sparkline theory and practice" thread (2004, excerpting Beautiful
Evidence pp. 46-63) and "Sparklines history" notebook (2016); Wikipedia on Edward Tufte, Chartjunk, Sparkline, Small
multiple and Misleading graph; InfoVis:Wiki on Data-Ink Ratio, Lie Factor, Small Multiples and Graphical Excellence;
Michael Friendly's Gallery of Data Visualization (The Lie Factor); Larry Gales's outline of Tufte's principles
(University of Washington, 2005) and Dan Garcia's notes on Tufte's course (Berkeley, 1994). The books were not read;
page numbers are as those summaries cite them. 2026-11-05, the person chose "Tufte + Ousterhout" from a list of taste bibles.
