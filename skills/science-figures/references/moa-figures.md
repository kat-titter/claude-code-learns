# Mechanism-of-action figures

For drawing how a therapeutic works: a drug, peptide, biologic or candidate at its target. Read with science-figures §2 and §4
(shape over boxes) and the person's style skill (palette, type). Written for a novel therapeutic domain, where
the mechanism is partly open and the evidence is uneven — the figure has to show both.

## What the figure carries

Five things, in this order, one step per arrow:

1. **The target in its place** — receptor in its bilayer, enzyme in its compartment, transporter spanning the membrane,
   nuclear receptor on DNA. Place says as much as shape: peripherally restricted means drawn outside the blood-brain
   barrier, and the barrier is then part of the figure.
2. **The ligand at its site**, drawn as its chemical structure (small molecule), bead string (peptide) or domain
   cartoon (biologic), sized against the target so the contact area is honest.
3. **What binding does to the machinery** — the conformational change, the pocket closing, the dimer forming. This is
   the step most figures skip, and it is the mechanism.
4. **The signalling chain**, each member drawn as itself, down to the cellular output.
5. **The effect in the body**, at the tissue or whole-organism level, named as the endpoint a trial measures.

## By target class

- **GPCR**: seven-helix bundle in the bilayer, orthosteric pocket inside the bundle (allosteric site on the outer face
  if that is the point), heterotrimeric G protein on the inner leaf, then the effector (adenylyl cyclase, PLCβ), the
  second messenger as a small molecule, the kinase, the output. β-arrestin is the second branch — draw it when bias is
  the story, greyed when it is not. **Antagonist**: ligand in the pocket, chain drawn but dimmed, with the endogenous
  agonist shown blocked outside. **Agonist**: chain live. **Inverse agonist**: the chain below its own basal level,
  which needs a baseline mark to be visible at all.
- **Enzyme**: the fold with its active-site cleft, substrate entering and product leaving, cofactor where it binds. A
  competitive inhibitor sits in the cleft; an allosteric one sits elsewhere and the cleft deforms. **An effect on
  enzyme expression is not an effect on the pocket** — draw more or fewer copies of the enzyme, with the transcription
  step that made them, and leave the pocket open. Confusing the two is the commonest error in this class.
- **Transporter**: the two conformations side by side (outward-open, inward-open) with the substrate moving between
  them, and the ion gradient that pays for it.
- **Ion channel**: pore in cross-section, gate, ions as dots on one side, and open probability as the quantity that
  changed.
- **Nuclear receptor**: ligand in the ligand-binding domain, dimer on a bent response element, coactivator, transcript
  leaving.
- **Antibody or large biologic**: the Y with its epitope contact drawn true to scale against a small molecule at the
  same target — the size difference is the mechanism's constraint, not decoration.

## Status and evidence, on the figure

A novel domain's figures are read by people deciding what to believe, so each one says what tier its claim sits at.
A small mono tag by the caption, not a colour nobody can decode:

| tier | says |
|---|---|
| approved | the agency and the indication (approvals differ by country; "approved in Russia, not FDA-approved" is one tag, not two figures) |
| in trials | the phase and the registry id (NCT…), so the reader can check it themselves |
| preclinical | the species and the preparation (rat, in vitro, membrane prep) |
| thin | single lab, single language, or a mechanism inferred rather than measured |

Where a step is inferred rather than shown, draw its arrow dashed and say so in the caption. A dashed arrow is the
cheapest honesty in the figure.

## Where it is going

A mechanism figure in a moving field dates within months, so it carries its own direction:

- **The open question as the last element**: the step nobody has measured, drawn with a question glyph or a dashed
  arrow, named in the caption as the question rather than hidden by omission.
- **The next readout**: the trial or experiment that will settle it, and roughly when.
- **A date on the figure**, mono, small. It tells a later reader what the figure could not have known.

## The page around the figure

A whole mechanism-of-action explainer - the five beats, the four figures, the primary-source retrieval recipes and
the checks - is the `moa-explainer` skill. This file stays the playbook for the mechanism figure itself.

## Scope

Stay at the level the mechanism needs: target, pathway, tissue, measured endpoint, trial status, literature. A
mechanism figure needs no dose, route, schedule, regimen, source or availability, and nothing about a person taking the
compound — none of it is mechanism, and a set of figures that reads as a how-to-use guide rather than pharmacology gets
stopped before it is drawn (a peptide explainer MoA set, 2026-11-05: "maybe avoid discussion or insinuation of
use/ingestion?"). Introduce each compound by its target family and its status; that is both the honest frame and the
one that lets the work run. See prompt-practice §6 for briefs on the same material.

## Provenance

Written 2026-11-05 for one explainer's MoA figures (aticaprant, ART27.13, bromantane, GB-115), from "im just
interested in the science and want to illustrate MoA of novel therapeutic domain well" and "see where it's going".
The shape-over-boxes rule it builds on is science-figures §2, captured the same day.
