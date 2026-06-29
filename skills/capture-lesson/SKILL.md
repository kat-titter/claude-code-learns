---
name: capture-lesson
description: Turn a correction into a reusable Skill — automatically. Fire the moment the user corrects you, points out a mistake, says "no / that's wrong / actually it's X / you forgot Y", expresses surprise at a result ("17s seems like a lot", "why is it doing that?"), when you debug your own output, when the same mistake recurs, or when they say "remember/save this". Captures the lesson, generalizes it to the whole class of problem, checks it isn't a duplicate, and validates it before saving.
when_to_use: Any time a problem is noticed and corrected in the conversation — that correction IS the lesson. Don't wait to be asked. This is the agent's hippocampus; it should fire on its own.
---

## It fires on corrections, not commands

The capture signal is a **correction in the natural conversation** — the brain's
salience tag for "keep this." Watch for, and self-trigger on:

- the user corrects you — "no", "that's wrong", "actually…", "you forgot…"
- surprise that implies a problem — "that seems like a lot", "why is it doing that?"
- you debug your *own* output, or hit the same mistake twice
- explicit — "remember this", "save this"

The moment a correction lands, capture. Most won't become skills — that's fine.

## 1 · Capture cheap — the fast store (hippocampus)

Jot the candidate immediately to `~/.claude/lessons-inbox.md` (one line, don't
break flow). Fast, cheap, lossy. Promotion comes later.

## 2 · Generalize — the class, not the instance

Before writing anything, ask: **what *family* of problems is this?** Name the
general case; the description and fix must cover **siblings**, not just this exact
file/value. (One doc's citation bug → "numbered references in *any* markup", not
"this file".) An overfit skill is noise.

## 3 · Don't hoard — gate + route (slow consolidation, cortex)

- Promote to a skill only if it **recurs** or is clearly **important**; let trivia
  age in the inbox and decay.
- **Search existing skills first.** If one covers the area, **update it** (integrate
  into the schema) instead of spawning a near-duplicate.

## 4 · Validate — required, or it stays a note

A captured skill is not done until it passes all three:

- **triggers** — it actually fires on a realistic prompt (sanity-check it, or A/B
  with the `skill-creator` plugin: with-skill vs without).
- **generalizes** — it handles a *sibling* case, not just the original. Where you
  can, **bundle a checker and prove it on a different input** — e.g. `citations`
  ships `check-citations.py`, which then validated a *separate* project.
- **provenance** — it traces to a real moment in this conversation. If you can't
  point to where it came from, you invented it — drop it.

Fail any → it's a note in the inbox, not a skill.

## 5 · Index, and (optionally) automate the catch

Add a row to `~/.claude/coding-skills.md`. Hands-off capture is **active**: a
`Stop` hook (`scripts/scan-corrections.py`, wired in `settings.json`) scans each
finished session for correction phrases and logs candidates to the inbox — so
nothing is lost even when not self-invoked. Review the inbox to promote.
