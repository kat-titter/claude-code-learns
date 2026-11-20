# Tufte's definitions, with sources

The terms SKILL.md uses, as the sources retrieved on 2026-11-05 state them. The books themselves were not read; page
numbers are as the summaries cite them (VDQI: The Visual Display of Quantitative Information, 1983, 2nd ed. 2001; EI:
Envisioning Information, 1990; BE: Beautiful Evidence, 2006).

## Graphical excellence (VDQI)

"Gives the viewer the greatest number of ideas, in the shortest time, with the least ink, the smallest space", and tells
the truth about the data (InfoVis:Wiki, Graphical Excellence). The first principle: "Above all else show the data"
(Tufte's own notebook on sparklines, 2016).

## Graphical integrity and the lie factor (VDQI pp. 57-69)

- Principle: "The representation of numbers, as physically measured on the surface of the graphic itself, should be
  directly proportional to the quantities represented."
- Lie factor = (size of effect shown in the graphic) / (size of effect in the data), where the size of an effect is
  |second value − first value| / first value. Honest drawing sits between 0.95 and 1.05; above 1 overstates, below 1
  understates (InfoVis:Wiki, Lie Factor; Wikipedia, Misleading graph; Friendly's Gallery).
- Cases: the New York Times fuel-economy chart, 18 to 27.5 mpg (+53%) drawn as +783%, lie factor 14.8 (p. 57); area
  used for one-dimensional data, lie factor 2.8 (p. 69); the "shrinking family doctor" (p. 69), where the square-cube
  law multiplies a linear change; ten-year periods compared with one five-year period (p. 60); Washington Post doctors'
  incomes with unevenly spaced years (Wainer 1997, via Friendly).
- Design variation must not be confounded with data variation: changes in the scale of the graphic correspond only to
  changes in the data (Friendly, summarizing VDQI).
- Four questions (Gales's outline): does the display tell the truth; is the representation accurate; are the data
  documented; are appropriate comparisons, contrasts and contexts shown.

## Data-ink and the data-ink ratio (VDQI)

- "A large share of ink on a graphic should present data-information, the ink changing as the data change. Data-ink is
  the non-erasable core of a graphic, the non-redundant ink arranged in response to variation in the numbers
  represented" (InfoVis:Wiki, quoting Tufte 1983).
- Data-ink ratio = ink used to display the data / total ink used to display the graphic (Wikipedia, Misleading graph);
  the goal is a ratio as close to 1.0 as possible "without eliminating something that is necessary for effective
  communication" (InfoVis:Wiki). Sparklines have a data-ink ratio of 1.0 (Tufte's notebook, 2016).
- Criticism recorded on the same page: Inbar, Tractinsky and Meyer (2007) found 87 students preferred the fuller of
  Tufte's two bar charts; removing the top border removed an implied 20% line.
- Moves (Gales): light or no grids; white space as grid lines across bars; ticks at the data values; range frames
  (axes drawn over the span of the data); replace bars with lines where one line carries the value; scale information
  present but muted; the data, not the data containers.

## Chartjunk (VDQI pp. 106-121; EI pp. 52-65)

- "The interior decoration of graphics generates a lot of ink that does not tell the viewer anything new. The purpose
  of decoration varies — to make the graphic appear more scientific and precise, to enliven the display, to give the
  designer an opportunity to exercise artistic skills. Regardless of its cause, it is all non-data-ink or redundant
  data-ink, and it is often chartjunk" (Wikipedia, Chartjunk, quoting VDQI).
- "Sometimes decoration can help editorialize about the substance of the graphic. But it is wrong to distort the data
  measures — the ink locating values of numbers — in order to make an editorial comment or fit a decorative scheme"
  (VDQI 2001, p. 59, via Wikipedia).
- On Nigel Holmes's Diamonds chart: "chockablock with cliché and stereotype, coarse humor, and a content-empty third
  dimension ... who would trust a chart that looks like a video game?" (EI, via Wikipedia). Holmes's reply (NYT, 1992):
  Tufte "remains trapped in the world of academia".
- Kinds (Wikipedia): heavy or dark grid lines, unnecessary text, gimmicky typefaces, ornamented axes, frames, pictures,
  backgrounds or icons inside the data area, ornamental shading, unnecessary dimensions; and the kind that skews the
  data: items out of scale, noisy backgrounds, 3-D line and bar charts.
- The debate: Few, "The Chartjunk Debate" (too loose a definition); Kosara, three kinds of chart junk (2012); Bateman
  et al., "Useful junk?" (CHI 2010: embellished charts remembered better); Wu et al. (CHI 2021: meaningful icons
  improved accessibility for readers with intellectual and developmental disabilities); Parsons and Shukla (VIS 2020:
  practitioners disagree on the definition).

## Layering and separation, micro/macro, small multiples (EI)

- The book's topics, from its publisher's page: escaping flatland, color and information, micro/macro designs, layering
  and separation, small multiples, narratives of space and time.
- 1 + 1 = 3 (or more): two elements in close proximity produce a visible interaction, moiré and optical vibration, which
  fatigues and can show information that is not there (EI p. 60, via Gales).
- Smallest effective difference: make every mark as small and light as it can be and still be clear (Garcia, Gales).
- Micro/macro readings: data-rich displays where every point has a value up close and only trends and patterns show
  from afar, presented within one eyespan at the resolution of print (Wikipedia, Edward Tufte); the Consumer Reports
  grid of car defects (VDQI p. 174, via Gales); the Vietnam Veterans Memorial's names in chronological order (EI
  pp. 43-44, via Wikipedia).
- Small multiples: "At the heart of quantitative reasoning is a single question: Compared to what? Small multiple
  designs, multivariate and data bountiful, answer directly by visually enforcing comparisons of changes, of the
  differences among objects, of the scope of alternatives. For a wide range of problems in data presentation, small
  multiples are the best design solution" (EI p. 67, via Wikipedia). "Illustrations of postage-stamp size are indexed
  by category or a label, sequenced over time like the frames of a movie, or ordered by a quantitative variable not
  used in the single image itself" (EI, via InfoVis:Wiki). Same measures and scale in every panel. Griffin et al.
  (2006): animation better for seeing movement, small multiples better for comparing times.
- Colour (Gales): muted grids as a layer; pure bright colours for small highlights, almost never backgrounds; colour
  spots on light grey; fine contour lines delimit subtle shades (EI p. 94); context shifts colour (EI pp. 92-93); 5 to
  10% of readers are colour-blind to some degree.
- Data density = number of entries in the data matrix / area of the graphic (Gales); the eye resolves 0.1 mm, about
  60,000 distinctions per square inch (Bickmore, via Tufte's sparkline thread).

## Sparklines (BE pp. 46-63; edwardtufte.com, 2004 thread and 2016 notebook)

- "A sparkline is a small intense, simple, word-sized graphic with typographic resolution"; "datawords: data-intense,
  design-simple, word-sized graphics"; the term introduced in 2006, the form documented in VDQI (1983, pp. 133-135) as
  "intense continuous time-series".
- Three driving principles: maximize data density, minimize or zero out non-data, and the shrink principle ("graphics
  can be shrunk way down"): draw large, reduce three to five times.
- The glucose example: a number, then the last 80 readings as a line, the normal range as a grey band, the most recent
  value tied to the printed number by a colour accent; a stack of such lines compares hundreds of variables.
- Aspect ratio: "statistical graphics should be moderately greater in length than in height"; Cleveland's rule, slopes
  averaging 45° over every cycle, gives a lumpy rather than spiky or flat profile; use the maximum reasonable vertical
  space under the word-like constraint, then adjust the horizontal stretch. Financial sparklines about 5:1, a season
  20:1, DNA about 300:1.
- Clutter: moiré is worst when data lines and the spaces between them are about equal and contrast strongly; mute the
  contrast and change the line weight; strong frames make the negative space between them the dominant element; the
  test is "Do the prominent visual effects convey relevant content?"; "the physical location of the numbers, words, and
  graphics enforces the implicit grid; that grid never needs to be expressed directly."
- "Approximately right rather than exactly wrong" (Tukey, 1965); the sparkline table showed about 5,000 more numbers in
  21% more data area than the New York Times mutual-fund table; sparklines "improve the attention span of tables" and
  reduce recency bias. Outliers: a log scale, a broken scale, or a table. One colour or flat colour in print.
- The Apple Watch sparkline (2014): "should show more detail, more data texture. Should have design minimization, not
  data minimization." General idea: max[data], min[design].

## The Cognitive Style of PowerPoint (2003)

A NASA slide reproduced in the Columbia Accident Investigation Board's report: an engineering detail in small type on a
crowded slide with six bullet points, which in a regular engineering white paper might have been noticed (Wikipedia,
Edward Tufte).
