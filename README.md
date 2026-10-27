# claude-code-learns

**Correct it once. It remembers.** Feedback becomes a skill, the library keeps itself tidy, and a weekly check finds
new skills worth adding. Built only on what Claude Code already has: skills, hooks, memory and scheduled tasks.

**Explainer:** [kat-titter.github.io/claude-code-learns](https://kat-titter.github.io/claude-code-learns/) &emsp;
**Install:** [one command](#2-install) &emsp; **Example library:** [`coding-skills.md`](coding-skills.md)

---

## 1. How it works

```mermaid
flowchart TB
  you(["You"])
  agent(["Claude Code"])
  nudge["feedback-nudge.py"]
  pnudge["prompt-nudge.py"]
  scan["scan-corrections.py"]
  inbox[("lessons-inbox.md")]
  cap{{"capture-lesson/SKILL.md"}}
  watch[["skills-watch.py"]]
  subgraph lib [" "]
    general["citations/SKILL.md"]
    taste["my-style/SKILL.md"]
    memory[("memory/MEMORY.md")]
  end
  you -->|"corrects, prefers"| nudge
  nudge -->|"each prompt:<br/>flags feedback"| cap
  you -->|"dictates, terse"| pnudge
  pnudge -->|"brief first:<br/>outcome, context, check"| agent
  agent -->|"notices<br/>its own slip"| cap
  scan -->|"session end:<br/>logs what was missed"| inbox
  inbox -->|"if it recurs"| cap
  cap -->|"for anyone"| general
  cap -->|"your taste"| taste
  cap -->|"one project"| memory
  lib -->|"loads when<br/>a task matches"| agent
  watch -->|"weekly: proposes,<br/>you approve"| cap
  classDef default fill:#dafbe1,stroke:#1a7f37,color:#116329
  classDef core fill:#aceebb,stroke:#1a7f37,stroke-width:2px,color:#116329,font-weight:bold
  class cap core
  style lib fill:none,stroke:#8c959f,stroke-dasharray:4 3
```

- **Learns fast**: a correction becomes a guideline in the same turn.
- **Notices mistakes**: hooks catch feedback; the agent flags its own surprises.
- **Reads you right**: a terse or dictated prompt becomes a brief before work starts (`prompt-practice`).
- **Stays light**: only skill descriptions load each session; the rest waits on disk.

## 2. Install

```
git clone https://github.com/kat-titter/claude-code-learns && cd claude-code-learns
```

```
./install.sh --name yourname
```

Adds `capture-lesson`, `prompt-practice`, a `yourname-style` skill for your taste, and four hooks. For the weekly
check, paste `skills/capture-lesson/weekly-watch.md` into a weekly scheduled task.

> [!TIP]
> `./install.sh --name yourname --dry-run` shows every change first. Re-running is safe.

## 3. Keeping it tidy

- One home per guideline; a new case extends the line that is already there.
- Each guideline is one line: what to do, an example, the date.
- `audit-skills.py` flags repeats, overlaps and long skills to merge or split.

## 4. Files

```
install.sh              set up in one command
skills/capture-lesson/  the skill that writes skills, with its hooks and checks
skills/prompt-practice/ every prompt as a brief, with its hook
skills/html-*/          example general skills: lightly interactive HTML docs and decks, with checkers
templates/, *.example*  starting points: style skill, CLAUDE.md, hooks, memory, inbox
coding-skills.md        an example library of 22 skills
index.html              the explainer
```

## 5. Colophon

Built with Claude Code by Kat Titterton. Code under the MIT license; see [`LICENSE`](LICENSE).
