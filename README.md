# claude-code-learns

A small setup that lets Claude Code keep what it learns. When you correct a
mistake, the lesson gets saved as a reusable **Skill** — so the agent stops
making the same mistake twice.

**Read the one-page explainer:** https://kat-titter.github.io/claude-code-learns/

It's built on what Claude Code already has — [Agent Skills](https://code.claude.com/docs/en/skills)
and memory. The one addition is a Skill whose job is to write other Skills. The
pattern itself (self-improving skills / a learnings loop) is well established; this
is a tidy take on it, with the capture tied to the moment you correct the agent.

## What's here

```
index.html                     the explainer page (also linked above)
coding-skills.md               catalog of the skills
lessons-inbox.example.md        the "fast store" — cheap capture before promotion
skills/
  capture-lesson/              the meta-skill: turns a correction into a Skill
    scripts/scan-corrections.py  Stop-hook that logs corrections automatically
  macos-long-render/           wrap long Mac jobs in caffeinate (don't sleep-stall)
    scripts/caffeinate-render.sh
  citations/                   add/verify numbered citations in HTML
    scripts/check-citations.py
```

## Use it

1. Copy any skill folder into `~/.claude/skills/` (personal) or
   `<project>/.claude/skills/` (one repo).
2. A skill is just a folder with a `SKILL.md`. The `description` is what makes
   Claude reach for it — write it like the moment you'd want it.
3. Optional, for hands-off capture: add a `Stop` hook in `~/.claude/settings.json`
   that runs `scan-corrections.py`, so corrections get logged even when not caught
   in the moment:

   ```json
   { "hooks": { "Stop": [ { "hooks": [
     { "type": "command",
       "command": "python3 ~/.claude/skills/capture-lesson/scripts/scan-corrections.py" }
   ] } ] } }
   ```
   (Adjust the path. The hook only appends candidate lines; it never blocks a turn.)

## Why it works

It mirrors how memory actually consolidates — a fast store grabs what just
happened, a slow process keeps the parts that matter. The explainer page has the
references (McClelland 1995; Kumaran, Hassabis & McClelland 2016; and the synaptic
plasticity / tagging / replay literature).

## Notes

- Validate that a skill actually triggers with the official `skill-creator` plugin.
- Use freely.
