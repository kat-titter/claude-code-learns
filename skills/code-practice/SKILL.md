---
name: code-practice
description: Keeps code clean and repos organized - one home per helper, one path per setting, behaviour-preserving refactors and a layout a newcomer reads at a glance. Use when writing, reviewing or refactoring code, adding a script, or when someone says "clean code", "avoid redundant code", "organize the repo", "dedupe" or "too many scripts".
when_to_use: Before adding a file or function; when a function is copied into a second file; after an A/B comparison picks a winner; when a folder fills with v2, v3 and _old.
---

# Code practice

A reader should find each thing once, in the place its name suggests, follow each function in one read, and see at a
glance what runs today. Whether to build the thing at all, and how much structure it has earned, is a separate
question (a simplicity skill such as grug-brain, if you keep one).

## Gotchas

- The same helper pasted into a second script drifts apart silently: give it one home and import it (One home per helper).
- A refactor that reads as equivalent can still change output: run old and new on the same inputs and diff (Refactors that keep behaviour).
- An A/B winner left beside the loser as v2, v3, _old: delete or archive the loser once the comparison is decided (The live program).

## Design rules, read as code

A repo is a page someone reads, so the rules of good page design carry over. Each row has a check in
`scripts/code_audit.py` that can fail, except the last two, which the eye or a formatter keeps.

