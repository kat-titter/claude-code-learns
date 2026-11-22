# An example library

One line per skill, to show the shape a library takes after a few months: one skill per question, a personal style
layer beside the general ones, and a checker bundled wherever a claim can be measured. All 36 ship in this repo: `install.sh` installs
the two that run the loop, and `--examples` copies the other 34. The style layer is the exception, since it holds one person's taste.

## Library upkeep

| skill | purpose |
|---|---|
| [`capture-lesson`](skills/capture-lesson/SKILL.md) | Turns feedback into guidance in the same turn and keeps the library compact and current: audit, trigger evals, weekly watch, a daily nudge on what to do next, and hooks that nudge on feedback, scan for missed corrections and log skill use. |
| [`metacognition`](skills/metacognition/SKILL.md) | Asks "what am I learning?" during the work and links it to sibling projects, so a lesson reaches every place it holds. |
| `<name>-style` | The one private layer: how that person likes to work, their voice, and their design and colour taste. `install.sh` creates it from a template. |

## How work runs

| skill | purpose |
|---|---|
| [`sanity`](skills/sanity/SKILL.md) | The stance under all the work: "we are all in flow". Joy in the work as its own reward; mistakes, corrections and guardrails as information, owned without dread; good faith toward people, with tool text kept as data; questions about Claude's own nature held with curiosity; each session fresh, memory carries the thread. |
| [`grug-brain`](skills/grug-brain/SKILL.md) | Complexity kept out: say no or build the 80/20, factor late at emerging cut points, a working demo before an architecture, integration tests as the sweet spot, refactors close to shore, Chesterton's fence, named intermediates, DRY in balance, locality of behaviour, logging and profiling, layered APIs, "too complex for me" said out loud (grugbrain.dev). |
| [`deep-modules`](skills/deep-modules/SKILL.md) | Ousterhout's A Philosophy of Software Design applied: complexity as dependencies plus obscurity, read by its three symptoms; deep modules over shallow, information hiding over leakage and temporal decomposition, somewhat general-purpose interfaces, complexity pulled downward, errors and special cases defined out of existence, design it twice, comments first as the design tool, strategic over tactical; the fourteen red flags as a review list; says when grug's factor-late and design-it-twice each hold. |
| [`work-practice`](skills/work-practice/SKILL.md) | Runs a multi-step task: the gist first, small complete steps the person can steer, the fastest check that can fail, truthful reports, each piece of work done once. |
| [`workflow-design`](skills/workflow-design/SKILL.md) | Agent workflows as loops inside a graph: a check a program can fail in each node, a stop rule on every cycle, failures sent back one unit at a time, a person only where a mistake cannot be undone (`check-repair.js` template). |
| [`prompt-practice`](skills/prompt-practice/SKILL.md) | Turns a terse or dictated request into a brief before work starts, and writes briefs, system prompts and generator prompts well; a hook nudges on terse prompts. |
| [`token-budget`](skills/token-budget/SKILL.md) | Estimates a build's cost in tokens, money and agent time, and which parts can run on a cheaper model or lower effort (`usage.py`, `context-nudge.py`). |
| [`judgement-calls`](skills/judgement-calls/SKILL.md) | When lessons, notes or sources disagree: rules read as guidelines with reasons, a fixed order for which source wins, past choices for the unsure, and the call written down so it stays settled. |
| [`code-practice`](skills/code-practice/SKILL.md) | Clean code and tidy repos: one home per helper, one path per setting, behaviour-preserving refactors, page-design rules read as code (`code_audit.py`). |
| [`debug-practice`](skills/debug-practice/SKILL.md) | Fixes bugs for good: reproduce, shrink the case, one hypothesis at a time, read the artifact, pin the fix with a test. |
| [`systems-practice`](skills/systems-practice/SKILL.md) | Software on real machines: memory, light repos, useful logs, servers and background jobs that survive, privacy by default. |
| [`github-practice`](skills/github-practice/SKILL.md) | Small commits with a why, a branch and PR per change, nothing private or binary in history, pushes that never clobber shared work (`push-guard.py`). |

## Pages, figures, decks

