---
name: macos-long-render
description: Runs long local jobs on a Mac (renders, training, batch science with many workers) without sleep or out-of-memory kills - sizes the worker pool from measured memory, pauses the newest worker under memory pressure with a watcher script, makes units survive a kill, and diagnoses a crawl. Use before unattended or parallel compute, or on "out of memory", "OOM", "Mac froze", "too many workers", "memory pressure", "how many workers", "swap" or "slowed overnight".
when_to_use: Before an overnight or multi-worker run; beside Claude sessions or agents; after a crawl, a kill or a freeze.
---

# Long jobs on a Mac

A long job needs the Mac awake (§1), a pool that fits in memory (§2), a watcher that sheds load before macOS does
(§3), units that survive a kill (§4) and a budget that counts Claude too (§5). §6 reads what went wrong; §7 quotes ETAs.

## Gotchas

- A pool runs the Mac out of memory because Claude sessions and agents count too. 2026-11-19: a five-worker rebuild
  plus several sessions and subagents; the kernel logged `low swap: failed to create swapfile` at 16:12:52, pressure
  warn 16:13:26, critical 16:13:55, then the app restarted. The disk was 97% full, so swap could not grow (likely
  cause). Restarted with 4 workers and no agents, it ran clean and reproduced the finished passes exactly.
- `xargs -P` stops launching units once a worker dies by a signal (`terminated with signal 15; aborting`): loop passes
  until every unit has its marker (§4).
- Pausing a worker (SIGSTOP) stops its growth but frees nothing until macOS compresses or swaps it out; only
  terminating frees memory at once.
- A render that ran fine for hours crawls overnight (the last 9% at about 36 times slower): the Mac slept or
  idle-throttled; wrap it in caffeinate (§1). Read the power log before blaming thermals (§6).

## 1. Stay awake

Wrap any job that runs unattended for more than an hour or two; otherwise macOS sleeps or idle-throttles it.

```bash
caffeinate -dimsu nohup python3 long_job.py > job.log 2>&1 &
```
Flags: `-d` display, `-i` idle, `-m` disk, `-s` sleep on charger, `-u` user active. Keep it plugged in, lid open.
Wrapper: `${CLAUDE_SKILL_DIR}/scripts/caffeinate-render.sh -- <command>`. The watcher (§3) holds its own `caffeinate -i`.

## 2. Size the pool before launch

