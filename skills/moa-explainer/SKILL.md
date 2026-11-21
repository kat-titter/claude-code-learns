---
name: moa-explainer
description: Builds a short mechanism-of-action explainer as one self-contained HTML page - a drug or compound followed from what it binds to the thing a reader can see in an assay - with the five beats, the four figures, the primary-source retrieval recipes and the checks. Use when asked to explain how a compound works, why it produces some visible phenotype, or to write an MoA page, explainer or artifact about a molecule.
when_to_use: Before writing any explainer about how a compound works; when a figure must show machinery rather than boxes; when a page's numbers must all come from sources read this session.
---

# Mechanism-of-action explainer

One page, about 1,000 words of running prose and four figures, that takes a reader from a molecule to the thing
they can see down a microscope. science-figures' `references/moa-figures.md` is the playbook for the mechanism
figure itself; this skill is the document around it.

## Gotchas

- **A `<style>` block inside an inlined figure SVG styles the whole page.** `circle{r:1.7px}` for strip-plot dots
  shrank every circle in every other figure to a dot, silently: the ATP icon became three specks and a kinase
  vanished. Scope every rule in a figure's style block to a class (`g.pt circle{r:1.7px}`), and when a drawn shape
  goes missing, read its computed geometry before redrawing it.
- **An icon file's declared viewBox is usually larger than what it draws.** Set each `<symbol>`'s viewBox to the
  drawing's own bounds, measured with `getBBox()` in the browser on the symbol's direct children; a Servier
  chromosome in its own 381-wide box rendered 42% of the width asked for. Measure after the stylesheet is clean, or
  mangled shapes poison the bounds.
- **A shaded colour icon does not survive being flattened to one ink.** Bioicons' ATP (yellow phosphates, grey sugar)
  became a dark blob. Draw that one in the page's own hand - three circles, a pentagon, a fused ring - and record in
  SOURCE.txt that the icon was downloaded and not used.
- **Author every figure at the figure band's exact width.** The band here is 740 px (780 px text column, 20 px inset
  each side), so a 740-unit viewBox renders at scale 1 and a 12 px label is 12 px. An 880-unit drawing in the same
  band renders every label at 0.84x and fails the 11 px floor.
- **page-legibility-check reports ratio 1 for white text on a filled SVG shape**, because it compares the text colour
  with the page background and cannot see the fill behind. Compute those pairs by hand from the tokens and record the
  numbers, and leave a label that already passes at 5.8:1 as it is.
- **Record every downloaded asset's path, licence and date in a SOURCE.txt beside it**, including the ones not used.

## The five beats, in this order

1. **The visible thing, in the lead.** Open on what the reader would notice in a well or a slide, with its real
   number ("one nucleus in five comes out more than twice the area of a vehicle-treated one"). State the puzzle in
   the next sentence ("the drug never touches DNA"), then promise the route.
2. **What the compound is.** Who made it and why they chose this molecule over its predecessor, its identity numbers,
   and its status said plainly: phase, trial id, approved or not, and what it is used for now. A compound that
   failed in the clinic and lives on as a screening control has a more interesting paragraph than one that did not.
3. **What it binds, and what that protein does.** Name the target family, give the measured potencies, then spend
   the paragraph on the target's own jobs, because the mechanism is what stops when they stop.
4. **What a cell does about it.** The classic experiments that settled the phenotype, named with their compounds and
   years, then the same picture in the compound at hand.
5. **Why the visible thing follows, and what the assay sees.** Close the loop on the lead's number, and say in one
   paragraph which links are measured and which are joined up.

Headings state findings, not topics. Keep one carried question from the lead to the last line.

## The first screen shows the thing

A page that opens on a headline and six lines of prose has told the reader nothing they can look at. Put a
masthead above the fold, before the byline: the molecule's structure at one side, and at the other the mechanism
at the scale the reader will meet it, drawn in the piece's own channel colours. For a drug that changes a cell,
that is a control cell beside a treated one, the changed feature drawn to its measured scale with both numbers on
it. Then drop the separate structure figure, because the masthead already draws the molecule and a page says each
thing once. (AMG 900 explainer, 2026-11-17: "molecule and simple moa should be visible right away not just text".)

