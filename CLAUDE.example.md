# Working with me, every project

## Feedback becomes guidance
When I give feedback (a correction, a preference, a style note, surprise at a result), act on it, then route the
lesson with the capture-lesson skill in the same turn:
- **Applies to anyone doing this kind of work** → the matching general skill in `~/.claude/skills/` (or a new one).
- **My own taste, voice or way of working** → the `my-style` skill.
- **A fact about one project** → that project's memory.
Mention the update in one line at the end of the reply ("Skill updated: design-practice, axes say which way is good").

## How skills read
- General first: written so anyone can use them; my preferences live in `my-style`, which general skills point to.
- Guidelines with examples, phrased as what to do ("separate items with space, weight or alignment"), with the reason
  and the case that taught it. Judgement over rules.
- One owner per guideline; other skills link to it.

## Library upkeep
After a long session, or when I ask to refactor skills, run
`python3 ~/.claude/skills/capture-lesson/scripts/audit-skills.py` and follow capture-lesson's "Tend the library".
Once a week a scheduled task runs `skills-watch.py` (new or updated skills upstream, gaps, footprint) and leaves
proposals in `~/.claude/skills-watch/`; act on them only after I say yes.
