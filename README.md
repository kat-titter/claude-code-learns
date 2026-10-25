# claude-code-learns

Correct Claude Code once and it remembers. Feedback becomes a skill, the library keeps itself tidy, and a weekly
check finds new skills worth adding.

**Explainer:** https://kat-titter.github.io/claude-code-learns/

```mermaid
flowchart LR
  you(["your feedback"]) --> hook["feedback hook"]
  self(["the agent's own surprise"]) --> cap
  hook --> cap{{"capture-lesson"}}
  stop["end-of-session hook"] --> inbox[("lessons inbox")]
  inbox -->|"recurs"| cap
  cap -->|"for anyone"| general["general skill"]
  cap -->|"your taste"| taste["your style skill"]
  cap -->|"one project"| memory[("project memory")]
  general --> next(["next session"])
  taste --> next
  memory --> next
  week[["weekly check"]] -->|"proposals, on your yes"| cap
```

- **Learns fast**: a correction becomes a guideline in the same turn.
- **Notices mistakes**: hooks catch feedback; the agent flags its own surprises.
- **Stays light**: only skill descriptions load each session; the rest waits on disk.

## Install

```bash
git clone https://github.com/kat-titter/claude-code-learns && cd claude-code-learns
```

```bash
./install.sh --name yourname
```

Adds the `capture-lesson` skill, a `yourname-style` skill for your taste, and two hooks. Safe to re-run;
`--dry-run` shows what it will do. For the weekly check, paste `skills/capture-lesson/weekly-watch.md` into a
weekly scheduled task.

## Keeping it tidy

- One home per guideline; a new case extends the line that is already there.
- Each guideline is one line: what to do, an example, the date.
- `audit-skills.py` flags repeats, overlaps and long skills to merge or split.

## What's here

```
install.sh              set up in one command
skills/capture-lesson/  the skill that writes skills, with its hooks and checks
templates/, *.example*  starting points: style skill, CLAUDE.md, hooks, memory, inbox
coding-skills.md        an example library of 15 skills
index.html              the explainer
```

MIT licensed.
