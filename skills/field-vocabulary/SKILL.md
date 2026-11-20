---
name: field-vocabulary
description: Swaps coined internal jargon for the words practitioners use (DJ, music, science, design) in anything a person reads - UI labels, captions, legends, hover cards, docs and reports. Use when writing or reviewing user-facing text, naming a feature or control, or when someone says "use normal words", "no jargon", "what does that mean?" or "that's not what DJs call it".
when_to_use: Before publishing user-facing text; when a reader trips on a term; when labels were named during development.
---

# Field vocabulary

Coined names are fine inside code (variables, files, internal notes). Anything the user or their audience reads uses
the words people in that field already use. A term the field doesn't use reads as noise or, worse, as a claim.

## Gotchas

- A word coined while building ("crate", "seam", "rules") reads as normal to the builder: run the glossary check before publishing.
- A prep note or brief the person reads alone, later, is written for a cold reader: no rule names, kit terms or labels
  from the session ("conventional, not classical", "the fixation search", "kit numbers"); each line says the action
  and why in plain words (a recruiter prep call, 2026-11-08: "what?", then "elaborate?").
- A real term with the wrong meaning is worse than jargon ("untreated" for DMSO wells): the project glossary maps each to the field's word.

- **Files are named by their extension.** A download or export lists its format as the file extension people see on disk
  (.txt, .cue, .mp3, .flac, .xml), never a word like "text" (a DJ tool export panel, 2026-11-06).

## Practice
0. **Learn the field's words before naming anything.** In a new domain, read how practitioners talk (a DJ's set
   notes, a methods section, a style guide) and name things that way from the first draft; a coined word renamed later
   survives in code, labels and docs (2026-10-27: "use existing words/vernacular (transition instead of seam)").
1. **Name things the way practitioners do.** DJ/music: playlist (not "crate" in our UI), track, transition (not "seam"),
   set, mix, cue, drop, breakdown, build, intro/outro, EQ, lows/mids/highs, bass swap, echo out, loop, key, bpm.
2. **Soften verdict words when the checks are guidance:** guideline, flag, "listen here", "follows / borderline / departs from it" (not rule, wall, fail, breaks).
2b. **Spell out every acronym where the reader first meets it**, then use the short form: "G-protein-coupled receptor
   (GPCR)", or a hover card on the first use (`.term` with a one-line definition), including one-letter codes in figures
   ("G, glycine" in the key). Run the check below the page before publishing. (Peptide docs, 2026-11-05: "never use an
   acronym w/o defining it first"; the reader had to ask what G, H and K meant.)
3. **When a new term is needed**, define it once, in plain words, where it first appears; a short phrase often does it.
   A label a stranger can't read ("tension building", "level") gets that gloss on hover (a DJ tool, 2026-10-27: "what
   does this mean? hover to reveal").
   One word per measure in every view (column, line tag, hover, docs): a short alias on one plot reads as a second
   measure (2026-10-27: "talk is conversationability. remember shared visual and linguistic key").
   Two near-synonyms side by side (behaviour and function) get their difference said in one line, or one of them goes
   (essay, 2026-11-19: "what is the different between behavior and function? need both?").
4. **Keep a person's own names** for things they named (in a DJ tool, "horses" for galloping kicks, "Keep"/"Fix").
5. **Name controls by their content** in science writing (controlled-comparisons); "lab" or "site" as the field uses it.
6. **Check before publishing:** run the checker on the user-facing files with the project's glossary.

- **A figure's labels take the field's verb, not a plain-English stand-in.** In pharmacology that is inhibit,
  activate, antagonise, transduce, upregulate, disinhibit, abolish: "binding blocked" not "kept off", "Gi/o not
  activated" not "never recruited", "release not inhibited" not "the brake, not applied", "CB2 antagonised" not
  "CB2 blocked", "transcription upregulated" not "transcribed more", "extracellular / intracellular" not
  "outside / inside". The caption may still explain in plain prose; the labels on the drawing carry the term
  (a peptide explainer, 2026-11-05: "always use scientific words like inhibit, activate").

## Checker
`python3 ${CLAUDE_SKILL_DIR}/scripts/check_vocab.py --glossary GLOSSARY.json FILE_OR_DIR ...`
- GLOSSARY.json: `{"prefer": {"crate": "playlist", "seam": "transition"}, "ignore": ["crate_map", "data-crate"]}`
  (`prefer` maps a term to the field's word; older glossaries call it `banned`, which still works)
  (keys are case-insensitive whole words; `ignore` lists substrings that make a hit OK, e.g. identifiers in code).
- Scans visible text of .html (tags/attributes stripped except title/alt/aria-label), .md, .txt, .svg text; prints
  `file:line: term -> suggestion`; exit 1 if any hit. A default glossary for a DJ tool lives next to the script
  (`dj_glossary.json`), and one for cell-biology decks (`science_glossary.json`).

## Provenance
2026-10-20, a DJ studio: "please no emergent use of vocab like 'crate', use field-aligned vernacular 'playlist'".
Earlier in the same project: "seam" → "transition" (a live DJ's note, 2026-10-14) and "rules" → "guidelines" (2026-10-20).
a pitch deck, 2026-10-19: a skeptic found the deck calling DMSO wells "untreated"; JUMP's untreated wells are a different
control. The deck now says DMSO throughout; `science_glossary.json` catches it.
