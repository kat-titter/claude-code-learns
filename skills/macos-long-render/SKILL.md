---
name: macos-long-render
description: Wrap long-running local jobs on macOS (video/ffmpeg renders, model training, multi-hour GPU/MPS or batch jobs) in caffeinate so the Mac can't sleep or idle-throttle them mid-run. Also use to diagnose a local job that ran far slower than estimated or crawled overnight.
when_to_use: Before kicking off any unattended macOS compute expected to run more than ~1-2 hours, and when investigating why a render/training/batch job took far longer than its ETA (to tell sleep/idle-throttle from thermal throttling).
---

## Wrap long unattended jobs in `caffeinate`

Any local job that runs unattended for more than ~1–2 hours on a Mac **must** be
wrapped in `caffeinate`, or macOS will sleep / idle-throttle the process —
especially overnight — and it crawls to a near-halt.

```bash
caffeinate -dimsu python3 long_job.py
```
Flags: `-d` display, `-i` idle, `-m` disk, `-s` sleep-while-on-charger, `-u` mark
user active. Also keep it **plugged in** and the **lid open**.

For a backgrounded long job:
```bash
caffeinate -dimsu nohup python3 long_job.py > job.log 2>&1 &
```

A ready wrapper is bundled: `${CLAUDE_SKILL_DIR}/scripts/caffeinate-render.sh -- <your command>`.

## Diagnose: sleep/idle-throttle vs thermal

When a job took much longer than expected, pull the *cumulative* time-per-iteration
across the whole run, then reason about the *instantaneous* rate per window
(cumulative averages hide cliffs).

- **Sleep / idle-throttle** → speed is steady for hours, then a **sudden cliff**,
  and it happens **overnight / while unattended**. Compute was fine; the *machine*
  idled out. Fix = `caffeinate`.
  - Real example (Apple M5, Real-ESRGAN render): held **~4 s/frame for 91%** of
    frames, then the last 9% ran at **~145 s/frame** — a 36× drop, overnight only.
    True compute time was ~6.7 h; wall-clock ballooned to **28.6 h**.
- **Thermal throttling** → a **gradual** climb in time-per-iteration over the run
  as the chip heats up. Not a cliff. Mitigation = better cooling / lower load,
  not caffeinate.

**Takeaway:** don't conclude "this hardware is slow" from a long wall-clock until
you've ruled out sleep/idle. The fix is almost always `caffeinate`.

## Estimating ETAs

A few-iteration cold benchmark *underestimates* a multi-hour job. Re-measure the
rate after it's been running a while (steady state) before quoting an ETA, and
state the assumption explicitly ("~Xs/iter *if it holds*").
