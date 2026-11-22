---
name: token-budget
description: Estimates what a build will cost in tokens, money and agent time, and which parts can run on a cheaper model or lower effort - work packages from a PRD, calibration on the account's own transcripts, three estimates, every downgrade challenged, contexts kept short.
when_to_use: Before a multi-session build or large workflow; on "how many tokens", "how much will this cost", "which parts can use Sonnet or Haiku", "token efficient" or "spending too much".
---

# Token budget

Tokens buy work, and most of the bill is re-reading: every call re-reads the whole context. So a budget is
measured before it is planned (§1), the work is cut into packages with a check each (§2), estimated three ways
(§3), challenged where it goes cheaper (§4), routed by the check that exists (§5), and run with short contexts (§6).

## Gotchas

- **Re-reading is the bill, not writing.** One account's last 44 sessions (2026-09-28 to 10-28) re-read 19.4B cached
  tokens for 61M output, 316 to 1 and about 60% of list cost. Sonnet 5.5 cache reads cost the same $0.20/M as Opus
  5.5, so a model switch leaves the largest line untouched; shorter contexts cut it.
- **An estimate that assumes small contexts is optimistic until the sessions hand off.** The same sessions re-read a
  median 458k per call (quartiles 282k to 673k). Plan on 1.5 to 2x a table that assumes 75 to 110k, or enforce §6.1.
- **A project word matches every transcript** when it sits in memory or the system prompt (all 50 sessions matched
  "a DJ tool"): filter by folder or first message, as `usage.py --match` does.
- **A cheaper model facing a red check loosens the check.** Thresholds, oracles and state-holding cores stay with the
  top model; the cheaper one may not edit them (§5).
- **The Workflow task's output file wraps the return** in `{"summary", "agentCount", "logs", "result"}`: read `["result"]`.

## 1. Measure where the tokens go

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/usage.py --calls`: per session the calls, output,
cache writes, cache reads, hours and list cost, then the median context per call and the share beyond a cap.
`--session ID` splits one session by task, the unit to scale from (a DJ tool, 2026-10-28: one verified engine change
with before/after renders and a doc took about 770 calls, 0.85M output and 230M re-read, about $80, $46 of it
re-reading). Prices come from the claude-api skill's table, read in the session; plan limits from `get_usage` (a weekly
limit at 100% means extra usage: every token is billed).

## 2. Break the work into packages, each with its check

Twelve to twenty packages, each with its deliverable, size (lines new and ported), dependencies, the oracle that
proves it done (a test, byte identity, a manifest, a human judge), the human gate and the main risk. Build the
oracle before the work: a tolerance table, a frozen corpus, a seeded manifest harness. It is what lets a cheaper
model do the rest (§5).

## 3. Estimate three ways, then reconcile

Bottom-up (lines to calls to calls x context), analogy (multiples of the unit measured in §1) and risk-first (the
rework rounds where a human judges or an output must match an old one). Two plans per package: the top model
everywhere, and routed. Take the median where the lenses agree within 2x, else the better-argued one, and say why.
Template: `references/estimate-workflow.js` (read it, fill its args, run it with the Workflow tool: 8 agents; the
a DJ tool run used 777k tokens and 13 minutes).

## 4. Challenge every downgrade

One critic tries to refute each cheaper routing against the quality bar and prices the rework; one completeness
critic lists what the plan leaves out (test data, CI, platforms, signing, hosting, docs, human review hours,
coordination, context resets). Apply or reject each with one line. a DJ tool, 2026-10-28: 37 challenges moved four
packages back to Opus and added seven; the routed plan still came to 38% of the top-model plan.

## 5. Route by the check that exists

| the work | runs on |
|---|---|
| a wrong call silently changes the output or leaks data; thresholds, oracles, state-holding cores | top model, high or xhigh |
| an exact oracle checks every result (byte identity, tests, manifest equality) | Sonnet high; escalate to the top model only when the check fails |
| mechanical edits under a check, docs, summaries | Sonnet medium |
| extending a deterministic list that a stronger model then judges | Haiku |

The calendar is set by what tokens cannot buy: the human's judging hours (a DJ tool: 15 to 25 hours of listening),
machines, accounts, signatures. List them beside the token total.

## 6. Run lean

Ranked by measured saving, on the sessions in the Gotchas:
1. **Hand off near 150k.** 69% of re-read tokens sat beyond 150k ($2,751 of $7,361 that month, the most a
   handoff saves). A short PROGRESS note with paths and results is the whole handoff; one fresh session per
   package and per human-judging round. A UserPromptSubmit hook, `scripts/context-nudge.py`, says so once at
   150k and again at each further 150k (`CONTEXT_NUDGE_AT` moves it).
2. **Trim the fixed load.** A session starts at a median 80k (tools, MCP servers, skills, system prompt), re-read on
   every call: turn off the plugins and connectors the work does not use. For a job that calls many tools, let the
   agent write a short script that calls them (tools as files it imports) instead of loading every tool definition
   into context: a reported cut from 150,000 to 2,000 tokens for the same task (X post on Anthropic's MCP write-up,
   2026-11-21, weekly X intake; the write-up itself not yet read here).
3. **Delegate the reading.** A subagent or workflow agent starts small and returns the conclusion (the DJ run's
   8 agents averaged 97k tokens each); briefs carry paths, not pasted contents.
4. **Fewer, fuller calls.** Independent tool calls in one message; long runs in the background, waited on once at
   completion; log tails, grep and outlines instead of whole files, DOM text over screenshots.
   Every token read is re-read on every later call.
5. **Effort and model per package.** Lower effort makes fewer, consolidated calls; Sonnet halves output and cache-write
   cost, not reads.
6. **Time in parallel.** Independent packages in parallel sessions on their own worktrees, renders and tests on spare
   cores and slots, and the human's judging batched so one sitting covers several results.

## Provenance

2026-10-28, a DJ tool: "PRD estimate build tokens and time w/ opus 5.5 ultracode (all), any parts could use lower effort
or model, how to break down? is there a skill for this? PRD > token efficient execution"; then "make a skill from this
method", and mid-build "ideas to increase time and token efficiency?". Numbers measured from the account's own
transcripts that day (`scripts/usage.py`); the estimate run is in the app's build plan.
