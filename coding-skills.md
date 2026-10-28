# An example library

This is an example. It is the author's skill library as of late October 2026 (29 skills), one line each, to show the
shape a library takes after a few months: one skill per question, a personal style layer beside the general ones,
checkers bundled where a claim can be measured. Linked skills ship in this repo; the rest live only in the author's
own skills folder and are listed to show the shape.

## Library upkeep

| Skill | What it is for |
|---|---|
| [`capture-lesson`](skills/capture-lesson/SKILL.md) | Turns feedback into guidance in the same turn and keeps the library compact and current: audit, trigger evals, weekly watch, and hooks that nudge on feedback, scan for missed corrections and log skill use. |
| `metacognition` | Asks "what am I learning?" during the work and links it to sibling projects, so a lesson reaches every place it holds. |
| `<name>-style`, `<name>-visual-house-style` | The author's personal layer, kept private: how they like to work, voice, design and colour taste, figure house style. |

## How work runs

| Skill | What it is for |
|---|---|
| `work-practice` | Runs a multi-step task: the gist first, small complete steps the person can steer, the fastest check that can fail, truthful reports, each piece of work done once. |
| [`prompt-practice`](skills/prompt-practice/SKILL.md) | Turns a terse or dictated request into a brief before work starts, and writes briefs, system prompts and generator prompts well; a hook nudges on terse prompts. |
| `token-budget` | Estimates a build's cost in tokens, money and agent time, and which parts can run on a cheaper model or lower effort (`usage.py`, `context-nudge.py`). |
| `code-practice` | Clean code and tidy repos: one home per helper, one path per setting, behaviour-preserving refactors. |
| `debug-practice` | Fixes bugs for good: reproduce, shrink the case, one hypothesis at a time, read the artifact, pin the fix with a test. |
| `systems-practice` | Software on real machines: memory, light repos, useful logs, servers and background jobs that survive, privacy by default. |
| `github-practice` | Small commits with a why, a branch and PR per change, nothing private or binary in history, pushes that never clobber shared work (`push-guard.py`). |

## Pages, figures, decks

| Skill | What it is for |
|---|---|
| `design-practice` | Composition, short text with each fact once, one meaning per colour, one symbol per thing, true phone layouts (`check_design.py`, `check_symbols.py`). |
| `app-design` | Apps and a page's interactive parts: the first screen, controls that look pressable, short hover cards, visible states, waits and failures. |
| `figure-design` | Figures that read at a glance: labelled axes with units, the legend outside the plot, nothing overlapping, one scale for spacing and size. |
| `interactive-figures` | Sliders, clickable diagrams, hover cards and live simulations that feel calm, with an audit for targets, focus and reduced motion (`audit_interactions.py`). |
| `page-legibility-check` | Measures contrast, label collisions, overflow and tiny text at desktop and phone widths, light and dark (`check-page.sh`). |
| `verify-animated-page` | Verifies canvas, WebGL and animation-loop pages in an automated browser with fresh captures and a synthetic clock (`raf_probe.js`). |
| `field-vocabulary` | Swaps coined jargon for the words practitioners use in labels, captions and docs, with per-field glossaries (`check_vocab.py`). |
| [`html-docs`](skills/html-docs/SKILL.md) | A document as one HTML page with light interactivity that reads whole and prints whole (`light-audit.py`). |
| [`html-slide-deck`](skills/html-slide-deck/SKILL.md) | A deck as one HTML page: click views, talk and reader layers, printed PDF, rendered views, stable rebuilds and a verified publish (nine scripts). |
| `pitch-deck-story` | What goes on a five-minute pitch, slide by slide: story beats, word budgets, appendix, timed script and Q&A. |

## Science and writing

| Skill | What it is for |
|---|---|
| `controlled-comparisons` | Comparisons that are controlled and traceable: same dose, groups and chance level, named controls, leakage checks, true scale bars (`constant_within_group.py`). |
| [`citations`](skills/citations/SKILL.md) | Numbered references checked against the real source, with in-text markers kept in sync (`check-citations.py`). |
| `storytelling` | The arc of anything with a reader: an opening that earns attention, a chain of cause and consequence, a close that lands. |
| `humanize-science-writing` | Long-form science writing that reads as a person wrote it, with a reviewer for cohesion, rhythm, argument and AI-style signals (`review_prose.py`). |
| `prose-voice` | A living voice for posts, essays and bios: warm, candid, sometimes funny, a person plainly at the desk. |
| `viral-tweet` | High-reach posts and threads for launches and build-in-public, in the author's voice. |

## Audio and long jobs

| Skill | What it is for |
|---|---|
| `beat-align-audio` | Beat-aligns two pieces of music before they overlap, so kicks land together with no flam (`check_beat_alignment.py`). |
| [`macos-long-render`](skills/macos-long-render/SKILL.md) | Keeps long Mac jobs awake with `caffeinate`, and tells sleep and idle-throttling from thermal slowdowns or a busy machine. |

To add a lesson, follow `capture-lesson`: find the section that owns it, write the gist, update this index.
