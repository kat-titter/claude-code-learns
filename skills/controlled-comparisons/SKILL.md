---
name: controlled-comparisons
description: Makes a scientific comparison controlled and traceable before it reaches a slide, figure or paper - same dose, groups and chance level per row, named and negative controls, leakage checks, fair baselines and true scale bars. Use when comparing drugs, labs, sites, instruments or models, or when someone asks "is that the same dose?", "what's chance here?" or "where does this number come from?".
when_to_use: Before any analysis number is quoted or published; when two rows were computed on different groups or splits; when a classifier names the group suspiciously well; when a micrograph goes into a figure.
---

# Controlled comparisons

Each guideline below comes with the case that taught it (a pitch deck, JUMP Cell Painting data, Oct 2026). Use the ones
that fit the comparison in front of you.

## Gotchas

- DMSO wells called "untreated": a real term for a different control (a pitch deck skeptic, 2026-10-19). Name each control by what was in the well.
- A luck baseline computed on a different number of labs than the model saw makes chance lopsided: same groups, same count, every row.
- One split's headline number: report the spread over splits before quoting it.
- Scale bars without true units: every micrograph's bar says its length in µm.

## Compare like with like

- **Same dose.** Read the dataset's methods for the dose at every site before comparing a drug across sites. JUMP ran
  library compounds at 10 µM everywhere and at 0.625 µM at one site; the lab that "kept 80% of its cells" had a
  sixteenth of the dose. Compare the sites at one dose, show the dose on the figure, and show the other site beside the
  comparison with its dose (it doubles as a dose check: lower dose, fewer cells killed).
- **Same groups, same chance.** When rows compare inputs or methods (profile, DNA image, brightfield), fit every row on
  the same groups, the same items and the same split, so one chance level holds for the whole table.
- **Show the noise floor and a positive reference on the same plates**: control against control, and a known drug
  measured the same way, next to the result.
- **Name the cause the data can support.** When dose and site coincide (one site, one dose), "consistent with the
  lower dose" is the honest reading.

## Controls, named and shown

