---
name: github-practice
description: Uses git and GitHub well - small commits with a why, a branch and pull request per change, secrets and binaries kept out of history, pushes that never clobber shared work, a README that says what the repo is, and private-to-public done as an audit. Use when committing, branching, pushing, opening a PR, writing a README or .gitignore, or making a repo or Pages site public.
when_to_use: Before any commit, push or PR; when a README feels too long or wordy; before changing a repo's visibility; when a push is rejected or a force-push is on the table (a hook blocks force-pushes and pushes to main).
---

# GitHub practice

A repo shows the world two things: its history and its front page. History is cheap to write and expensive to take
back, because it is cloned and forked; the front page is what a visitor reads before anything else. So the sections
run in the order a repo is built: write each commit well (1), share it without clobbering anyone (2), keep private
things out from the first commit (3), give the repo a front page (4), and go public only once all of that is checked
(5), which reuses every step before it.

## Gotchas

- A README that grows into the docs ("too long, wordy"): one screen, detail in the linked doc (§4).
- Pushes to main or master and every force-push are blocked by the push-guard hook: hand the person the exact command and why (§2).
- `gh pr merge --auto` merges at once when the repo has auto-merge off and no required checks: read the PR's checks on its latest commit first, or turn on auto-merge in the repo settings (claude-code-learns #9, 2026-11-20: it merged before CI finished on the last two commits; that run then passed).
- Sessions sharing one checkout share one git index: hunks one session stages ride into the next session's `git commit`
  (essay, 2026-11-19: a hero-table change landed inside another session's Figure 12 commit 557bd75). For whole
  files, `git commit -- <paths>` skips the index; for hunks of a file two sessions edit, give each session its own worktree.
- Dates, collaborator names and personal details left in a repo going public ("remove the date... don't name collaborating institutions"): audit before the flip (§5).
- PDFs, renders and images committed "just this once": keep binaries out of history and share them from local storage (§3).
- A push to a branch whose PR was merged in the meantime opens nothing and runs no CI, so it looks like waiting: check `gh pr view <n> --json state` before pushing to a PR's branch, and open a new PR when it says MERGED (claude-code-learns, 2026-11-06) (§2).
- `git add -A` in a checkout other sessions share sweeps their edits into your commit: check `git status --short`, stage paths by name (§2).
- A shared checkout can be mid-merge for another session (`MERGE_HEAD` present, `UU` files): leave its merge to its owner, wait until it closes, then merge yours (a DJ tool main, 2026-10-27: a voice-breath merge sat open with CHANGELOG.md unresolved; resolving it would have committed another session's half-done work) (§2).

- **Parallel sessions in one checkout merge as they go.** Each session commits its own work on its branch and merges it into main
  as soon as it is checked, or commits straight in main; none leaves live edits uncommitted in main's working tree while its branch
  holds a copy. Otherwise every merge collides and has to be untangled by counting which branch lines are already live (a DJ tool,
  2026-11-05: seven branches, 1,100 dirty files; "merge everything that can/should be").

## 1. Commits: each entry readable on its own

- **One change per commit**, so it can be read, reverted or cherry-picked alone. A fix and a refactor are two commits.
- **A title of 50 characters or less, a blank line, then the why** (git's own guidance: `git help commit`, Discussion).
  The title says what changed, in the imperative, led by the area it touches when the repo has several
  ("capture-lesson: validate in proportion, grep first"); the body says why and how it was checked.
- **Read the staged diff before committing** (`git diff --staged`) and stage paths by name; `git add -A` sweeps in
  scratch files, renders and secrets (section 3 says which).
- **Commit at working points**: each commit builds and runs, so a revert or `git bisect` lands on something usable.
- **A commit carries the change and everything that describes it**, so every file in the repo tells the same story: before
  committing, grep the repo for the changed thing's name, its numbers and counts, and update the README, explainer
  page, index and dated figures that mention them (2026-10-26: a skill gained a validation step; the explainer's
  loop and checklist, its footprint bars and the example index's skill count followed in one commit).
- **Undo shared history with a new commit** (`git revert <sha>`); `reset` and `commit --amend` touch only commits
  nobody else has. A commit lost to a reset stays in `git reflog` for 30 days by default (`gc.reflogExpireUnreachable`;
  `git help config`), so look there before redoing work.
- **Tag what you ship**: an annotated tag per release or published version (`git tag -a v1.0 -m "..."`); release
  assets such as a deck's PDF hang off the tag, and links meant to stay put point at the tag rather than main.

## 2. Sharing: branches, pull requests, pushes

A good commit still has to reach the shared line without breaking it or overwriting someone else's.

- **A branch per change**, off the default branch; the default branch stays working and deployable.
- **Small PRs that say what changed, why, and how it was checked** (commands run, links; screenshots only for visual
  changes), the same why the commit body gives. A PR one reviewer can read in one sitting gets reviewed.
- **Bring the branch up to date before pushing**, resolve conflicts locally, and read CI before asking for review.
- **Shared history is rewritten only with the owner's yes**, and pushed with `--force-with-lease`, which refuses to
  overwrite a newer commit someone else pushed (section 5, step 5, for the fresh-clone case).
- **Close the loop on a publishing push**: after a GitHub Pages push, wait for the build
  (`gh api repos/<o>/<r>/pages/builds/latest`) and load the live URL (html-slide-deck, "Publish and confirm").
- **Use `gh` for GitHub operations** (PRs, issues, checks, visibility), so each step is scriptable and visible.
- **Two sessions in one checkout each commit only their own paths**: another session's uncommitted edit is its work in
  progress, so stage by name, and give parallel writers their own worktree (`git worktree add ../<repo>-<task> -b <task>`).
  (2026-10-26: a skills audit found 25 paths of other sessions' edits uncommitted and, with the owner's yes, committed
  them as one labelled snapshot before its own per-skill commits.)
- **A session that writes code starts in its own worktree.** When the app cannot make one, its first step is
  `git worktree add ../<repo>-<task> -b <task>` before any edit, and the brief says so (a DJ tool, 2026-10-27: a proposed
  session landed in the shared checkout; then "new session should start w/ worktree? best practices").

## 3. What stays out of history

Every push copies history to places you cannot clean later, so what is private stays out from commit one.

- **Commit as the host's no-reply identity, set once per machine** (`git config --global user.name <user>`,
  `user.email <id>+<user>@users.noreply.github.com`), with no repo-level override in `.git/config`, which would win.
  A Mac with no global identity commits as `user@<hostname>` (`.local`, `.lan`).
- **Secrets, tokens, personal emails, home paths and private URLs live outside the repo**: read them from the
  environment or an ignored config file. A secret that reached a pushed commit gets rotated first; rotation may be
  all a credential needs (GitHub docs, "Removing sensitive data").
- **Binaries, renders, PDFs and datasets** stay out, with a `.gitignore` from the first commit; ship them as release
  assets or keep them local, and commit the source that rebuilds them.
- **A Pages site's pictures: masters out, web copies in**, by the rule in code-practice.
- **Fixing the head leaves history as it was**: old file versions keep the email they once held, and every commit
  keeps its author. What slipped in takes the rewrite in section 5.

## 4. The front page: README, About box, root

History is what the repo keeps; the front page is what a visitor sees first, and it should answer their questions in
one screen.

- **The README answers GitHub's five questions**: what the project does, why it is useful, how to get started, where
  to get help, who maintains it (GitHub docs, "About READMEs"). In one screen: a line of what it does, the live link,
  install and first use in a code block, a small file tree, the license. Longer documentation lives in `docs/`, a
  wiki or an explainer page the README links. (A skill-library README went from 124 lines to 58 and read better,
  2026-10-25.)
- **Written for a reader with no background in the tool or the field**: a short example of the behaviour first, a
  four-row glossary of the platform's words, plain idea before the technical term (in brackets), depth in `<details>`
  folds so the first screen stays short. A project built on a platform says which current practices it uses, with
  sources, and what it adds to each, in one table (claude-code-learns, 2026-10-28: "legible to someone with no claude
  code or neuro experience"; "clear how this leverages current best practices, customizes/builds on them").
- **Relative links** (`docs/setup.md`, `./LICENSE`) so they work in clones and on every branch; keep each link's text
  on one line, or the link breaks.
- **Diagrams in Mermaid**, which GitHub renders: short labels, top to bottom so the README column shows them full
  size, parsed before pushing (capture-lesson, "Share it", has the keywords that break it). When the diagram needs a
  person, a brand or exact layout, draw it as SVG text from a script, light and dark through `<picture>` with
  `prefers-color-scheme` sources, and keep a Mermaid copy in `AGENTS.md` for agents (claude-code-learns, 2026-11-05).
- **One publisher per site, and the publish checks GitHub first.** When a script exports a private branch to a public
  repo, every publish overwrites what was merged on GitHub since the last one. So exactly one session publishes, and
  the script fails unless each GitHub-made commit G (parent P) is already contained: `git merge-tree --write-tree
  --merge-base=P <candidate> G` must return the candidate's own tree; that check allows later edits on top (an essay,
  2026-11-19: three sessions published within an hour, and one export rolled back a merged PR).
- **A data or analysis repo's README draws its code flow**: raw data with its checksum, each script as a node, the
  results files, the figures they feed, counts on the edges, in the project's own palette via `classDef`, so a reader
  traces any number to the script that makes it (an essay, 2026-11-19: "code should have great readme with
  code flow shown (mermaid or similar), style that matches essay").
- **The About box finishes the page**: a name that says what it is, lowercase with hyphens (`overdose-watch`), a
  one-line description, the Pages or demo URL as homepage, a few topics (`gh repo edit -d "..." -h <url> --add-topic <t>`).
- **The root shows what runs today**, the same story as the README's file tree: README, LICENSE, `.gitignore`, the
  source; experiments and archives sit in their own folder (code-practice).

## 5. Private to public

Private is the default. Going public shows the history (section 3) and the front page (section 4) to everyone at
once, so the flip comes last, after each is checked:

1. **Audit the whole history, not the head**, for what section 3 keeps out. Count identities
   (`git log --all --format='%an <%ae> | %cn <%ce>' | sort | uniq -c`), grep `git log -p --all` for emails, home
   paths, scratch paths, tokens and private URLs, and read the Actions logs: workflow history becomes visible to
   everyone (GitHub docs, "Setting repository visibility").
2. **Decide with the owner what stays private** (raw notes, verdicts, a blind-test reveal), and finish the front page:
   a LICENSE and the README of section 4.
3. **Rewrite what the audit found, in a fresh clone**, with `git filter-repo` (2.47 or later): `--mailmap` maps each
   identity to the no-reply one, `--replace-text` swaps literals, `--invert-paths --path` drops files.
4. **Verify the rewrite**: the identity count shows one line; `git rev-parse HEAD^{tree}` matches the old head when the
   files should not change; each commit's tree, dates and message match
   (`git log --format='%T %ad %cd %s' --date=raw` on both sides, diffed).
5. **Force-push with the owner's yes and an explicit lease**, `--force-with-lease=main:<old sha>`: a fresh clone has no
   tracking ref, so a bare lease has nothing to compare against. Re-point other clones with `git reset --keep origin/main`.
6. **Flip, then check live**: `gh repo edit --visibility public --accept-visibility-change-consequences`; read the log
   as GitHub serves it (`gh api repos/<owner>/<repo>/commits`) and load the Pages URL (section 2).

Why the rewrite comes before the first public day (GitHub docs, retrieved 2026-10-26): after a rewrite, old commits
stay reachable "directly via their SHA-1 hashes in cached views", through pull requests that reference them, and in
forks, and only GitHub Support clears those, only for sensitive data. The flip has its own costs: going public erases
stars and watchers and publishes Actions history; going private on GitHub Free unpublishes a Pages site, and public
forks stay public.

Cases: a DJ-set repo went public 2026-10-17 with a personal email or hostname on all 240 commits and a private
playlist URL, and went back to private until the rewrite (step 1 caught it). A skill-library repo, public from day
one, had 16 of 18 commits under hostnames or a Gmail (2026-10-26); steps 3 to 6 left the head tree hash and the live
page unchanged.

## Provenance

2026-10-25: "github best practices", in one note on how work should run (its siblings live in work-practice).
2026-10-26: "github best practices: private > public repo, readmes, commits, style", after the skill-library rewrite,
with GitHub's docs on visibility, READMEs and removing sensitive data read that day; then "skill elements should be
clearly connected, polish": the sections reordered into one chain (commit, share, keep out, front page, go public).
Cases: a DJ-set repo's publish audit (2026-10-17), the skill-library rewrite (2026-10-26), the deck publishes in
html-slide-deck.
2026-10-26, mid-audit: "github, version control best practices": undo and recover (git's own reflog defaults), tags for
what ships, sessions sharing a checkout; and the push-guard hook (`scripts/push-guard.py`, 17 cases in `--test`).