| page rule | code rule | check |
|---|---|---|
| One focal point per view | One job per function; the top reads as the recipe | `focus`: function ≤ 60 lines, file ≤ 500 |
| Say each fact once | One home per helper; one source for a shared page head | `once`: no 8-line block in two places |
| The point opens the page | The README says what the repo is, names its entry points, and every path it names exists | `front` |
| Erase chartjunk | No v2/_old/final files, no commented-out code; git keeps them | `clutter` |
| Negative space groups things | Folders by job; a top level that reads at a glance | `space`: ≤ 15 entries |
| Every figure has a caption | Every script opens with one line saying what it does | `legend` |
| Embedded media stays small | Binaries over 1 MB stay out of git (a release asset or local); a Pages site keeps web copies | `light` |
| One meaning per colour | One name per concept in every file (`width_px` everywhere, never `w` here, `width` there) | by eye |
| One left edge, one rhythm | One formatter and one naming style per language | formatter |

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/code_audit.py REPO [REPO ...] [--detail N]
```

It prints one row per repo, then each finding as file:line, and exits 1 on any. It reads only files git tracks.
Calibrated on ten public repos (2026-11-19): README links to file families (`results/e16`) and folders marked
"local only" pass, prose comments pass, and generated pages are judged at their builders. JS function length is
found by brace matching, so it is approximate; Python uses the AST.

- **Judge a generated page at its source.** A self-contained page built from one shared head carries copies by design;
  the head has one home in the builder (a docs folder built by `docs/build.py`). The audit traces each page to its
  builder (a `.src` sibling, a script that writes it, a README line, a "do not edit" header) and lists it.

## Clean code

- **Names say the job**: a function is a verb for what it does (`render_frame`, `fit_grid`), a value the thing it holds
  with its unit (`gap_px`, `duration_s`); a name that needs a comment gets renamed.
- **Small functions, one level of detail each**: the top reads as the recipe (load, fit, render, check), each step a
  call; a function past one screen or mixing levels splits.
- **A pure core, effects at the edges**: math and decisions take values and return values; files, GPUs, networks and
  clocks sit in thin wrappers around them, so the core tests on plain inputs.
- **Numbers come from data or a rule, not by hand.** A number in code is fit from data (a validation run, a measured
  file), computed from the inputs, or a named setting whose comment cites its source; a count set by hand for one run
  means a rule is missing ("render the next take until K pass", not "render 4"). (A render pipeline, 2026-10-28: "avoid
  hard code numbers", after a batch size was set to 4 by hand on three jobs to get two outputs past the checks.)
- **One path per decision, and the explicit call wins.** Each setting is decided in one function; mode defaults fill
  only what the caller left unset, and a test proves an explicit value survives every mode. (The same pipeline,
  2026-10-14: an explicit start offset was overridden by one mode's default, the second time an explicit call lost to
  a mode default.)
- **One entry point owns its settings.** A step called directly behaves as it does inside the pipeline, because the
  settings live in the function, not in the caller's environment. (The same pipeline, 2026-10-14: a step run by calling
  its script directly skipped two checks the full pipeline sets, and wrote to the wrong folder.)
- **Fail loudly**: a missing input, a crashed step or an impossible value raises with the value in the message;
  an old output is never a silent fallback.
- **Comments say why**, the code says what; dead code, commented-out blocks and unused flags go (git keeps them).

## Refactors that keep behaviour

- **Pin the behaviour first**: a golden output, a hash of the rendered file or a test on fixed random inputs, run
  before the change and after it; equal means done.
- **Refactor apart from features**: one refactor per commit, no behaviour change mixed in, so a diff reads as a move
  and a revert stays clean.
- **Move in small steps that each run**: extract, rename, inline, one at a time, with the pinned check after each;
  a big rewrite grows beside the old path and replaces it once the outputs match.
- **As fast as before, and reviewed**: time the script on both sides of a refactor and run a code review on the diff
  before the PR goes up; equal bytes, equal time and a clean review mean done. (An essay builder's 700-line `build()`
  split into steps, 2026-11-19: "code should be performant, pass code review"; 0.17 s before, 0.16 s after.)
- **Published results keep their exact behaviour**: scripts behind a shipped render or paper change only to import an
  identical helper.

## Review by three

Three reviewers with different opinions review each pull request apart, their consensus stands in for a person's
review, and only the taste calls reach the person. Agents judge; `scripts/review3.py` holds everything with one right
answer: the PR's facts, the 2-of-3 tally, the one GitHub review, the commit status and the merge gate.

- **Run it**: `review3.py prep OWNER/REPO N --repo-dir CLONE`, then do what it prints: the exact `Workflow` call,
  which names the `review-3.js` beside review3.py by its path and hands it review3.py's own path as `script` (one
  install path, `CLAUDE_CONFIG_DIR` included, no link to keep), then `review3.py ready RUN`. If the head was already reviewed, prep prints only the ready command. A link in
  `$CLAUDE_CONFIG_DIR/workflows/` only adds the name `review-3`.
- **Three schools, separate contexts**: grug (no to abstraction, the 80/20, integration tests), Ousterhout (deep
  modules, leakage, design it twice) and maintainability (the table above, starting from the audit delta). They
  disagree on purpose, on function length most of all. Each finds alone, at most 8 findings, then votes blind on the
  other two schools' findings without knowing who raised them.
- **Consensus is counted in code** (`review3_test.py` pins it, and runs the gate through a fake `gh`;
  `review-3.test.mjs` runs the workflow on stub agents): 2 of 3 agreeing is a finding to act on; 2 of 3 calling it
  important blocks; 1 of 3 is a taste call, listed and never blocking. Consensus rows from different reviewers in one
  file within 3 lines of each other, the same line included, merge into one row that names the others under "Also
  raised as" (one run cited one bug at `:82` and `:84`); one reviewer's own rows never merge, and a taste call stays
  its own row.
  A finding outside the diff, such as a doc the PR left stale, goes in the review body, not inline.
- **Built pages are judged at their script**: prep lists the pages `code_audit.py` traces to a builder in
  `generated.txt` and drops them from the diff the reviewers read. On a first run a 5k-line built page was most of
  the 814k tokens.
- **One review on the PR, event COMMENT**: verdict, a consensus table, a "Taste calls" table (reviewer, position, why,
  the other two), inline comments on consensus lines only, the audit delta folded. Reviewers never approve or block.
- **The gate lives on GitHub**: prep sets the `review-3` commit status to pending on the head; post sets success at 0
  blocking or failure otherwise, linked to the review. Require `review-3` on the default branch (strict off, admins
  not enforced) and the merge button waits for a review of the current head, while an owner can still override on
  purpose. A private repo on a free plan cannot require a check, but the status still shows. The lesson behind it: a
  PR was merged from the web page while its second review ran, and that review found 5 blockers; a gate only
  protects a merge that waits for it.
- **It starts itself**: `scripts/review3-hook.py` is a PostToolUse hook on Bash. After `gh pr create`, `gh pr ready`
  or a push, when the PR is open, not a draft, in a repo the gh user owns, and its head has no `review-3` status yet,
  it adds one line telling the session to review it; it reads that status, never the push output (`git push -q`
  prints nothing), and a pushed commit GitHub does not show as the head yet counts as unreviewed. On every other command it prints nothing (about 45 ms). Keep a PR in draft while pushing fixes;
  `gh pr ready` starts the review. The installer does not add it, because each review costs real tokens:

  ```json
  "PostToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "timeout": 15,
    "command": "python3 \"$HOME/.claude/skills/code-practice/scripts/review3-hook.py\"" }] }]
  ```
- **Ready is a gate a program can fail**: open, based on the default branch, no conflicts, the review covers the
  current head, 0 blocking, CI not failing or running. Other open PRs on the same files and uncommitted edits in
  worktrees print as warnings with a merge order. Then, on the person's word,
  `gh pr merge N --squash --match-head-commit SHA`.
- **Why this shape**: hosted review bots never approve, post inline plus a summary, and verify before posting; the
  noisiest tools catch the most and get read the least, so findings are capped and 1 of 3 never blocks; correlated
  judges fail together, so contexts stay separate and votes blind.

## One home per helper

- **The second copy is the signal.** When a function is needed in a second script, move it to a shared module and import
  it in both. (An image-generation repo, 2026-10: slerp, a Catmull-Rom spline and VAE encode/decode were each defined
  in six scripts; one small module serves them all.)
- **Look before adding a file.** Search for the function or script that already does the job (`grep -n "def name"`) and
  extend it; a new module is for a new job, not a second version of an old one. (Same repo: a new upscaler file nearly
  duplicated the loader inside the final render script.)
- **Share pure functions first.** Math and format helpers move safely; prove the move with the old and new versions on
  the same random inputs (`torch.allclose`, identical bytes).
- **A few documents that point at each other.** A project's writing lives in a small fixed set (about three), each with
  one job and each linking the others; new material goes into the one that owns it, and a retired doc's content is
  folded in, its file removed, its old link forwarded or left to 404. The README is only the repo's front page. (An art
  project, 2026-10-26: a project doc, a build guide and a white paper; the pitch kit became a section of the white
  paper. "max 3 docs, docs reference each other, avoid creating new docs".)

## The live program carries only the live path

- **Comparisons, strips and benchmarks live outside the program they judge**, in a small tool or a scratch folder.
  Once the verdict is in, delete the losing path; git keeps it. (A live generative-art server briefly kept its old
  latent walk and a comparison mode inside the server script.)
- **Flags are for people running it**, not for one past experiment.

## A layout that reads at a glance

- **Superseded experiments retire to an `archive/` folder** inside the area they came from, with a one-line note of
  what replaced them, so the top level shows only what runs today.
- **Names say the job** (`upscale.py`, `latent.py`), not the iteration (`v3`, `new`, `final2`); a version belongs in git.
- **The README's file table matches the tree**: every file it names exists, and every top-level file has a row.
- **Generated output, caches and models stay outside git** in ignored folders.
- **A Pages site's pictures: masters out, web copies in.** The page can serve only what the repo holds, so commit a
  WebP copy under 1 MB, as wide as its largest showing needs (twice its measured box on a 1440 px screen, or its
  printed box at 300 dpi) and never wider than the master. Keep the full-size master in a gitignored local folder,
  with a small script that remakes the copies, so the rule has one home. Measure the boxes in the browser: a 10 MB
  portrait was showing at 130 x 156 px. Git LFS is no way round it, since Pages does not serve LFS files. (An art
  project's Pages site, 2026-11-19: 43 MB of masters became 1.4 MB of copies.)

## Provenance

2026-11-19: "carry over learnings from great visual design to great code organization ... easy to read, well
organized, logical flow, minimal redundancy, one thing at a time"; the design-rules table and `code_audit.py`, and the
Pages pictures rule. 2026-10-25, on an art project's code folder: "repo should be organized, avoid redundant code".
2026-10-26: "skills: clean code, refactors, code organization"; renamed from code-organization the same day; cases
from the lessons inbox. 2026-11-21: review by three, `review3.py` and the `review-3` workflow; 2026-11-22:
the `review-3` commit status, the hook, near-twin merging and built pages left out.