- Call each control by what was in the well: a DMSO (vehicle) well and an untreated well are different controls. On a slide, the
  vehicle control is a check in the held-equal row, "✓ same liquid, no drug" beside "same cells" and "same protocol",
  rather than a bare "✓ no drug" (a check asserts a presence); the names and glosses (U2OS, DMSO: the liquid drugs are dissolved
  in) go in the caption, since a gloss column on stage was too much text (a pitch deck 03, 2026-11-08: "no drug is a
  check? how to simply explain liquid 'vehicle control'", then "too much text").
- Add a negative control to every classifier: the same pipeline with labels shuffled inside each training fold. It
  should land at chance; show it as a row.
- Put the reference wells on screen next to the treated ones (same plate, same field size, same display window).
- **Run the control that would fake the result**: name what could produce the same number without the effect and
  score it as its own row. In a history of judgements, time or revision order (a person Fixes, the work is redone,
  they Keep: render date alone ranked Keeps over Fixes in 13 of 13 pairs); in an embedding of a mix, the source
  material alone (the outgoing song alone scored the same as the transition). When the control wins, the data cannot
  answer the question; say so and name the data that could. (a DJ tool taste study, 2026-10-27.)
- **Show a positive control a reader already understands**, shared by every group compared: the one with a textbook
  mechanism and the largest effect in the data, named with its mechanism in a few words ("AMG900, Aurora kinase
  inhibitor: cells copy their DNA but cannot divide, so nuclei double"). The most familiar name can be too weak to see
  (dexamethasone, effect 9 against AMG900's 58). Pick its runs from batches whose known answer came out, unless the
  failure is the point. (a pitch deck, 2026-10-26: "pick well-understood, commonly used control".)

## Leakage and spread

- **Look for columns that only say which group a row came from** (frame size, bit depth, a site's fixed setting):
  `${CLAUDE_SKILL_DIR}/scripts/constant_within_group.py TABLE --group site`. Drop them for input-vs-input comparisons, keep both versions
  in the results so the change is visible.
- **One split is one draw.** Score every input on many splits (20 deals of the batches worked well) and report the
  median and range, plus how many splits one input beats another. A single split can be the second-worst of twenty.
- **Choose features and scaling inside the training fold**, and hold out whole batches when batches carry the signal.
- **Dedupe before any split**, exact and near copies alike (one model under two IDs, a resubmitted record), so no copy
  sits on both sides; report class imbalance with its source (what made one class common) and write the assumptions
  beside the data description (essay, 2026-11-19: "de-dupe data important in machine learning ... describe data
  processing"; "check data: source of imbalance, assumptions").

## Luck baselines that fit the question

- "1 in k" assumes every answer is equally likely. When answers are lopsided (one input picks the same neighbour for
  most batches), build the baseline by permutation: shuffle one side's answers among the items of the same group,
  keeping how often each answer is picked, and compare the observed agreement with that distribution.
- Say what the baseline holds fixed ("beyond each lab's usual neighbour, agreement is luck").
- Leave out pairs that agree by construction (a series' first point against itself) before a rank correlation.

## Pictures and structures

- **Scale bars carry their unit and their true length** for each image: field width = image pixels × pixel size from
  the instrument metadata. Check old bars by measurement (nucleus size against images of known scale found tiles that
  were 1000-pixel fields drawn as if 1080).
- **Every micrograph names its stain and what it marks**, a small chip beside the scale bar ("Hoechst, DNA"; for a
  composite, one swatch per channel in its display colour). Read the channel from the code or file that pulled the
  image, not from how it looks. A reader of a deck of grey nuclei asked for the legend on every cell image (a pitch deck,
  25 Oct 2026: "when showing cell image, always include channel legend like Hoechst (DNA)").
- **Show cells, not only nuclei**: a two-channel composite, nucleus plus cell body (DNA and actin/membrane in Cell
  Painting), in the page's own two colours, so the image reads with the figures around it (a pitch deck: nuclei pink,
  cell body green, rhyming with pink for a point and green for the field; 2026-10-26: "dont show only nuclei").
- **Cell crops follow image practice**: one whole cell per crop, centred, the rest masked to black (nuclei seed the
  cells); a scale bar on every crop and the channel key below the image block, never on the pixels; one brightness scale across
  every group and condition, set from each group's own control cells and applied to its treated cells too; the dose
  in the title; in the number panel under it, the baseline named ("1× = DMSO") and the summary line named ("mean
  ×2.1"). (a pitch deck 05, 2026-10-26.)
- **An example of "normal" is a control well, checked in the source's own annotation** (DMSO, control siRNA, mock), and
  every borrowed image carries its source and licence (CC BY and CC BY-SA require credit). A slide's six published
  "normals" turned out to be four perturbed wells and one control; the IDR annotation files said so (a pitch deck 02c,
  2026-10-25). Pick the well and field by a rule in code (control wells on the same plate, QC-passed, off the edge,
  sharpest by a focus score) rather than by eye: the well first picked by eye was nearly the blurriest of 48.
- **Gloss the model system once, where it first appears**: what the cells are and why they are used ("U2OS: bone-cancer
  cells, flat and easy to image"), with how widely the field uses them in the reader's layer. A deck that shows one
  cell line throughout left a reader asking what it was (a pitch deck, 25 Oct 2026). Caught again 2026-11-08: the gloss sat in a hidden list, so the stage
  kept it out of sight; on a slide it goes in the figure caption ("U2OS cells [26]"), the stage keeps "same cells".
- **Draw a structure from the dataset's own record** (its SMILES or InChI), state what the record leaves out (no
  stereochemistry), and name the active form with its source.
- **Look an identifier up in the dataset's own metadata, never from memory**, and assert it against a second
  record before a filter uses it (JUMP: the InChIKey in compound.csv.gz gives AMG900 = JCP2022_037716; a remembered
  id, JCP2022_085227, was aloxistatin, and only an assert against the project's own mapping caught it, 2026-11-08).
- **Connect the chemistry to the biology in one short chain** on the figure (reactive group, what it binds, what the
  cell does), with debated mechanisms stated in the fine print and the Q&A. Include the intermediate step that says
  why the binding kills ("binds GPX4 → lipid peroxides pile up → cell dies, ferroptosis"), one small icon per step,
  each arrow resting on a source whose abstract says it; a step no abstract states ("membrane breaks") stays off the
  figure. (a pitch deck 05a, 25 Oct 2026: "how does it kill cells? intermediate step".)

## Numbers people can trace

- **Audit the geometry, not only the caption.** A fact check that reads sentences misses the numbers a figure
  *draws*. A weight-loss figure labelled a dose range without its doses and drew its placebo bar at 3.9% where the
  cited report gives 2.2%; a second row drew a 2.7% placebo arm that is another trial's discontinuation rate. Only
  the caption was in the claim list, so only the caption was checked. When a verdict corrects a number, grep the
  figure for every mark built from it (bar width, axis position, label, the appendix row that repeats it) and
  recompute each from the axis scale. (Peptide fact audit, 2026-11-17.)
- **A summary box is not a result.** Trade reports and press releases mix a results paragraph, a takeaways box and
  investigator quotes, and the three disagree. One report's body gave per-dose reductions *against* placebo while
  its own takeaways box called the same range "placebo-adjusted"; a weight-loss figure quoted at 12.4% was an
  investigator's sentence, where the results paragraph said 11.2% against 2.1% placebo. Take numbers from the
  results paragraph, and treat a figure that appears only in a quote or a box as unsourced even though it is "in
  the cited source". (Same audit.)
- **A negative claim needs its own retrieval.** "No study has measured X" is a claim about a literature, and the
  document already cited often reports X: an FDA briefing carried the repeat-dose and genotoxicity studies a page
  said did not exist, and cited the stability study it called unmeasured. Retrieve every "no study", "never" and
  "none found" separately before it goes on a page. (Same audit.)
- **Cite the record, not the review that mentions it.** Mechanism detail drifts to whichever review names it: a
  receptor's class, its G protein, the direction of its second messenger and its transmembrane count were all hung
  on review abstracts that state none of them, while the UniProt entry gives the function text and the segment
  count and PubChem gives the sequence. Prefer the registry record; it is citable, dated and quotable.
  (Same audit.)

- **Conflicting evidence stays on the slide**, marked and cited beside the claim it qualifies ("*conflicting results:
  Gleerup et al 2021"), so the room weighs both. (A 2023 lactoferrin review talk.)

- **Say the unit of replication on the figure**: that G09 is a well, how many wells and how many cells each group
  has, in the axis labels or the caption, so a reader knows what n counts (a figure with "G09, n = 437" left a
  biologist asking "G09 is well? using all wells?", 2026-11-08).
- **Show the effect both ways, as two y axes on the same plot**: raw units on the left (182 → 301 µm²) and the
  ratio to the control on the right with the control at 1 (DMSO = 1, AMG900 = 1.6), a faint line at 1.0, the two
  scales agreeing exactly, so no separate ratio table is needed (2026-11-08: "what is the delta in raw units, as
  ratio DMSO (DMSO is 1)", then "two y axis: one is raw unit, one is ratio DMSO = 1").
- **Counts come with their masks.** A panel of the segmentation outlines on the same crops the figure shows, and
  the number of objects each filter dropped per group (size floor, border), so the n can be trusted and the method
  is on the page (2026-11-08: "show segmentations where counts come from so they can be trusted, be transparent
  with methods").
- Compute every number on a slide from a results file, with an assert for each claim the text makes.
- Record the dose, the groups, the splits and the excluded items in the results, so the figure and the file agree.
- Give each analysis one skeptic who recomputes the main numbers independently and tries to break the design
  (alignment, leakage, chance, dropped rows, keys other code reads).
- **Anchor a new measurement to the dataset's own published numbers before trusting its scale.** A nuclear area
  from a fresh segmentation is checked against the pixel size in the instrument metadata and against the
  dataset's released per-well features for the same wells (JUMP's `Nuclei_AreaShape_Area`: 240 / 246 / 324 µm²
  for the two DMSO wells and the AMG900 well; a fresh Otsu mask gave 182 / 183 / 263, 25% smaller, same order and
  a 1.3 to 1.5× effect either way). Report the anchor beside the new number (2026-11-08: "sanity check is the
  scale correct? nuclei size is reasonable within published").

## Scripts

`${CLAUDE_SKILL_DIR}/scripts/constant_within_group.py TABLE... --group COL [--near 0.01]` lists columns constant inside every group (exit 1
when found) and near-constant ones. Validated on two different JUMP tables (the e17 wells, 8 labs; the positive-control
wells, 3 labs): both surface the camera-frame `TotalArea` columns.

## Related

pitch-deck-story and html-slide-deck (where the comparison is shown), design-practice (axes, legends), citations.

## Provenance

a pitch deck, 2026-10-17 to 2026-10-20: "use perturbations same dose. remember science, controls are important.
show dose. show chemical structure of RSL3"; "use same set of labs, same # of labs so random baseline is the same";
"cell scale bars ... should have um units". Skeptics found the DMSO/untreated naming, the frame-size columns, the
lopsided luck baseline and the single-split headline; each fix is in results/e16 and results/e17.