Author it at the figure band's width, with the key under it and the caption under that, like any other figure; a
one-line mechanism strip repeating the caption's bold line is the first thing to cut when it runs past the edge.

## The four figures

| # | what it shows | how it is drawn |
|---|---|---|
| 0 | masthead | the molecule plus the cell-level mechanism, above the fold (see above); draw the structure on a smaller canvas rather than scaling the big one down, or its labels shrink below the floor |
| 1 | the mechanism | the target in its place, the ligand at its site, and the step that stops: `references/moa-figures.md` |
| 2 | the process | drawn in its own natural form, not a box chain - a cell cycle as a cycle, a transport step as two conformations - with the consequence drawn to scale (nuclei with area proportional to DNA content) |
| 3 | what the assay sees | the measurement, one point per object, half violin behind each group, median bar with its value, ratio to control on the right axis, and over the pair the test, its p and the effect size (a house-style skill, if there is one, sets the strip-plot form) |

Each figure keys its own marks under the drawing; the caption's bold line states the mechanism, not a verdict.

## Getting the facts (all primary, nothing from memory)

Recipes that answer, with no key and no sign-in:

```bash
# titles, abstracts, journal, volume, pages, DOI, PMCID
curl -s --get "https://www.ebi.ac.uk/europepmc/webservices/rest/search" \
  --data-urlencode 'query=TITLE:"AMG 900"' --data-urlencode format=json \
  --data-urlencode pageSize=15 --data-urlencode resultType=core
# full text of an open-access paper (Europe PMC's own fullTextXML returns 500 often; this one works)
curl -sL "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC6279493/unicode"
# verify every citation's volume, issue, pages and year before writing the list
curl -s "https://api.crossref.org/works/10.1158/0008-5472.CAN-10-3001"
# structure and identity
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/AMG%20900/property/SMILES,MolecularFormula,MolecularWeight,IUPACName/JSON"
# potencies, with the paper each value came from
curl -s "https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL2140408&standard_type__in=Ki,IC50&limit=200"
curl -s "https://www.ebi.ac.uk/chembl/api/data/document/CHEMBL4265875.json"   # resolve the source
```

- **Cite ChEMBL's source, not ChEMBL.** A number in ChEMBL carries a `document_chembl_id`; resolve it and cite that
  paper, saying which quantity it reports (IC50 is not Ki).
- **Look for the user's own measurements before drawing a schematic.** The close is far stronger with real data, and
  a public CC0 dataset (Cell Painting Gallery, JUMP) plus the user's own segmentation beats an invented histogram.
  Carry the user's own caveats across: if their masks run smaller than the consortium's pipeline, say both ratios.
- **Say which links are measured and which are joined.** One plain paragraph near the end, and a dashed arrow on the
  inferred step in the figure. Name the experiment that would settle it.

## Checks before publishing

1. `humanize-science-writing/scripts/review_prose.py index.html` - aim for grade about 9, mean sentence under 17,
   spread near 9, limits stated, and a callback from the lead.
2. `page-legibility-check/scripts/check-page.sh index.html "" 2000 <dir>` - zero overlaps, zero clipped, no
   horizontal scroll, at 1280 and 400 px, light and dark.
3. Every reference verified at its DOI through Crossref, markers adjacent to their claims (the citations skill).

## Worked example

One page on AMG 900 and nuclear size: 1,007 words, four figures, sixteen references, and a close measured from
1,092 nuclei of the public JUMP pilot plate. Its folder splits the page into parts a script splices: a head file
holding the style system (ported from a sibling page, so the two share one look), a body file of prose, one authored
SVG per figure, and a `scripts/` folder that generates the structure, the icon symbols and the measured plot. The
build script splices the lot into `index.html` and prints the prose word count, so the word budget is checked on
every build rather than at the end.

## Related

science-figures (`references/moa-figures.md`, molecules and mechanisms), figure-design (axes, keys, spacing),
the person's style skill (palette, strip plots, one accent with one meaning), html-docs (the page as a document), storytelling (the arc), humanize-science-writing, citations,
page-legibility-check, cell-figure-style (if the page carries a micrograph panel).

## Provenance

Written 2026-11-17 while building one MoA explainer, at the request "this Moa doc should be a skill". The five beats
are the order that brief asked for; the gotchas are the four things that went wrong in that build.
