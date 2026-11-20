---
name: debug-practice
description: Finds and fixes bugs for good - reproduce first, shrink to the smallest failing case, test one hypothesis at a time, read the artifact rather than the job's word, fix the cause and pin it with a test. Use when something is broken, wrong, flaky or silent, or when someone says "debug", "why is this failing", "it worked yesterday" or "it says done but nothing changed".
when_to_use: Before changing code to fix a reported problem; when a fix did not take; when a result is off by a constant (a beat, a pixel, a factor of two).
---

# Debug practice

A bug is found when you can make it happen on purpose, and fixed when a check that failed now passes and stays passing.

## Gotchas

- "Done" in the log while the output is unchanged: read the artifact (exit code, timestamp, diff), not the job's word.
- A fix in the code while the running server, page or cache still serves the old build: restart or reload, then re-measure.
- A process stuck at 0% CPU is usually waiting on input, not working: check what it reads (a hook script imported for its regexes sat on stdin, 2026-10-26).
- Off by a constant (a beat, a pixel, a factor of two): look first for a unit, frame-rate or index mismatch.

## 1. See it fail

- **Reproduce first, on the smallest case**: one transition instead of the mix, one figure instead of the page, one input
  instead of the batch. A bug you can trigger in seconds gets fixed in minutes.
- **Measure what the person perceives**, not a proxy: per-band energy at the handover, not full-band loudness; the
  rendered bar, not the recipe that claims it. (A DJ-set engine, 2026-10-14: a 12 dB highs cliff hid under a full-band
  loudness check; a mute the recipe reported never reached the audio, because it lived in a branch the variant never
  entered.) Pick and measure a point at the width of the action it anchors: a voice gate placed on the quietest 10 ms
  read 12.7 dB loud across its own 150 ms ramp (2026-10-27).
- **Trust the artifact, not the job's word**: check the exit code of every step, the output's timestamp and a diff of
  its content. (2026-10-14: a background job "completed (exit 0)" while its edit script had died on a SyntaxError, so
  the renders used old settings.)

## 2. Narrow it down

- **One hypothesis, one test that could prove it wrong**, written down before running; change one thing at a time.
- **Bisect what used to work**: `git bisect` over commits, or halve the inputs, flags or config until the change that
  breaks it stands alone.
- **An error by a constant points at an anchor**: off by one beat, one pixel, a factor of two or a unit means a start
  index, an origin or a unit is wrong. (2026-10-14: a grid fit anchored bar 0 at 0.0 despite a pickup bar, so bar
  lines sat one or three beats off; a ramp helper took a length but was called with end indices.)
- **Stale beats wrong**: when a change seems to have no effect, suspect a cache (the browser's, a build's, a "render
  if stale" step) before the code; serve regenerated pages with `Cache-Control: no-store`.

## 3. Fix it for good

- **Fix the cause, not the symptom**, then add the failing case as a test or a check that would have caught it.
- **Search for siblings**: grep for the same pattern elsewhere (every caller of the helper, every path with the same
  default) and fix them in the same pass. (2026-10-14: an explicit setting lost to a mode default twice, in two paths.)
- **Fail loudly next time**: a guard or an assertion where the bug slipped through silently (code-practice, "Fail
  loudly").
- **Write the lesson once**: one line in the project's notes or a skill, the symptom and the cause, so the next
  session finds it by the symptom.

## Related

code-practice (clean code and refactors), systems-practice (memory, logging, infrastructure), work-practice ("Rebuild
safely"), verify-animated-page (canvas and WebGL pages), beat-align-audio (audio timing).

## Provenance

2026-10-26: "computer skills: ... bug finding and debugging"; cases from the lessons inbox (2026-10-06 to 10-18).
