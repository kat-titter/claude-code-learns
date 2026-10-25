# An example library

The author's skill library as of October 2026 (16 skills), one line each, to show the shape a library takes after a few months:
one skill per question, a personal style skill beside the general ones, checkers bundled where a claim can be measured.
Linked skills are in this repo; the rest live in the author's `~/.claude/skills/`.


## Library upkeep

| Skill | What it is for |
|---|---|
| [`capture-lesson`](skills/capture-lesson/SKILL.md) | Turn feedback into guidance in the same turn, routed to a general skill, the `<name>-style` skill, or project memory; tend the library (`audit-skills.py`); weekly watch for new skills and gaps (`skills-watch.py`). Hooks: `feedback-nudge.py` on each prompt, `scan-corrections.py` at session end. |
| `kat-style` | The author's personal layer (kept private): how guidance is written, writing voice, design taste, science standards, how updates are given. |

## Pages, figures, decks

| Skill | What it is for |
|---|---|
| `design-practice` | Composition, text, legends, axes and scale bars, interactivity, colour. Checkers: `check_design.py` (separators, repeats), `check_symbols.py` (unique symbols). |
| `page-legibility-check` | Measure contrast, label collisions, overflow and tiny text at desktop and phone widths, light and dark (`check-page.sh`). |
| `interactive-figures` | Design, build and audit interactive figures and explorables: push the system before naming the property, field notation, one calm card for every view, inertia and reduced motion, first frame without JS; `audit_interactions.py` checks targets, names, focus, click errors, motion and no-JS frames (validated on the loop-table post and its essay). |
| `field-vocabulary` | The field's own words in anything a person reads; glossaries for treble and cell-biology decks (`check_vocab.py`). |
| `html-slide-deck` | One-file HTML decks: views, talk and PDF layers, stable rebuilds, printing, rendering, publishing to GitHub Pages and verifying it live (five scripts). |
| `pitch-deck-story` | What goes on a five-minute pitch: story order, one idea per slide, numbers that read, fair comparisons, appendix boards, timed script and Q&A. |
| `verify-animated-page` | Verify canvas/WebGL/rAF pages in the browser pane: fresh captures, focus-safe tests, synthetic clocks (`raf_probe.js`). |

## Science and writing

| Skill | What it is for |
|---|---|
| `controlled-comparisons` | Same dose, same groups and chance, named and negative controls, leakage checks, spread over splits, fair luck baselines, true scale bars, structures from the record (`constant_within_group.py`). |
| `storytelling` | The arc, openings and closings for anything with a reader: And-But-Therefore, concrete before abstract, one question carried through, a close that answers or calls back. The medium skills link here. |
| [`citations`](skills/citations/SKILL.md) | Numbered references checked against the real source, with in-text markers kept in sync (`check-citations.py`). |
| `humanize-science-writing` | Long-form science writing that reads human and travels, with a reviewer for cohesion, legibility, argument and AI-style signals (`review_prose.py`). |
| `viral-tweet` | High-reach posts and threads: hooks, specifics, reply velocity, links in replies; voice from the author's profile. |

## Audio and long jobs

| Skill | What it is for |
|---|---|
| `beat-align-audio` | Beat-align two music signals before overlapping them; verify by kick timing (`check_beat_alignment.py`); Rubber Band R2 realtime for stretches. |
| [`macos-long-render`](skills/macos-long-render/SKILL.md) | Keep long Mac jobs awake (`caffeinate`), tell idle from thermal slowdowns, and diagnose a shared, overloaded machine (load, swap, BLAS threads). |

To add a lesson, follow `capture-lesson`: find the section that owns it, write the gist, update this index.
