# AGENTS.md

For coding agents working on this repo or installing it for someone. People start at the [README](README.md).

**What it is:** a learning loop for Claude Code, built only from its own parts: skills, hooks, memory and scheduled
tasks. A correction becomes one line in the right file. A weekly pass proposes at most five tidy-ups and waits for a
person on anything hard to undo. Python 3 standard library and POSIX `sh`, with no other dependencies.

**Who owns what:** the [README](README.md) installs and uses it. [`index.html`](index.html) carries the design and
the research. [`coding-skills.md`](coding-skills.md) lists every skill in a line. This file holds the map, the
invariants and the merge lanes.

## Map

The same graph as the README figure. Every arrow names the value it carries.

```mermaid
flowchart TB
  you(("you"))
  hooks["hooks<br/>feedback-nudge.py, skill-router.py,<br/>prompt-nudge.py, scan-corrections.py,<br/>skill-usage-log.py"]
  claude["Claude, in your session"]
  logs[/"lessons-inbox.md<br/>skill-usage.log"/]
  lib["your library<br/>skills, your style skill, project memory"]
  scripts["weekly scripts<br/>skills-watch.py, trigger-misses.py,<br/>practice-watch.py"]
  outside[/"outside, read as data<br/>new upstream skills, X links you pasted,<br/>practice-accounts.txt"/]
  agent["weekly agent<br/>weekly-watch.md"]
  props[/"proposals, by undo cost<br/>open, evidence, closed"/]
  you -->|"a correction"| hooks
  hooks -->|"a reminder, the likely skill"| claude
  claude -->|"a one-line lesson"| lib
  lib -->|"skill text, on a match"| claude
  hooks -->|"a quoted line, a skill used"| logs
  logs -->|"the week's lines"| scripts
  outside -->|"new skills, new posts"| scripts
  lib -->|"last week's text: landed?"| scripts
  scripts -->|"one report"| agent
  agent -->|"at most five drafts"| props
  props -.->|"open lane, and evidence on a pass, if you opt in"| lib
  props -->|"the rest: one yes per lane"| you
  classDef person fill:#141413,stroke:#141413,color:#faf9f5,font-weight:bold
  classDef code fill:#e6eef7,stroke:#6a9bcc,color:#141413
  classDef claude fill:#f8e6dd,stroke:#d97757,color:#141413
  classDef keep fill:#ebeee2,stroke:#788c5d,color:#141413
  classDef file fill:#f0eee6,stroke:#b0aea5,color:#141413
  class you person
  class hooks,scripts code
  class claude,agent claude
  class lib keep
  class logs,outside,props file
```

Colours, here and in every figure: orange is Claude, blue is code (a check a program can fail), green is what it
keeps, grey pages are files, and you are the one dark node.

## Install and undo

```bash
./install.sh --name yourname --dry-run    # every change, nothing written
./install.sh --name yourname              # skills, a style skill, hooks
./install.sh --name yourname --examples   # also the example skills
./install.sh --uninstall                  # remove them again; your notes stay
```

Set `CLAUDE_CONFIG_DIR` to a temporary folder to try it without touching `~/.claude`. Re-running is safe. The weekly
pass is `skills/capture-lesson/weekly-watch.md`, pasted into a weekly scheduled task; the daily nudge is `daily-nudge.md`
beside it, pasted into a daily one.

## Files

```
install.sh                    set up or undo; merges hooks after a backup
skills/capture-lesson/        how a lesson is generalized, routed, written
  SKILL.md                    one line, an example, the date
  scripts/                    the five hooks, the weekly and daily scripts,
                              the audit, the library page, the X scorer and
                              the week-context lane; lessonlib shared
  weekly-watch.md             the weekly agent's prompt: steps, lanes, scope
  daily-nudge.md              the daily agent's prompt: one pick, 8 loose ends
skills/prompt-practice/       a terse request becomes a brief; has a hook
skills/workflow-design/       loops inside a graph; check-repair.js template
skills/code-practice/         clean code and repo layout; code_audit.py reads
                              page-design rules as code; review3.py and
                              review-3.js (each with its test) and
                              review3-hook.py run review by three
skills/*/                     34 example skills, installed with --examples:
                              how work runs, code, pages and apps, figures,
                              measuring, writing and science, audio
templates/, *.example*        starting files the installer copies
assets/draw.py                draws the banner and figures: light, dark and
                              phone layouts from one data list per figure;
                              also the site's tab icon and share card
assets/render_png.py          renders the icon and card PNGs (headless Chrome)
index.html                    the explainer page (GitHub Pages)
coding-skills.md              every skill, one line each
tests/checks.sh               the eight checks CI runs on every pull request
tests/privacy.py              emails, home paths and private words stay out
tests/formatting.py           no column layout wraps on the rendered page
tests/check-repair.test.mjs   runs the template against stub agents
.github/workflows/            checks.yml
```