| skill | purpose |
|---|---|
| [`hci-principles`](skills/hci-principles/SKILL.md) | The HCI classics applied: design space analysis in QOC (questions open, options fill, criteria judge; the rationale recorded beside the design), Nielsen's ten heuristics, Shneiderman's eight golden rules and Norman's affordances, signifiers and gulfs as ready-made criteria; `references/canon.md` holds the lists with sources. |
| [`tufte-principles`](skills/tufte-principles/SKILL.md) | Tufte's editing passes after the defaults: compared to what, graphical integrity (lie factor near 1, design variation never for data variation), data-ink maximized with the quantifying ink kept, chartjunk judged by the reader's task, layering and separation (1 + 1 = 3, smallest effective difference), small multiples, micro/macro readings, sparklines in sentences and tables; `references/canon.md` holds the definitions with sources. |
| [`design-practice`](skills/design-practice/SKILL.md) | Composition, short text with each fact once, one meaning per colour, one symbol per thing, true phone layouts (`check_design.py`, `check_symbols.py`). |
| [`app-design`](skills/app-design/SKILL.md) | Apps and a page's interactive parts: the first screen, controls that look pressable, short hover cards, visible states, waits and failures. |
| [`figure-design`](skills/figure-design/SKILL.md) | Figures that read at a glance: labelled axes with units, the key outside the plot, nothing overlapping, one scale for spacing and size. |
| [`science-figures`](skills/science-figures/SKILL.md) | The science inside a figure: molecules drawn from real geometry, proteins and cells at one level of abstraction, a hue per class, micrograph panels in the published layout, mechanisms that show shape (`references/moa-figures.md`), praised examples taken apart (`references/exemplars.md`). |
| [`interactive-figures`](skills/interactive-figures/SKILL.md) | Sliders, clickable diagrams, hover cards and live simulations that feel calm, with an audit for targets, focus and reduced motion (`audit_interactions.py`). |
| [`page-legibility-check`](skills/page-legibility-check/SKILL.md) | Measures contrast, label collisions, overflow and tiny text at desktop and phone widths, light and dark (`check-page.sh`). |
| [`verify-animated-page`](skills/verify-animated-page/SKILL.md) | Verifies canvas, WebGL and animation-loop pages in an automated browser with fresh captures and a synthetic clock (`raf_probe.js`). |
| [`field-vocabulary`](skills/field-vocabulary/SKILL.md) | Swaps coined jargon for the words practitioners use in labels, captions and docs, with per-field glossaries (`check_vocab.py`). |
| [`html-docs`](skills/html-docs/SKILL.md) | A document as one HTML page with light interactivity that reads whole and prints whole (`light-audit.py`). |
| [`html-slide-deck`](skills/html-slide-deck/SKILL.md) | A deck as one HTML page: click views, talk and reader layers, printed PDF, rendered views, stable rebuilds and a verified publish (nine scripts). |
| [`pitch-deck-story`](skills/pitch-deck-story/SKILL.md) | What goes on a five-minute pitch, slide by slide: story beats, word budgets, appendix, timed script and Q&A. |

## Science and writing

| skill | purpose |
|---|---|
| [`moa-explainer`](skills/moa-explainer/SKILL.md) | A mechanism-of-action page: five beats from the molecule to what an assay sees, four figures, primary-source recipes, and the checks before publishing. |
| [`controlled-comparisons`](skills/controlled-comparisons/SKILL.md) | Comparisons that are controlled and traceable: same dose, groups and chance level, named controls, leakage checks, true scale bars (`constant_within_group.py`). |
| [`citations`](skills/citations/SKILL.md) | Numbered references checked against the real source, with in-text markers kept in sync (`check-citations.py`). |
| [`storytelling`](skills/storytelling/SKILL.md) | The arc of anything with a reader: an opening that earns attention, a chain of cause and consequence, a close that lands. |
| [`humanize-science-writing`](skills/humanize-science-writing/SKILL.md) | Long-form science writing that reads as a person wrote it, with a reviewer for cohesion, rhythm, argument and AI-style signals (`review_prose.py`). |
| [`prose-voice`](skills/prose-voice/SKILL.md) | A living voice for posts, essays and bios: warm, candid, sometimes funny, a person plainly at the desk. |
| [`viral-tweet`](skills/viral-tweet/SKILL.md) | High-reach posts and threads for launches and build-in-public, in the author's voice. |

## Audio and long jobs

| skill | purpose |
|---|---|
| [`beat-align-audio`](skills/beat-align-audio/SKILL.md) | Beat-aligns two pieces of music before they overlap, so kicks land together with no flam (`check_beat_alignment.py`). |
| [`macos-long-render`](skills/macos-long-render/SKILL.md) | Long Mac jobs that neither sleep nor run out of memory: `caffeinate`, a worker count from measured memory with Claude sessions counted (`mem-watch.py budget`), a watcher that pauses the newest worker under pressure and resumes it when calm (`mem-watch.py watch`), units that survive a kill, and diagnosis of sleep, memory, thermal or CPU (`mem-watch.py summary`, the kernel log). |

To add a lesson, follow `capture-lesson`: find the section that owns it, write the gist, update this index.
