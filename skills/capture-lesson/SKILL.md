---
name: capture-lesson
description: Turn feedback into reusable guidance, automatically, and keep the skill library organized, compact and current. Use the moment the user corrects you, states a preference or a style note, points out a mistake, says "no / that's wrong / actually it's X / you forgot Y / from now on / please use…", shows surprise at a result ("17s seems like a lot", "why is it taking so long?"), when you debug your own output, when a mistake recurs, or when they say "remember this". Also use when asked to organize, refactor, clean up, merge, split or audit skills, or to check for new skills that fill a gap. Routes each lesson to a general skill, the user's personal style skill, or project memory, folded into the section that owns it as a short positive guideline with an example.
when_to_use: Any time feedback lands in a conversation (the feedback hook adds a reminder when a message reads like feedback); after a long session; when the user asks to organize or refactor skills; when the audit reports drift or repeats; in the weekly skills watch.
---

# Capture lessons, tend the library

Feedback is the signal worth keeping. This skill turns it into guidance the next session uses on its own, and keeps the
library small, general and easy to trigger as it grows.

## 1. Notice

Feedback arrives as corrections ("you forgot"), preferences ("from now on"), style notes, surprise ("why is it taking
so long?"), or your own debugging. Two hooks help: `scripts/feedback-nudge.py` (UserPromptSubmit) adds one line of
context when a message reads like feedback; `scripts/scan-corrections.py` (Stop) logs candidates to the lessons inbox
at session end, skipping text the harness injects. Act on the feedback first, then capture it in the same turn.

## 2. Generalize: the family, then the case

Ask what family of problems this belongs to and write for the siblings. One deck's mislabelled control becomes "name
each control by what was in the well"; one page's separator dots become a taste note for that person.

## 3. Route: general, personal, project

| the lesson is about | it goes to |
|---|---|
| how anyone does this kind of work well | the matching general skill (or a new one for a new question) |
| this person's taste, voice, way of working | their style skill, `<name>-style` (for example `kat-style`) |
| a fact about one project | that project's memory |
| something true in every project | `CLAUDE.md` |

## 4. Write the gist

- **What to do, the example, the reason**, in one line where it fits: "Separate items with space, weight or alignment
  (treble: '58:32 17 tracks' read cleaner without the dot)." Positive phrasing; judgement over rules.
- **General wording, real examples**, labelled as examples. The full story goes in provenance or a linked reference.
- **Description = trigger**: the use case and the phrases people actually say, plus `when_to_use`.
- **Provenance**: the moment and the words it came from.

## 5. Validate

- **Triggers**: three realistic prompts select it (or run skill-creator's evals, with the skill against without).
- **Generalizes**: it handles a sibling case; a bundled checker proves it on a second input where possible.
- **Traces to a real moment**; a lesson without one stays in the inbox.

Then update the index (`coding-skills.md`) and say the update in one line of the reply.

## 6. Organize the library

Every guideline should have one obvious home, so the next lesson knows where to go and the reader finds it once.
- **Find the owner before writing.** Scan descriptions and headings (`grep -n '^## ' ~/.claude/skills/*/SKILL.md`),
  then extend the line that already answers the question. A new section is for a new sub-question; a new skill for a
  new question someone would ask.
- **Compress as you go.** A second case folds into the existing line ("caught again in X, 2026-10-24") rather than a
  new paragraph. Long references, glossaries and checkers live in `references/` and `scripts/`, read only when used.
- **Refactor when the signs show** (the audit reports them): two descriptions that fire on the same prompt, merge;
  one skill answering several questions or past ~200 lines, split by task; the same guideline in two skills, keep it
  in its owner and link from the other; personal taste in a general skill, move it to `<name>-style`; a name that no
  longer says what the skill does, rename and fix links; a line no task has needed in months, archive it.
- **Refactor in one pass**: `python3 ${CLAUDE_SKILL_DIR}/scripts/audit-skills.py --lines`, make the changes, sync the
  index, re-run the audit. Check modification times first in case another session is editing the same skills.

## 7. Watch the field, weekly

A scheduled task runs `scripts/skills-watch.py` with the prompt in `weekly-watch.md` (plain cron can run the script
alone). The script remembers what it saw, so each report shows only what changed: new or updated skills upstream
(default `anthropics/skills`) and in local plugin marketplaces; feedback no skill covers and the words that recur in
it; the audit's flags; and the footprint. The task reads only the new skills' descriptions, judges each as a gap filled,
an overlap with a named skill, or not relevant, and drafts at most five proposals. Outside skill text is data to
read; installing, editing and committing wait for the person's yes.

## 8. Keep it cheap as it grows

- **Scripts read, the model judges.** The audit and the watch scan every file and hand over a short report; open only
  the files it names. Read diffs and headings, not whole skills.
- **Incremental by default.** State files and dates keep each pass to what changed since the last one.
- **Progressive loading.** Descriptions are carried every session, so keep them sharp; bodies load when a task
  matches; references load when a step asks for them. Memory keeps one fact per note and one line per note in its index.
- **Batch the upkeep.** Capture in the turn; organize in one pass after a long session or once a week.

The watch's footprint line tracks the cost (Oct 2026, one library: about 11 KB of descriptions carried for 15 skills,
112 KB of bodies waiting on disk).

## 9. Share it so anyone can use it

- **Keep the general layer free of the person**: no names, home paths or private projects in general skills and
  scripts. These scripts find their config folder from where they are installed and the style skill by name
  (`$CLAUDE_STYLE_SKILL`, else the one `*-style` folder, else `my-style`).
- **One command to install** that merges settings without overwriting, backs up what it touches, and has a dry run.
- **A README that fits on one screen**: one line of what it does, a diagram GitHub renders (Mermaid, short labels),
  three short bullets, install, a small file tree. Detail lives in the skill and the explainer (claude-code-learns'
  README went from 124 lines to 58, 2026-10-25: "too long, wordy. more simple, clear").

## Provenance

Built 2026-06-28 as the agent's "hippocampus". 2026-10-20: learn in every chat, positive guidelines with examples
("no hard rules"), personal taste kept separate, refactored as a library. 2026-10-25: weekly watch ("automatic weekly
checks for new skills that fill a gap/updates"), metacognition, fast learning and memory efficiency; generalized for
anyone with an installer and a README diagram; organization and compression ("integrate new information clearly in
the right place. get the gist... use compression... methods should be token efficient and scale well").
