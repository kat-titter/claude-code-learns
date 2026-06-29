# Coding skills — index

Reusable, hard-won coding lessons. **Procedural lessons live as proper Claude Code
Skills** in `~/.claude/skills/` (they auto-trigger and load only when relevant).
This file is just the human-readable catalog.

| Skill | What it's for |
|---|---|
| [`capture-lesson`](skills/capture-lesson/SKILL.md) | **The skill for skills** — turn a hard-won lesson/gotcha into a properly-structured, auto-triggering Skill. Invoke this whenever a reusable lesson emerges. |
| [`macos-long-render`](skills/macos-long-render/SKILL.md) | Wrap long unattended macOS jobs (renders, training, batch) in `caffeinate` so the Mac can't sleep/idle-throttle them. Also: how to tell sleep/idle-throttle (sudden cliff) from thermal (gradual climb), and that cold benchmarks under-estimate multi-hour ETAs. |
| [`citations`](skills/citations/SKILL.md) | Add/verify numbered citations in docs (esp. HTML). Web-verify each source's real bib details; keep in-text superscripts in sync with the reference list (the grouped-`<ol>` auto-numbering-restart bug). Bundles `check-citations.py` to verify indexing. |

*Project-scoped skills live in each repo's `.claude/skills/` — e.g. `tiat_slop_2026/.claude/skills/render-loop/` (render the vanitas loop, caffeinate baked in).*

### Adding a new lesson
- **Procedure / checklist / gotcha-with-a-fix** → make a Skill: `~/.claude/skills/<kebab-name>/SKILL.md` with a `description` (the trigger — lead with the use case + variant phrasings) and `when_to_use`. Bundle scripts under `scripts/` and reference with `${CLAUDE_SKILL_DIR}`. Add a row here.
- **Standing fact / convention** (always-true, not a procedure) → put it in `CLAUDE.md` instead.
- Validate triggering with the `skill-creator` plugin (`/plugin install skill-creator@claude-plugins-official`).
