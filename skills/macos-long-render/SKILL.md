---
name: macos-long-render
description: Wraps long local jobs on macOS (ffmpeg renders, model training, multi-hour GPU/MPS or batch runs) in caffeinate so the Mac cannot sleep or idle-throttle them, and diagnoses a job that crawled. Use before starting unattended compute expected to run over an hour or two, or when a run took far longer than its ETA or slowed overnight.
when_to_use: Before any overnight or unattended render; when telling sleep or idle-throttling apart from thermal throttling or a busy machine.
---

## Gotchas

- A render that ran fine for hours crawls overnight (the last 9% at about 36 times slower): the Mac slept or idle-throttled; wrap it in caffeinate.
- Blaming thermals when the machine slept: read the power log first (Diagnose).

## Wrap long unattended jobs in `caffeinate`

Wrap any local job that runs unattended for more than ~1–2 hours on a Mac in
`caffeinate`; otherwise macOS can sleep or idle-throttle the process,
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

**Takeaway:** rule out sleep and idle before reading a long wall-clock as slow hardware.
The fix is almost always `caffeinate`.

## Diagnose: a shared, overloaded machine

When a job crawls while the Mac is awake, look at what else is running before blaming the job:
- `sysctl -n vm.loadavg` against `sysctl -n hw.ncpu`, and `sysctl vm.swapusage`. A load several times the core count
  or swap near full means the job is waiting (a deck build, 2026-10-19: load 35 on 10 cores, 13 GB swap; a 5-minute
  analysis took over an hour while another project ran a parallel batch).
- `ps -Ao pid,etime,pcpu,rss,command -r | head` shows who holds the CPU; a tiny RSS on a big job means it was swapped out.
- Give numeric jobs one BLAS thread on a shared machine (`OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  OMP_NUM_THREADS=1`): threaded BLAS fights other jobs and runs slower.
- Run one copy at a time; a reproducibility check can run its two copies one after the other.
- Another session's work stays the user's call: report it and ask before pausing it.
- Same pattern elsewhere: a Whisper transcription stalled at 20% CPU while other jobs ran (a music app, 2026-10-19).

## Estimating ETAs

A few-iteration cold benchmark *underestimates* a multi-hour job. Re-measure the
rate after it's been running a while (steady state) before quoting an ETA, and
state the assumption explicitly ("~Xs/iter *if it holds*").