```
workers   = min( floor((available - reserve) / (peak x 1.25)), cores - 2 )
available = memory free % x RAM     kern.memorystatus_level, what jetsam sees
reserve   = 15% of RAM + agents you may start x 0.34 GB
peak      = "peak memory footprint" of the largest unit, from /usr/bin/time -l
```
`python3 ${CLAUDE_SKILL_DIR}/scripts/mem-watch.py budget --agents 2 -- python3 step.py --unit biggest` runs the unit,
measures it, counts the Claude processes running now and prints the formula filled in. It warns when the disk has less
free than RAM (swap cannot grow) or pressure is already above normal.
**Check**: after a few units, `mem-watch.py summary watch.jsonl` shows pressure normal and swap flat; if not, drop one
worker. On a 16 GB, 10-core Mac (2026-11-19): 11.2 GB available, 2.4 GB reserve, a 0.25 GB unit, so 8 workers, capped
by cores.
- Footprint, not RSS: `ps` RSS counts shared pages twice (a Claude CLI showed 420-460 MB RSS against about 230 MB in
  `top`'s MEM). `/usr/bin/time -l` reports the largest single process, so a unit that spawns helpers needs their peak too.
- Measure the biggest unit, not the first; set `OMP_NUM_THREADS=1` and friends when workers already fill the cores.

## 3. Watch the run

```bash
caffeinate -i nohup ./run_all.sh 4 > run.log 2>&1 &
JOB=$!
nohup python3 ${CLAUDE_SKILL_DIR}/scripts/mem-watch.py watch --pid $JOB --match 'step\.py' --log watch.jsonl 2> watch.err &
```
Every 10 s it logs one JSON line: pressure, free %, swap, compressor, load, thermal level, disk free, the job's RSS,
running and paused workers, the top five processes. Workers are the job's innermost descendants matching `--match`
(else any over 100 MB); check that the first readings' `run` equals your worker count.

| when | default | it does |
|---|---|---|
| pressure warn, free under 10%, swap up 2 GB since the last calm point and rising, or the job over `--job-gb` | `--pause-at warn` | SIGSTOP the newest running worker, one per reading, keeping `--keep 1` running |
| critical, free under 10% or over the cap for 60 s with only `--keep` running | `--term-after 60` | SIGTERM the newest paused worker; the job reruns its unit (§4) |
| pressure normal, free 15%+, swap flat for 30 s | `--calm 30` | SIGCONT the oldest paused worker, one per calm window |
| the watcher exits (SIGTERM, SIGINT, SIGHUP, even twice) | | SIGCONT every paused worker; after a `kill -9`, `mem-watch.py resume watch.jsonl` does it from the log |

It never signals the Claude app, CLI, helpers or the MCP servers they start (a job run from a Claude shell is still a
worker, even in a folder named Claude), the watcher, its parents or other users. Prefer `--pid`: `--match` alone
governs every matching process you own, and `--match` the worker's own command so a worker that spawns ffmpeg is paused
with it. RSS misses compressed pages, so `--job-gb` is a coarse cap and pressure, free % and swap are the real guards;
the cap counts paused workers too, so a trip over it ends in a SIGTERM unless the job shrinks. The thresholds are set,
not measured; tune them from the log.
`--self-test` runs the rules on synthetic readings (26 checks, including the pressure and swap paths a test cannot
safely force).
Tested 2026-11-19: 4 units of 0.25 GB on 3 workers, `--job-gb 0.6`, readings every second. It paused at 0.68 and 0.73 GB,
terminated the newest paused worker 5 s later, resumed the other after 4 s calm, and the rerun pass finished the killed
unit: 40 s against 30 s unwatched. Cost: 77 ms CPU per reading (under 1% of a core at 10 s), 13 MB. Killing the watcher
mid-pause set both paused workers running again. A review then found four bugs, fixed and pinned: a paused worker that
swapped under 100 MB was forgotten and left frozen, a second SIGTERM cut the exit cleanup short, `--match node` could
pause MCP servers, and the SIGTERM clock started at the first warn. A rerun hit real pressure (warn on 71% of readings,
swap 3.0 to 6.5 GB beside a rebuild): the watcher paused the test's workers, they swapped down to 3 MB and stayed
governed, and it resumed each one when pressure eased.

## 4. Units that survive a kill

- **One marker per unit, written last and atomically**: write `out/U.tmp`, then `os.replace` it to `out/U.done` (or
  the real output name). A killed unit leaves no marker, so it reruns; a finished one never does.
- **Loop passes until nothing is left**, since a pool runner may abort on the first killed worker:
  ```bash
  for pass in 1 2 3; do
    todo=$(for u in $(cat units.txt); do [ -e out/$u.done ] || echo $u; done)
    [ -z "$todo" ] && break
    echo "$todo" | xargs -P "$N" -I{} python3 step.py {} || true
  done
  ```
- **Seed from the unit id** so a rerun reproduces finished units exactly; then a killed run restarts from the step it
  died in, with fewer workers and nothing else heavy running (work-practice, resume points).

## 5. Fan-out costs memory

- Each Claude session or agent holds about 0.34 GB footprint (CLI 0.21 GB plus its MCP servers 0.13 GB); the app holds
  1.9 GB. Ten sessions took 5.3 GB of 16 (measured 2026-11-19). `budget` counts what runs now; `--agents N` reserves
  for the ones you may start mid-run.
- One background script with a log beats a fan-out of agents for known commands; keep agents for judgement calls.
- While a pool runs at its budget, start new sessions, agents or heavy browser work only after rerunning `budget`.

## 6. Diagnose a crawl or a kill

Start with `mem-watch.py summary watch.jsonl`: it prints the worst pressure, swap growth, thermal level, load against
cores, the pauses and kills, the biggest processes, and a verdict.

| sign | cause | fix |
|---|---|---|
| steady for hours, then a cliff, overnight | sleep or idle throttle | caffeinate (§1) |
| pressure warn or critical, swap climbing, `low swap` or jetsam kills | memory | fewer workers, free disk, fewer sessions |
| time per unit climbs gradually, thermal heavy, pressure normal | thermal | fewer workers, cooler machine |
| load over twice the cores, pressure normal, thermal nominal | CPU contention | one BLAS thread per job, one job at a time |

- **Memory, without a watcher log**: the kernel log for the window.
  ```bash
  log show --start "2026-11-19 16:00" --end "2026-11-19 16:20" --style compact --predicate 'sender == "kernel" AND (eventMessage CONTAINS[c] "low swap" OR eventMessage CONTAINS[c] "killing" OR eventMessage CONTAINS[c] "pageshortage" OR eventMessage CONTAINS[c] "compressor-space") AND NOT eventMessage CONTAINS[c] "idle"'
  ```
  `low swap: failed to create swapfile` means swap could not grow: check `df -h /System/Volumes/VM`.
  `killing_top_process ... vm-pageshortage` or `compressor-space-shortage` is jetsam killing for memory;
  `killing (idle) ... idle-exit` and `per-process-limit` lines are routine daemon exits. Daemons log
  `memory pressure ... warn` and `critical` (predicate `eventMessage CONTAINS[c] "memory pressure"`), which dates the slide.
  Real jetsam kills also leave `/Library/Logs/DiagnosticReports/JetsamEvent-*.ips`; the 2026-11-19 freeze left none.
- **Thermal**: `notifyutil -g com.apple.system.thermalpressurelevel` gives 0 nominal, 1 moderate, 2 heavy, 3 trapping,
  4 sleeping (OSThermalNotification.h); `pmset -g therm` reports nothing on Apple silicon. A fanless laptop sat at heavy
  for every reading while a four-worker rebuild ran (2026-11-19).
- **Sleep against thermal**: pull the time per unit across the run and read the rate per window, since cumulative
  averages hide cliffs. Real case (Apple M5, Real-ESRGAN): about 4 s per frame for 91% of frames, then about 145 s per
  frame overnight, a 36-times drop; 6.7 h of compute took 28.6 h of wall clock.
- **A shared, overloaded machine**: `sysctl -n vm.loadavg` against `hw.ncpu`, and `sysctl vm.swapusage`. Load several
  times the cores or swap near full means the job is waiting (a deck build, 2026-10-19: load 35 on 10 cores, 13 GB swap;
  a 5-minute analysis took over an hour while another project ran a parallel batch). `ps -Ao pid,etime,pcpu,rss,command
  -r | head` shows who holds the CPU; a tiny RSS on a big job means it was swapped out. A Whisper transcription stalled
  at 20% CPU the same way (a music app, 2026-10-19).
- Give numeric jobs one BLAS thread on a shared machine (`OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  OMP_NUM_THREADS=1`); run one copy at a time, and a reproducibility check's two copies one after the other.
- Another session's job is the user's call: report it and ask before pausing it.

## 7. Estimating ETAs

A few-iteration cold benchmark underestimates a multi-hour job. Re-measure the rate once it has run a while before
quoting an ETA, and state the assumption ("about X s per unit if it holds").

## Related

systems-practice (memory and precision, logging, background jobs), work-practice (resume points, one heavy job at a
time), debug-practice (a job that says done but wrote nothing).

## Provenance

Caffeinate and the overnight cliff from a Real-ESRGAN render; the shared-machine case 2026-10-19. 2026-11-19, after an
out-of-memory restart during a five-worker rebuild: "a skill to monitor and optimize local memory and compute jobs";
budget, watcher, checkpoints and diagnosis added, `mem-watch.py` tested on a synthetic pool.
