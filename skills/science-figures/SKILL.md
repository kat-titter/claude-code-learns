---
name: science-figures
description: Draws the science itself in a figure - molecules and chemical structures, proteins and cells, micrographs, assay plots and mechanism-of-action diagrams - at one level of abstraction, with real icons, a hue per class rather than per instance, and a claim a specialist would accept. Use when a figure must show machinery rather than boxes, or when a scientific figure reads as a cartoon or a toy.
when_to_use: Before drawing a figure whose subject is a molecule, a cell or an experiment; before a micrograph panel or strip plot is published; when a mechanism is becoming a chain of boxes.
---

# Science figures

A scientific figure shows the thing, not a picture of the idea of the thing. These guidelines run in the order a
figure is built: the molecule (§1), the biology around it (§2), the colours that code them (§3), the mechanism that
joins them (§4), and what the experiment saw (§5). Axes, keys, spacing and flow diagrams are figure-design; a fair
comparison, its controls and its scale bars are controlled-comparisons; a whole mechanism page is moa-explainer.

## Gotchas

- A mechanism of action drawn as a chain of labelled boxes (Gαs → adenylyl cyclase → cAMP as rectangles): draw the machinery's shape and the drug's structure where it acts (§4).
- An organ, body part or instrument drawn by hand when an open icon exists: take it from Health Icons (CC0), Bioicons or Servier Medical Art, note the source and licence, and draw only what no set has (§2; a peptide explainer, figure 13, 2026-11-05: "prefer to find
  pre-existing svg instead of making own"). Molecular machinery too: enzymes, receptors in a
  bilayer, antibodies from Bioicons or Servier, the drug as its real structure; circles and boxes read as a diagram, not
  biology (a peptide explainer, Figure 2, 2026-11-06: "symbols more 'real' science and biology vs. simple geometric shapes,
  biorender style, use existing assets").
- A hue spent on each instance when the category is what the reader needs (four compounds, four colours): a hue
  codes a class (§3).
- A figure caption that passes a verdict rather than stating the mechanism: say what the thing does, in one
  sentence a specialist would accept (§4).
- A micrograph panel with a bare "Masks" column, a scale bar with no unit, or bold text outside the panel letters:
  the published layout answers all three (§5).

## 1. Molecules and structures

- **A glyph that stands for a thing carries that glyph where the thing is drawn in full.** A molecule drawn as a
  coloured hexagon in a mechanism figure and as a skeletal structure a screen earlier are two pictures a reader does
  not join by themselves: put the figure's own glyph, same shape and colour, in a strip directly above the full
  drawing ("the rose hexagon in Figure 3 is this molecule"), and give both the same `data-k` inside one linked block
  so pointing at either lights the other. The words alone do not do it; the mark has to appear twice (a peptide explainer,
  2026-11-05: "nothing connecting chem structure to pink hexagon, not clear theyre the sae hting").
- **A thing's identity travels with its symbol.** Formula, full name, structure and provenance sit beside the glyph
  they describe, not in a column across the figure; what belongs together is read together. Where the detail is too
  big for that spot, the glyph itself becomes the control that opens it as a card, so the reader never has to find
  the link to the mark (a peptide explainer, 2026-11-05: "this should be close to the symbol for the molecule. try to keep
  similar info together. show chem structure with formula. maybe as a pop up window"). The card opens clear of the
  glyph and its link: drawn over the mark just clicked, it hides the anchor it belongs to (same page, 2026-11-05).
- **Draw a chemical skeleton from its real geometry, not by eye.** Compute the vertices and project them; a cage like
  adamantane is the diamond lattice (four CH at the odd-signed corners of a cube, six CH2 at the axis points), and a
  short script emitting the bond paths is faster and right. An invented structure in a textbook figure is worse than
  no structure. Past one molecule, a small generator earns its keep: rings from a ring-from-vertex helper (ipso atom
  plus direction from the ring centre), fused rings from the shared edge, chains alternating ±30°, bonds trimmed at
  labelled atoms, and a non-bonded distance check before drawing (it caught an indole folded over its own peptide
  chain at 2.7 px; one bond angle fixed it). Where a compound's identity rests only on vendor synonyms (PubChem
  depositor names, no ChEMBL synonym), draw nothing and say on the figure why. Name the parts a reader should
  recognise (a peptide's residues, its acyl tail) with short labels placed by measured clearance from every atom and
  atom label, stepping in small increments with a cap: uncapped, a long label walks off the drawing, and a first
  guess landed on a carbonyl oxygen (a peptide explainer, 2026-11-05).

## 2. Drawing the biology

- **One level of abstraction per figure.** Every element in a panel is drawn at the same realism: a cartoon enzyme beside a full skeletal formula and a near-realistic antibody reads as a toy. Pick the register (surface silhouettes traced from real structures, BioRender-style) and draw every protein and drug in it, with true relative size on one scale and any magnified inset labelled with its factor (a peptide explainer, Figure 2, 2026-11-20: "a bit toy, more faithful biology, more like biorender, same level of abstraction for all elements").
- **The drawing names; the legend explains.** A label in a biology figure is the thing's name ("cytoplasm"); its
  definition ("the interior of a cell") goes in the figure legend, for readers outside the field. Explanatory phrases
  inside the drawing make it read as a diagram, not a figure (a chemistry explainer, 2026-11-06: "say the thing cytoplasm and
  then define it ... in the figure legend ... not in the actual graphical section").
- **In systems cell-biology figures the protein's label goes inside its shape.** G-protein subunits, kinases and
  enzymes carry their short name centred in the glyph, which is sized to hold it; long names stay outside and the
  shape takes the abbreviation, which also ties an enzyme to the gene bar of the same name (a peptide explainer,
  2026-11-05: "i think usually labels are applied in shape ... for systems cell bio figures"). Text that crosses a
  shape's stroke needs a paper halo (`paint-order:stroke`) or the stroke cuts through it.
- **Use a real icon for an organ or object, not a freehand one.** A hand-drawn brain reads as a blob; take a CC0
  outline (Health Icons, healthicons.org) and fill it with a flat token colour, and record the source and licence in
  the repo. Check what the project already has before downloading (a peptide explainer, 2026-11-05: "non-realistic brain
  self drawn. biorender: try to find open source icon" — the icon was already in the project's own icon folder).
  **Take the outline variant when the page is line art**, not the filled one: solid glyphs sit heavier than stroked
  drawings and pull the eye off the data. Define each icon once as a `<symbol>` and place it with `<use>`, so an
  icon that appears twice is drawn once (a chemistry explainer, Figure 9, 2026-11-06: filled Health Icons swapped for the
  outline set after the render, blood drop used in both routes).
- **Two marks drawn alike are a claim that the two things are alike.** Inside one comparison, an identical glyph says
  "same thing", so either the glyph carries the real, citable difference or you draw one thing. A panel contrasting two
  receptor subtypes drew both as the same seven-helix bundle; since only the receptor's *name* was in dispute, it became
  one bundle labelled with a question mark and the two claims as labelled arrows (a peptide explainer, 2026-11-05: "what makes
  these different? showing same symbol for both"). A glyph that recurs across figures for different instances is fine
  when the key names the **class** it stands for ("class A GPCR, seven helices"), not one instance.
- **Draw in the field's own conventions, with depth**: for cell biology, DNA as a helix with the gene banded and a bent
  promoter arrow, membranes as bilayers, proteins with shape, modifications as small lettered circles, soft shading,
  and the math written where it belongs (2026-10-24: "rich, detailed, scientific ... not over-simplified"). A mechanism
  of action shows shape at every step: the drug as its chemical structure (or bead string) at the site it binds, the
  receptor in its bilayer, enzymes and transporters as proteins with a pocket, second messengers as small molecules,
  vesicles fusing, DNA bound at its element; a box is only for a step nobody can draw (a peptide explainer, 2026-11-05:
  "when making scientific diagrams, do deep, show shape (chem structure, cell machinery) to illustrate MoA").
- **When the question is "how do these differ", draw the things themselves, not a scatter of regions.** A key in a
  pocket, a chain along a groove, a hand on a face says more than three labelled blobs on axes; keep the measured
  quantity as a small bar under each drawing (a peptide explainer, 2026-11-05: "gotta show more, actually illustrate pockets
  small mol can bind vs peptide vs antibody" after an abstract mass-vs-contact-area plot).

## 3. Colour for compounds and classes

- **The page's subject decides what a hue codes.** On a page about a cell, hues code places in it; on a page whose
  subject is a set of compounds, the compound IS the category and each one gets its own hue. Deciding this from the
  library-wide code rather than from what the page is about gets it backwards (a peptide explainer, 2026-11-05: Claude
  argued four compounds should share one site-of-action hue; then "the n=4 small molecule page (diff color every
  molecule), and the peptide research page (peptide highlight, diff color for each peptide)"). Draw the hues from
  the existing token set so the budget holds.
- **An entity on two pages keeps its colour and its name on both.** One compound appeared in both a small-molecule
  set and a peptide explainer; giving it one hue across the pair is what makes two pages one body of work, and is the
  thing a reader uses to carry an idea between them (a peptide explainer, 2026-11-05: "i think n=1 peptide in list of 4,
  use it in [the other page]. same color" / "see the importance of connecting information?"). Say the link in the
  caption too, and tell whoever owns the other page which token you used.
- **Siblings in one class share a hue family, never one hue.** Two molecules of the same class (semaglutide and
  tirzepatide) get two clearly distinct strengths of the class hue, used everywhere each appears, and a key names the
  molecules, not the measure the axis already gives (a peptide explainer, Figure 7, 2026-11-21: "the pink here refers to
  multiple things?" - one rose marked both drugs and was keyed "2025 sales").
- **A subject and its endogenous counterpart share a hue at two strengths.** The drug is the saturated mark, its
  natural ligand the same hue at ~22% with a stroke, so "same binding site" survives while the subject stays the
  thing the eye lands on.
- **A hue codes a category, not an instance.** Asked whether four compounds should each get a colour, the answer
  was no: three acted at plasma-membrane receptors, so sharing one hue says "same class of target, different
  molecule", which was the point; spending hues on identity would also have collided with the page's existing
  site-of-action code. But the question caught a real error - the fourth acted in the nucleus and was wearing the
  receptor hue, so it moved to the nucleus hue, where the colour does real work (a peptide explainer, 2026-11-05: "use
  different colors for different molecules?"). A question about a code is worth answering with the code's own logic,
  then checking every mark against it.
- **One thing, one colour, everywhere it appears.** A compound drawn rose at its receptor gets a rose bar in the
  results below it; splitting a thing's hue between a "what it is" code and a "how good the evidence is" code breaks
  the eye's link between the two halves of a figure. Where the two codes collide, identity wins the hue and the
  evidence statement goes in the heading or caption (a peptide explainer, 2026-11-05: "same color for molecule should be
  used to show molecule and highlight bar effect below (both red or both green) harmony!"). A bar labelled where it
  sits needs no key row at all.

## 4. Mechanisms

- **A figure's one-line claim states the mechanism, not a verdict on it.** The bold line under a scientific figure
  is the current understanding of what the thing does, in one sentence a specialist would accept: "Aticaprant
  antagonises the kappa-opioid receptor on dopamine terminals, removing dynorphin's Gi/o-mediated inhibition of
  dopamine release", not "Occupying the receptor is not the same as treating the illness" (a peptide explainer,
  2026-11-05: "figures: objective, not opinion ... just describe 1 line takeaway of current understanding of MoA").
  An editorialising claim is easy to write when the data surprised you - the surprise belongs in the prose, and
  evidence status ("terminated for insufficient efficacy", "the subtype is unsettled") is a fact, so it stays.
- **A drug's mechanism of action has a playbook**: `references/moa-figures.md` — the five things the figure carries,
  what to draw per target class (GPCR, enzyme, transporter, channel, nuclear receptor, biologic), the evidence tier and
  the dashed arrow for an inferred step, the open question and date that keep a moving field's figure honest, and the
  scope it stays inside (mechanism, not use).
- **A mechanism gets a deep figure: parts, circuit, signal**: three panes under one plate, each with a small header
  and live readout; flux drawn as dots moving along each reaction at the model's speed; the abstract circuit; the
  signal on a strip chart with the real parameter on one slider; a chain row reading shape → pattern → function.

## 5. Micrographs and assay plots

- **Micrograph panels follow the published immunocytochemistry layout.** One column per channel plus a "Merge"
  column; the channel label sits below each image column, in that channel's display colour and regular weight,
  and is the stain name alone with no parentheses ("Hoechst" in blue, "Phalloidin + WGA" in pink, "Merge"); a
  masks column names the object and the method ("Nuclear masks, Otsu + watershed"), never a bare "Masks", and the
  caption says what made them (a threshold, a watershed, a named model); single channels in greyscale; nothing above the images but the panel letters. The scale bar is a plain white bar inside the
  bottom-right corner with its length centred directly above it in small white text ("20 µm"), and the caption repeats it
  once ("Scale bars, 20 µm"). Condition labels at the left of each row. No bold in a figure except panel letters.
  A condition needs no colour of its own: the treated group in ink and the controls in grey reads cleanly, and
  colour then belongs to the channels alone; a condition that does take an accent takes one no channel is using.
  Titles stay short: the figure title under eight words, a panel title under four, the design details (wells,
  fields) in the caption. Nature and Cell figure conventions are the reference for all of this: bold lowercase
  panel letters top-left and nothing else bold, one sans at two sizes, axis labels with units, no gridlines, and
  no free text blocks on the canvas: summary numbers (a ratio, a fold change) live in the legend or on an axis
  (2026-11-08: "this info belongs in figure legend", of a "Ratio to DMSO" block beside a plot).
  Spacing is measured, not eyeballed: one constant gap between neighbouring panels, a larger constant between
  panel groups, the same title-to-image gap above every column, and a plot the height of the image block it sits
  beside; print the gaps from the code (2026-11-08: "consistent spacing of title above image, figure panel
  separation and balance").
  A value printed over marks or a reference line gets a white backing pill (alpha about 0.7, no edge) and moves
  off the line, outside the point cloud (2026-11-08: "this text is hard to read ... background white alpha 0.3",
  of median values on a dashed DMSO = 1 line). (Cell Painting figure, 2026-11-08, four rounds of
  notes: "legend goes below", "look at published cell ICC figures", "confusing to have AMG in pink since pink
  was already used for image", "scale bar should have units", "dont use bold text for figure columns", "keep titles short and clear", "should
  follow nature/cell style figure conventions", "AMG doesnt need to be color, black ok", "just Hoechst, colored blue. no parenthesis necessary", "'masks' of what? nuclei? from what model? be clear", "20 um is convention to label above the bar".)
- **Points alone look barren; give each group a shape.** Keep one point per item and set a half violin or a thin
  histogram behind each group in the same colour at low opacity, so the distribution reads at a glance while every
  point stays countable (a strip plot of 1,000 nuclei, 2026-11-08: "as violin plot? histogram? a little barren").
- **A condition's colour travels across panels**: the treated group's accent marks its points, its median value and
  its row or column label in the image panels alike, so a reader joins the pictures to the plot without reading the
  key twice (2026-11-08: "change row 2 text orange yellow to connect the information").
- **A method figure shows one real crop at every step, from the same code that makes the result.** One row per route, one panel per step, the number each step sets in its title (the threshold, the seed count, the objects in the crop); a comparison row (six threshold rules on the same crop) is allowed when the row says it is a comparison. Panels that come from a re-implementation drift from the pipeline; export the intermediates instead (a segmentation pipeline's steps.py, 2026-11-08: "methods should be transparent ... step-by-step, example crop nuclei at each step how the image changes").

## Related

figure-design (axes, keys, spacing, flow diagrams), moa-explainer (the whole mechanism page, `references/moa-figures.md`),
controlled-comparisons (fair comparisons, named controls, true scale bars), design-practice (the page around the figure),
page-legibility-check (measure overlaps, contrast and size), citations (every number's source), the person's style skill.

## Provenance

Split from figure-design on 2026-11-21, when that skill passed 420 lines and was answering two questions at once: how
a chart reads, and how the science inside it is drawn. The cases are unchanged, from a peptide explainer and a
chemistry explainer (2026-11-05 to 2026-11-21), a Cell Painting figure (2026-11-08) and a cell-biology diagram
(2026-10-24: "rich, detailed, scientific ... not over-simplified").