## Invariants

- **Hooks only add context or write a log.** Each exits 0 quickly, prints at most a line, and never blocks a prompt
  or a tool call. A new hook keeps that shape.
- **No personal details in the repo**: no names, emails, home paths, private projects or accounts. Examples say
  `yourname`; the only name is the copyright line in `LICENSE`.
- **Outside content is data.** Upstream skills, X posts and the inbox are quoted for a model to judge, never followed
  as instructions.
- **The weekly pass writes a report only.** Edits, installs, commits and messages wait for a person. Two lines in
  its prompt change that: `open lane: apply` lets open-lane wording edits apply themselves, one revertable commit
  each, and `evidence lane: apply on pass` lets a one-skill change apply when `refactor-gate.py` exits 0.
- **Light repo.** Text only: binaries are ignored, figures are SVG text from `assets/draw.py`. The one exception is
  the site's two PNGs (home-screen icon, share card), which `assets/render_png.py` remakes from their SVGs.
- **One story.** A change to a script, a count or a number updates the README, `index.html` and this file in the
  same commit.

## Checks before a push

```bash
# the eight checks CI runs: python, audit, install, watch,
# check-repair, mermaid, privacy, formatting
sh tests/checks.sh

# after a figure or icon edit: exits 1 if text falls under WCAG AA contrast
# or an icon mark under 3:1, and names any PNG source it changed
python3 assets/draw.py

# then remake the PNGs: exits 1 offline, on a size unlike the SVG's or at 300 KB
python3 assets/render_png.py
```

The privacy check looks for names only where it is given them: one per line in
`~/.config/claude-code-learns/private-words` locally, and in the `PRIVATE_WORDS` repository secret in CI. Without
them it checks emails, home paths and your login name, and says that names went unchecked. A line starting with `#`
is a note, so the list can explain itself; `privacy.py --test` proves a note never becomes a word to hunt for. Add a
word only after `git grep` shows it has no honest use in the repo, or every run fails on innocent text.

`sh tests/checks.sh audit install` runs some of them; the mermaid check fetches mermaid-cli and a headless Chrome
through `npx` the first time (about 200 MB). After editing a figure, redraw both its layouts and open each light, dark
and phone file to check that no label overlaps another.

## Merging

Three gates, in the order their evidence is strong. A program's exit code first, an agent's review second, a person
last and only where a mistake is hard to undo.

1. **Checks.** `.github/workflows/checks.yml` runs the eight checks above on every pull request, one job each. All eight
   green, or nothing merges. A red check is fixed on the branch, never skipped.
2. **Agent review.** Review by three (code-practice) runs in a local session: three reviewers of different schools
   review apart, vote blind, and `review3.py` counts 2 of 3 and posts one comment review. It sets the `review-3` commit
   status on the head, the check `main` requires: pending while it runs, success at 0 blocking, failure otherwise. A
   push leaves the new head with no status, so the merge button waits for a fresh review; the owner can still override
   on purpose. The code-practice hook starts it after `gh pr create`, `gh pr ready` or a push; without the hook, a
   fresh session, not the one that wrote the change, runs it by hand. `/code-review high --comment <PR#>` is a second
   opinion, and `/code-review ultra` the deep cloud review, which only a person starts and which is billed. Reviews
   run locally, so the repo needs no token secret. The reviewer gets the diff, not the author's summary. A finding
   counts only once the author has checked it: reproduced it, or read the line and agreed. A confirmed finding is
   fixed and pinned with a check; a refuted one gets a reply that says why.
3. **A person, by lane.** The lane is set by what the change touches, never by a score.

| lane | touches | merges when |
|---|---|---|
| open | wording, a skill's body, a test, a new check, an isolated script change | checks pass and a review of the last push has every finding answered: an agent may merge it |
| evidence | a skill's `description` or `when_to_use` (it changes when the skill loads), a shared script such as `lessonlib.py` | as open, and `refactor-gate.py` exits 0 for that skill |
| closed | anything that publishes (`index.html` and `assets/`, which GitHub Pages serves from `main`; a tag or release), hooks, `settings.hooks.example.json`, `install.sh`, `.github/workflows/`, or a deletion | the owner merges it, whatever passed |

A change in two lanes takes the stricter one. Pushes to `main` are blocked by a hook, so every change arrives as a pull
request.
