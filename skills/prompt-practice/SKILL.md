---
name: prompt-practice
description: Turns a short, dictated, typo'd or vague request into a clear brief before work starts, and writes strong prompts for others - subagent and session briefs, scheduled tasks, system prompts, and image, music or voice generator prompts. Use when a request is terse or dictated, when writing any brief or prompt, or when asked to "rewrite", "improve" or "fix my prompt".
when_to_use: Before the first tool call on a dictated or terse request; before sending a subagent prompt, session brief or workflow; when a session needed two corrections on the same point. A hook adds a one-line nudge to dictated prompts.
---

# Prompt practice

A prompt is a brief for a capable colleague who just walked in: they know their craft and nothing of this project.
The work is the same in both directions. An incoming prompt gets rewritten, silently, into the brief it implies; an
outgoing prompt is written as that brief from the start. A session brief ends with its stopping point: finish this
task, report, and list follow-ups as proposals the person picks from, rather than starting them. The gist is the core
intent plus the direction the work is heading, and the words are the ones practitioners use rather than terms coined
during the work; this skill turns both into a prompt.

## Gotchas

- Asking the person to confirm a rewritten brief costs a round trip: act on the likelier reading and say which in a few words.
- A subagent brief that omits the skills that apply: name them, since a running session may not have them loaded.
- A brief without a check that can fail: add the one fastest check before sending it.

## 1. Rewrite an incoming prompt into its brief

Before the first tool call, fill six slots from the prompt and from what is already known:

| Slot | What it holds | Where it comes from |
|---|---|---|
| Outcome | what exists when this is done, and the direction the work is heading after it | the prompt, the session so far |
| Deliverable | the artifact (file, page, commit, answer, render) and who reads or uses it | the prompt, the project's habits |
| Context | what the person already has and decided | memory, project notes and PROGRESS files, sibling sessions' notes, `git log` |
| Words | the field's terms and grammar; a dictated slip becomes the term it aimed at | the field's own docs and papers, the project's glossary |
| Prior work | what already does most of it | the person's own repos and sessions first, then docs, libraries, papers, published prompts |
| Check | the fastest test that can fail and shows it is done | tests, a script, a measurement, a screenshot to compare |

- **Fill gaps from the record before asking.** Memory, notes, files and the docs answer most open slots; a question to
  the person is for a decision only they can make, asked once, with the likely answer as the default.
- **Show the rewrite only when it changes the work**, as one line: "Reading this as: ...". Otherwise the brief stays
  internal and the reply shows the result.
- **A rewrite widens toward the person's direction**, not past it: it adds the follow-on the outcome needs (the other
  repos, the mirror, the index row) and names each addition so it is easy to drop.

Example (2026-10-26). In: "best practices: automatic worktreees". Brief: outcome, best practices for automatic git
worktrees in Claude Code and how this setup compares; deliverable, a short cited answer with fixes offered; context,
desktop app, many repos, a skills folder edited by parallel sessions; words, worktree, `.worktreeinclude`, saved
environment; prior work, the Claude Code worktree docs; check, each repo's ignore rule and worktree list measured.
The brief surfaced what the words did not: the collision that prompted the question was in a folder outside git.

## 2. Write a prompt for another agent or model

From Anthropic's prompting guidance and the Claude Code best practices (both read 2026-10-26; links in Provenance):
- **Colleague test.** Someone with no context on the task could follow it. State the goal, what is ruled out, the
  files or sources to read, the scope, and what done looks like; the reader sees only the prompt.
- **The why beside each instruction.** A reason lets the reader generalize: "read aloud by a text-to-speech engine, so
  write out symbols" carries further than a bare rule.
- **Say what to do.** "Write flowing prose paragraphs" steers better than a ban on markdown; name the target shape.
- **Specific over general.** Point at the file, the scenario, the pattern to copy (an existing widget as the model),
  the symptom with its likely location and what fixed looks like.
- **A check the reader can run, and evidence back.** Tests, a build, a screenshot compared to a reference; ask for the
  command and its output rather than a claim of success.
- **Structure for long inputs.** Documents first, the question last; XML tags to separate instructions, context,
  examples and inputs; three to five varied examples in `<example>` tags when format matters.
- **Reviews get the work, not the conclusion.** A reviewer sees the diff and the criteria, and flags only gaps
  against them, so its findings stay worth acting on.

A template for briefs and system prompts, trimmed to the slots that apply:

```
<goal>What exists when done, and why it matters.</goal>
<context>What is known and decided; files and sources to read; what is ruled out.</context>
<build_on>The existing work to extend, by path or link.</build_on>
<constraints>Scope, the field's words, taste, limits of time or cost.</constraints>
<done>The check that can fail, and the evidence to return.</done>
```

## 3. Prompts for generator models

Image, music and voice models read a different grammar from a chat model.
- **Their own vocabulary.** Subject, medium, light, lens and style terms (or the model's parameters and style codes)
  carry the image; instructions and reasons are noise to them.
- **Start from a prompt that worked.** Keep each good prompt beside its output (a render, a cover, a take) and change
  one element at a time, so the effect of each change is visible.
- **A prompt grammar is data.** When prompts are generated, keep the parts as lists and the rule that joins them, so
  the combinations are countable and any output traces back to its parts (in one generative series, 431 subject sets x
  6 orders x 28 moods x 18 lights = 1,303,344 prompts).

## 4. Build on others' work

- **Search before writing a prompt from zero**: the person's earlier prompts and briefs that worked (PROGRESS files,
  session notes, transcripts), the tool's own documentation and examples, the field's published prompts and methods.
- **Name the prior work in the brief**, by path or link, so the reader extends it rather than restarting.
- **After two corrections on the same point, rewrite the prompt** with what was learned and start clean; a fresh
  context with a better brief beats a long one carrying failed attempts (Claude Code best practices).

## 5. Automation

`${CLAUDE_SKILL_DIR}/scripts/prompt-nudge.py` runs on every prompt (a `UserPromptSubmit` hook). When the prompt reads as dictated or terse
(it starts in lowercase or ends without punctuation, 3 to 300 words), it adds one line of context asking for the
silent rewrite of §1; otherwise it stays quiet, and it always lets the prompt through. Install it next to any other
`UserPromptSubmit` hook in `~/.claude/settings.json`:

```json
{"type": "command", "command": "python3 ~/.claude/skills/prompt-practice/scripts/prompt-nudge.py"}
```

The nudge is one line of about 200 characters (about 50 tokens) on the prompts it fires on; this skill's body loads only when a brief or generator
prompt is being written, or when asked.

## Provenance

2026-10-26, the author: "skill: automate great prompting. consider edit/rewrite my prompts, context, understand the gist,
follow best practices, use domain vernacular/words/grammar, build off of others work". Sources read that day:
platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices and
code.claude.com/docs/en/best-practices. No existing prompting skill turned up in the skills catalog search.
