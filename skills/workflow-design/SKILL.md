---
name: workflow-design
description: Designs agent workflows as loops inside a graph - a check a program can fail in each node, a stop rule on every cycle, a named value on every arrow, code where code will do, failures sent back one unit at a time, a person only where a mistake cannot be undone. Use when writing a Workflow script, fanning out subagents or scheduling an agent, or on "loop", "graph", "fan-out", "orchestrate" or "approve only the last step".
when_to_use: Before a workflow script or fan-out; when a workflow is rerun whole, its verify step is an agent's opinion, the same workflow is drawn fresh, or proposals pile up unapplied.
---

# Workflow design

A loop makes one unit of work correct without a person. A graph decides which units exist, in what order, and where
a person signs off. Without the loop you read every output; without the graph you approve every step. Build the check
first, then the graph, then the step that writes each failure down as a rule. (After Hoodie, "Loops & Graphs", X,
2026-11-04.)

## Gotchas

- An agent's `pass: true` is an opinion. Put the command and its exit code in the schema and gate on the number in
  code: `checks.every(c => c.exit_code === 0)`.
- verify, fix, verify again, once, is not a loop. Bound it and say what happens after the last round.
- `parallel()` turns a dead agent into `null`. Count a null as a failure; "no errors" means nothing was reported.
- Rerunning a whole workflow rewrites the units that passed. Resume (`resumeFromRunId`) or send back the failing unit.
- A recurring workflow drawn fresh each time splits the work differently each run, so nothing it learns carries over.

## 1. The loop lives inside a node

- **A check a program can fail.** Rank the evidence: tests exit 0, output matches the schema, the diff stays inside
  the plan (strong); the cited source supports the claim, an independent path gets the same answer (medium); a
  reviewer agent approves (weak); "looks good", the model's confidence, no errors thrown (noise). A taste call is a
  check too, when the person makes it: their verdict is the test, and the rule it leaves is the next run's check.
- **Write the check before the task.** If no check exists, the first node builds one (a script, a fixture, a
  measurement), and the work waits for it.
- **Five things every cycle needs:** a test that says done, a round limit, a budget, memory of past attempts, and a
  person told when it stalls.
- **Open-ended discovery stops on dry rounds.** Count new findings per round, deduped against everything seen,
  rejected ones included, and stop after two rounds with nothing new.

## 2. The graph lives between nodes

- **Name the value on every arrow.** If no value travels from A to B, they run at the same time. Order copied from
  the sentence ("research, then check the repo, then price it") is not order the work needs. In a script that means
  `pipeline()` by default and a barrier only where the next step needs the full set (dedupe, rank, compare).
- **A node fits in four lines:** job, in, out, fails as. The schema is the contract, so the model, prompt or tool can
  change without breaking what reads it.
- **Model or code.** A node that judges, decides, assesses or summarizes needs a model, sized to the job (small for
  extraction, strong for synthesis). Merging, deduping, sorting, counting and joining have one right answer: plain
  code in the script.
- **Four shapes cover most work:** a chain (each step reads the last), a fan-out and join (research, reviews,
  audits), a router (a cheap classifier sends easy work down a short path), a bounded cycle.
- **Parallel workers get separate contexts.** Four reviewers who see each other's comments give one review four times.

## 3. Failure: send back the unit, not the batch

| what failed | do |
|---|---|
| a tool or network blip | retry |
| a model or source is down | fall back |
| an optional branch | skip, and log what was skipped |
| a unit's check | repair that unit only |
| three repairs | escalate: the plan is wrong |
| budget or permission | stop and tell the person |

Send back one unit with the failing check, its output and a scope line ("these files only"). Without the scope line
a one-line fix turns into a four-file diff. When a fix passes, write the cause as a rule for whoever splits the work
next time (capture-lesson routes it): this is the step that makes the next run better, and most setups skip it.

## 4. The gate: by what a mistake costs to undo

| lane | what | gate |
|---|---|---|
| open | one revert undoes it: a copy fix, a new test, an isolated function, a wording line in a skill kept in git | ships on its check |
| evidence | shared code, a schema, a skill description (it changes when the skill loads) | hard evidence first |
| closed | migrations, deletion, production writes, payments, publishing, hooks and settings | a person, whatever the score |

No confidence thresholds: confidence is the one number the model makes about itself, and a threshold is a number
someone lowers on a busy day. A lane has no number to lower. Ask the person once per lane, not once per item.

## 5. Who draws the graph

| the job runs | a mistake is | so |
|---|---|---|
| once | cheap to undo | the model writes the workflow; throw it away after |
| once | costly | the model drafts the plan; the person reads only the plan |
| again and again | cheap | save the graph (`~/.claude/workflows/<name>.js`, inputs as `args`) and let it ship |
| again and again | costly | save the graph; the person signs the last step |

The second time you draw the same shape, save it. A saved graph keeps its splits, so a rule learned in one run
applies to the next.

## Template

`references/check-repair.js`: units fan out (each owns its files), each is built, checked by exit code and repaired
alone up to a round limit; units that never pass escalate; every repair's cause comes back as a candidate rule. Copy
it to `~/.claude/workflows/check-repair.js` to call it by name with `args`.
