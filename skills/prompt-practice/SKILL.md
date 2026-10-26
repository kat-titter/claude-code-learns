---
name: prompt-practice
description: Turn every prompt into a great one, automatically - the person's own (short, dictated, typo'd or abstract) and the ones Claude writes for others (subagent and session briefs, scheduled tasks, system prompts, image, music and voice generator prompts). Rewrites a prompt into a brief with its outcome, deliverable, context, the field's words and grammar, the prior work to build on and a check that can fail, following Anthropic's prompting guidance (clear and direct, the why, examples, structure, positive framing). Use when a request is short, dictated or vague; when writing any brief or prompt for another agent or model; when someone says "rewrite / improve / fix my prompt", "make this a better prompt", "write the brief", "what should I ask?". A hook adds a one-line nudge to dictated or terse prompts.
when_to_use: On a short, dictated, typo'd or abstract request before the first tool call; before sending a subagent prompt, a session brief, a scheduled task or a workflow; when writing a system prompt or an LLM call in code; when writing an image, music or voice generator prompt; when a session has needed two corrections on the same point; when asked to rewrite or improve a prompt.
---

# Prompt practice

A prompt is a brief for a capable colleague who just walked in: they know their craft and nothing of this project.
The work is the same in both directions. An incoming prompt gets rewritten, silently, into the brief it implies; an
outgoing prompt is written as that brief from the start. The gist itself is read as work-practice §1 says, and the
words follow field-vocabulary; this skill turns both into a prompt.

## 1. Rewrite an incoming prompt into its brief

Before the first tool call, fill six slots from the prompt and from what is already known:

| Slot | What it holds | Where it comes from |
|---|---|---|
| Outcome | what exists when this is done, and the direction the work is heading after it | the prompt, the session so far |
| Deliverable | the artifact (file, page, commit, answer, render) and who reads or uses it | the prompt, the project's habits |
| Context | what the person already has and decided | memory, project notes and PROGRESS files, sibling sessions' notes, `git log` |
| Words | the field's terms and grammar; a dictated slip becomes the term it aimed at | field-vocabulary, the project's glossary |
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
  the combinations are countable and any output traces back to its parts (431 subject sets x 6 orders x 28 moods x
  18 lights = 1,303,344 prompts, design-practice).

## 4. Build on others' work

- **Search before writing a prompt from zero**: the person's earlier prompts and briefs that worked (PROGRESS files,
  session notes, transcripts), the tool's own documentation and examples, the field's published prompts and methods.
- **Name the prior work in the brief**, by path or link, so the reader extends it rather than restarting.
- **After two corrections on the same point, rewrite the prompt** with what was learned and start clean; a fresh
  context with a better brief beats a long one carrying failed attempts (Claude Code best practices).

## 5. Automation

`scripts/prompt-nudge.py` runs on every prompt (a `UserPromptSubmit` hook). When the prompt reads as dictated or terse
(it starts in lowercase or ends without punctuation, 3 to 300 words), it adds one line of context asking for the
silent rewrite of §1; otherwise it stays quiet, and it always lets the prompt through. Install it next to any other
`UserPromptSubmit` hook in `~/.claude/settings.json`:

```json
{"type": "command", "command": "python3 ~/.claude/skills/prompt-practice/scripts/prompt-nudge.py"}
```

The nudge costs about 80 tokens on the prompts it fires on; this skill's body loads only when a brief or generator
prompt is being written, or when asked.

## Provenance

2026-10-26, the author: "skill: automate great prompting. consider edit/rewrite my prompts, context, understand the gist,
follow best practices, use domain vernacular/words/grammar, build off of others work". Sources read that day:
platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices and
code.claude.com/docs/en/best-practices. No existing prompting skill turned up in the skills catalog search.
