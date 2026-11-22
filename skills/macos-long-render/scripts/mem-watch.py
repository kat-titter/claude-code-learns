#!/usr/bin/env python3
"""Keep a long local job inside the Mac's memory: size the pool, watch it, pause the newest worker, read the log.

  mem-watch.py budget [--peak-gb G | -- CMD ...]    worker count from free memory and one unit's measured peak
  mem-watch.py run [--job-gb G] -- CMD ...          one heavy job at a time machine-wide: lock, gate, run, govern
  mem-watch.py watch --pid JOB [--match RE] [...]   log every N s; SIGSTOP/SIGCONT/SIGTERM the job's newest workers
  mem-watch.py summary LOG                          memory, thermal or CPU: what the log says went wrong
  mem-watch.py resume LOG                           after a kill -9 of the watcher, SIGCONT what its log left paused
  mem-watch.py --self-test                          the pause/resume/terminate rules on synthetic readings

Only the job's own descendants (or processes matching --match) are ever signalled, never the Claude app, CLI,
helpers or MCP servers, never this watcher or its parents. Paused workers are resumed when the watcher exits. Stdlib only, macOS only.
"""
import argparse, fcntl, json, os, re, signal, subprocess, sys, time

GB = 1 << 30
LEVELS = {1: "normal", 2: "warn", 4: "critical"}
THERMAL = ["nominal", "moderate", "heavy", "trapping", "sleeping"]
# Executables that are never signalled. Matched on the executable path, not the arguments, so a job script that
# lives under ~/Claude/Projects is still a worker.
PROTECT = re.compile(r"(?i)(/Claude\.app/|/claude-code/|/\.claude-science/|(^|/)claude$|WindowServer|loginwindow|"
                     r"/Finder\.app/|/Dock\.app/|kernel_task|(^|/)launchd$|(^|/)caffeinate$)")
SHELLS = {"zsh", "bash", "sh", "dash", "fish"}
LOCK = os.environ.get("MEM_WATCH_LOCK") or os.path.expanduser("~/.claude/run/heavy.lock")
# every session's heavy job queues on this one file; MEM_WATCH_LOCK isolates a test or a second queue


def sh(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def machine():
    """One reading of the whole machine: pressure, free %, swap, compressor, load, thermal, disk for swap."""
    total, free, level, swap, load = sh("sysctl", "-n", "hw.memsize", "kern.memorystatus_level",
                                        "kern.memorystatus_vm_pressure_level", "vm.swapusage",
                                        "vm.loadavg").splitlines()[:5]
    sw = dict(re.findall(r"(total|used) = ([\d.]+)M", swap))
    vm = sh("vm_stat")
    page = int(re.search(r"page size of (\d+)", vm).group(1))
    comp = int(re.search(r"occupied by compressor:\s+(\d+)", vm).group(1))
    therm = re.search(r"(\d+)\s*$", sh("notifyutil", "-g", "com.apple.system.thermalpressurelevel"))
    st = os.statvfs("/System/Volumes/VM" if os.path.isdir("/System/Volumes/VM") else "/")
    return {"level": int(level), "free": int(free), "swap": round(float(sw["used"]) / 1024, 2),
            "swap_total": round(float(sw["total"]) / 1024, 2), "comp": round(comp * page / GB, 2),
            "load1": float(load.split()[1]), "therm": int(therm.group(1)) if therm else -1,
            "disk": round(st.f_bavail * st.f_frsize / GB, 1), "ram": round(int(total) / GB, 1)}


def etime_s(e):
    days, _, hms = e.rpartition("-")
    parts = [int(x) for x in hms.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return (int(days) if days else 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def processes():
    """pid -> {ppid, uid, mb, age, cmd, exe}, from two ps calls (args and executable path differ)."""
    procs = {}
    for line in sh("ps", "-axo", "pid=,ppid=,uid=,rss=,etime=,command=").splitlines():
        f = line.split(None, 5)
        if len(f) == 6:
            procs[int(f[0])] = {"ppid": int(f[1]), "uid": int(f[2]), "mb": int(f[3]) // 1024,
                                "age": etime_s(f[4]), "cmd": f[5], "exe": ""}
    for line in sh("ps", "-axo", "pid=,comm=").splitlines():
        f = line.split(None, 1)
        if len(f) == 2 and int(f[0]) in procs:
            procs[int(f[0])]["exe"] = f[1]
    return procs


def descendants(procs, root):
    kids = {}
    for pid, p in procs.items():
        kids.setdefault(p["ppid"], []).append(pid)
    out, stack = [], list(kids.get(root, []))
    while stack:
        pid = stack.pop()
        out.append(pid)
        stack.extend(kids.get(pid, []))
    return out


def untouchable(procs):
    """This watcher, its ancestors, pid <= 1, other users, protected executables, and anything a protected process
    started with no shell in between (Claude's MCP servers); a job run from a Claude shell is still a worker."""
    keep, pid = set(), os.getpid()
    while pid > 1 and pid in procs:
        keep.add(pid)
        pid = procs[pid]["ppid"]
    uid = os.getuid()
    keep |= {p for p, v in procs.items() if p <= 1 or v["uid"] != uid or PROTECT.search(v["exe"])}

    def started_by_protected(p):
        q = procs[p]["ppid"]
        while q in procs and q > 1:
            if os.path.basename(procs[q]["exe"]).lstrip("-") in SHELLS:
                return False
            if PROTECT.search(procs[q]["exe"]):
                return True
            q = procs[q]["ppid"]
        return False

    return keep | {p for p in procs if started_by_protected(p)}


def find_workers(procs, root, match, min_mb, no_touch, with_root=False):
    """The job's workers: descendants of root (or all processes) matching --match, else holding over min_mb, and
    innermost, so a pool runner whose own command line names the script (xargs ... run.py) is not one big worker.
    Each worker's group is itself plus its descendants (an ffmpeg it spawned), signalled together.
    The root itself is a worker only with with_root, which `run` sets because it started the process it watches;
    under `watch --pid` the root is the job's own driver and is never signalled, as --pid's help says."""
    pool = descendants(procs, root) if root else list(procs)
    if root and with_root:
        pool = [root] + pool
    rx = re.compile(match) if match else None
    cand = {p for p in pool if p not in no_touch and
            (rx.search(procs[p]["cmd"]) if rx else procs[p]["mb"] >= min_mb)}
    workers = []
    for p in cand:
        below = [d for d in descendants(procs, p) if d not in no_touch]
        if not cand.intersection(below):
            group = [p] + below
            workers.append({"pid": p, "age": procs[p]["age"], "group": group,
                            "mb": sum(procs[g]["mb"] for g in group)})
    return workers


class Governor:
    """Pure decision rules, one step per reading. Pause the newest running worker while memory is short; terminate
    the newest paused one if pressure stays critical with only --keep running; resume the oldest paused one after
    --calm seconds of normal pressure and flat swap."""

    def __init__(self, a):
        self.a, self.paused, self.swap_base, self.prev_swap = a, set(), None, None
        self.stuck_since, self.calm_since, self.calm_swap = None, None, None

    def reasons(self, m, job_gb, rising):
        a, why = self.a, []
        if m["level"] >= (2 if a.pause_at == "warn" else 4):
            why.append("pressure " + LEVELS.get(m["level"], str(m["level"])))
        if m["free"] < a.min_free:
            why.append("free %d%% < %d%%" % (m["free"], a.min_free))
        if rising and m["swap"] - self.swap_base > a.swap_gb:
            why.append("swap +%.1f GB and rising" % (m["swap"] - self.swap_base))
        if a.job_gb and job_gb > a.job_gb:
            why.append("job %.2f GB > %.2f" % (job_gb, a.job_gb))
        if m.get("disk", 99) < a.min_disk:
            why.append("disk %.1f GB < %.1f for swap" % (m["disk"], a.min_disk))
        return why

    def step(self, now, m, workers):
        a = self.a
        alive = {w["pid"] for w in workers}
        self.paused &= alive
        if self.swap_base is None:
            self.swap_base = self.prev_swap = m["swap"]
        rising = m["swap"] - self.prev_swap > 0.016
        self.prev_swap = m["swap"]
        job_gb = sum(w["mb"] for w in workers) / 1024
        running = [w for w in workers if w["pid"] not in self.paused]
        paused = [w for w in workers if w["pid"] in self.paused]
        why = self.reasons(m, job_gb, rising)
        if why and m.get("disk", 99) < a.min_disk and workers:
            # swap cannot grow on a full disk, and then macOS kills the whole session, Claude included: end the
            # newest worker now, the last one too (2026-11-21: 7.4 GB free went to 0.2 GB in 4 min of swap growth)
            w = min(running or paused, key=lambda w: (w["age"], -w["pid"]))
            self.paused.discard(w["pid"])
            return [("term", w, ", ".join(why))]
        if why:
            self.calm_since = None
            if len(running) > a.keep:
                self.stuck_since = None
                w = min(running, key=lambda w: (w["age"], -w["pid"]))
                self.paused.add(w["pid"])
                return [("pause", w, ", ".join(why))]
            over = bool(a.job_gb and job_gb > a.job_gb)
            severe = m["level"] >= 4 or m["free"] < a.min_free or over
            if not (severe and (paused or over)):
                self.stuck_since = None                 # the SIGTERM clock runs only while severe with nothing to pause
                return []
            if self.stuck_since is None:
                self.stuck_since = now
            if now - self.stuck_since >= a.term_after:
                # a job over its cap is ended even as the last worker: a lone runaway (one Python at 10 GB,
                # 2026-11-21) is what --keep would otherwise shelter
                w = min(paused or running, key=lambda w: (w["age"], -w["pid"]))
                self.paused.discard(w["pid"])
                self.stuck_since = now
                return [("term", w, ", ".join(why) + " for %ds with %d running" % (a.term_after, len(running)))]
            return []
        self.stuck_since = None
        calm = (m["level"] == 1 and m["free"] >= a.min_free + 5 and
                (not a.job_gb or job_gb <= 0.85 * a.job_gb))
        if not calm:
            self.calm_since = None
            return []
        if self.calm_since is None:
            self.calm_since, self.calm_swap = now, m["swap"]
            return []
        if m["swap"] - self.calm_swap > 0.0625:
            self.calm_since, self.calm_swap = now, m["swap"]
            return []
        if now - self.calm_since < a.calm:
            return []
        self.swap_base = m["swap"]                      # re-arm: swap counts from the last calm point
        self.calm_since, self.calm_swap = now, m["swap"]
        if paused:
            w = max(paused, key=lambda w: (w["age"], w["pid"]))
            self.paused.discard(w["pid"])
            return [("resume", w, "calm %ds" % a.calm)]
        return []


def signal_group(group, sig, no_touch):
    for pid in group:
        if pid not in no_touch:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def cmd_watch(a, alive=None):
    """alive, which `run` passes as its child's poll(), says whether the process this watcher started is still up.
    `watch --pid` passes none: it watches a job it did not start, whose root is that job's own driver, so the root
    is never a worker there. `a` stays a plain argparse namespace that serialises into the log."""
    if not a.pid and not a.match:
        sys.exit("watch needs --pid JOB (its descendants are the workers) or --match REGEX")
    procs = processes()
    if a.pid and (a.pid not in procs or PROTECT.search(procs[a.pid]["exe"]) or procs[a.pid]["uid"] != os.getuid()):
        sys.exit("pid %d is not running, or is protected (Claude, system, another user)" % a.pid)
    log = open(a.log, "a", buffering=1)
    gov = Governor(a)
    caf = None if a.no_caffeinate else subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
    stopped = {}                     # worker pid -> every pid SIGSTOPped with it, kept until resumed, killed or gone
    exits = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)

    def emit(rec):
        log.write(json.dumps(rec) + "\n")

    def bye(sig, _):
        raise SystemExit(128 + sig)

    for sig in exits:
        if signal.getsignal(sig) != signal.SIG_IGN:      # keep nohup's ignore on SIGHUP
            signal.signal(sig, bye)
    emit({"t": now_iso(), "event": "start", "pid": a.pid, "match": a.match, "args": vars(a)})
    t0 = time.time()
    try:
        while True:
            procs = processes()
            if a.pid and a.pid not in procs:
                break
            if a.pid and alive is not None and alive() is not None:   # run's own child exited (a zombie stays in ps)
                break
            no_touch = untouchable(procs)
            for pid in [p for p in stopped if p not in procs]:    # a paused worker died: free what it left stopped
                signal_group(stopped.pop(pid), signal.SIGCONT, no_touch)
            m = machine()
            fp = footprints()            # footprint counts swapped and compressed pages; RSS fell to 47 MB at 10 GB
            for pid, v in procs.items():
                v["mb"] = max(v["mb"], int(fp.get(pid, 0)))
            workers = find_workers(procs, a.pid, a.match, a.min_rss_mb, no_touch, with_root=alive is not None)
            seen = {w["pid"] for w in workers}
            for pid in stopped:          # a paused worker stays governed while it lives, even swapped under --min-rss-mb
                if pid not in seen:
                    group = [pid] + [d for d in descendants(procs, pid) if d not in no_touch]
                    workers.append({"pid": pid, "age": procs[pid]["age"], "group": group,
                                    "mb": sum(procs[g]["mb"] for g in group)})
            for act, w, why in gov.step(time.time(), m, workers):
                if act == "pause":
                    signal_group(w["group"], signal.SIGSTOP, no_touch)
                    stopped[w["pid"]] = list(w["group"])
                elif act == "resume":
                    signal_group(stopped.pop(w["pid"], w["group"]), signal.SIGCONT, no_touch)
                else:
                    group = stopped.pop(w["pid"], w["group"])
                    signal_group(group, signal.SIGTERM, no_touch)
                    signal_group(group, signal.SIGCONT, no_touch)    # a stopped process only dies once continued
                emit({"t": now_iso(), "event": act, "pid": w["pid"], "group": w["group"], "mb": w["mb"], "why": why})
                print("%s %s %d (%d MB): %s" % (now_iso(), act, w["pid"], w["mb"], why), file=sys.stderr)
            top = sorted(procs.items(), key=lambda kv: -kv[1]["mb"])[:5]
            m.update({"t": now_iso(), "job": round(sum(w["mb"] for w in workers) / 1024, 2),
                      "run": len(workers) - len(stopped), "paused": len(stopped),
                      "top": [[p, v["mb"], os.path.basename(v["exe"])[:40]] for p, v in top]})
            emit(m)
            if a.duration and time.time() - t0 > a.duration:
                break
            time.sleep(a.every)
    finally:
        for sig in exits:
            signal.signal(sig, signal.SIG_IGN)       # a second signal must not cut the cleanup short
        no_touch = untouchable(processes())
        for pid, group in stopped.items():
            signal_group(group, signal.SIGCONT, no_touch)
            emit({"t": now_iso(), "event": "resume", "pid": pid, "why": "watcher exit"})
        emit({"t": now_iso(), "event": "end"})
        if caf:
            caf.terminate()


def cmd_resume(a):
    """After the watcher died by SIGKILL: SIGCONT every pid its log paused and never resumed or terminated."""
    left = {}
    for line in open(a.log):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "pause":
            left[r["pid"]] = r.get("group", [r["pid"]])
        elif r.get("event") in ("resume", "term"):
            left.pop(r["pid"], None)
    procs = processes()
    pids = [p for g in left.values() for p in g if p in procs]
    signal_group(pids, signal.SIGCONT, untouchable(procs))
    with open(a.log, "a") as log:                       # so a second run does not signal these pids again
        for pid in left:
            log.write(json.dumps({"t": now_iso(), "event": "resume", "pid": pid, "why": "resume LOG"}) + "\n")
    print("resumed %d process(es): %s" % (len(pids), " ".join(map(str, pids)) or "none"))


def cmd_run(a):
    """One heavy job at a time across every session: wait for the machine-wide lock, wait until memory and disk have
    room, then run CMD under the watch rules and exit with its code. Sessions queue here instead of piling up."""
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("run needs -- CMD")
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    lock = open(LOCK, "a+")
    waited = 0
    while True:                      # --gate-wait bounds the queue too: a held lock is the commonest way to wait
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            lock.seek(0)
            held = lock.read().strip()[-200:] or "?"
            if a.gate_wait and waited >= a.gate_wait:
                sys.exit("run: gave up after %ds waiting for the heavy-job lock, held by: %s" % (waited, held))
            if not waited:
                print("run: waiting for the heavy-job lock, held by: %s" % held, file=sys.stderr)
            time.sleep(5); waited += 5
    lock.seek(0); lock.truncate(); lock.write("%d %s %s\n" % (os.getpid(), now_iso(), " ".join(cmd)[:160])); lock.flush()
    while True:
        m = machine()
        short = [w for w, bad in (("free %d%% < %d%%" % (m["free"], a.gate_free), m["free"] < a.gate_free),
                                  ("disk %.1f GB < %.1f" % (m["disk"], a.gate_disk), m["disk"] < a.gate_disk)) if bad]
        if not short:
            break
        if a.gate_wait and waited >= a.gate_wait:
            sys.exit("run: gave up after %ds: %s" % (waited, ", ".join(short)))
        print("run: gate waiting: %s" % ", ".join(short), file=sys.stderr)
        time.sleep(30); waited += 30
    child = subprocess.Popen(cmd)
    a.pid = child.pid
    try:
        cmd_watch(a, alive=child.poll)
    finally:
        rc = child.wait()
        lock.close()
    sys.exit(rc)


def footprints():
    """pid -> MB of physical footprint (what jetsam counts), from one top sample; RSS double-counts shared pages."""
    out, unit = {}, {"B": 1 / 2**20, "K": 1 / 1024, "M": 1, "G": 1024}
    for line in sh("top", "-l", "1", "-stats", "pid,mem").splitlines():
        f = re.match(r"\s*(\d+)\s+([\d.]+)([BKMG])", line)
        if f:
            out[int(f.group(1))] = float(f.group(2)) * unit[f.group(3)]
    return out


def measure_peak(cmd):
    r = subprocess.run(["/usr/bin/time", "-l"] + cmd, capture_output=True, text=True)
    fp = re.search(r"(\d+)\s+peak memory footprint", r.stderr)
    rss = re.search(r"(\d+)\s+maximum resident set size", r.stderr)
    if not (fp or rss):
        sys.exit("could not read a peak from /usr/bin/time -l; exit %d\n%s" % (r.returncode, r.stderr[-400:]))
    return int((fp or rss).group(1)) / GB, r.returncode


def cmd_budget(a):
    m, procs, fp = machine(), processes(), footprints()
    cores = int(sh("sysctl", "-n", "hw.ncpu"))
    if a.cmd:
        cmd = a.cmd[1:] if a.cmd[0] == "--" else a.cmd
        peak, rc = measure_peak(cmd)
        print("one unit: peak footprint %.2f GB (exit %d): %s" % (peak, rc, " ".join(cmd)))
    elif a.peak_gb:
        peak = a.peak_gb
    else:
        sys.exit("budget needs --peak-gb G or -- CMD (one small unit, measured with /usr/bin/time -l)")
    cli = [p for p, v in procs.items() if re.search(r"/claude-code/.*/claude$", v["exe"])]
    shells = ("zsh", "bash", "sh", "-zsh")         # a session's shell children are jobs, not the session's cost
    kids = {}
    for p, v in procs.items():
        kids.setdefault(v["ppid"], []).append(p)
    mcp, stack = [], [k for c in cli for k in kids.get(c, [])]
    while stack:
        p = stack.pop()
        if os.path.basename(procs[p]["exe"]) not in shells:
            mcp.append(p)
            stack.extend(kids.get(p, []))
    app = [p for p, v in procs.items() if "/Claude.app/" in v["exe"]]
    gb = lambda ps: sum(fp.get(p, procs[p]["mb"]) for p in ps) / 1024
    per_agent = (gb(cli) + gb(mcp)) / max(len(cli), 1)
    avail = m["free"] / 100 * m["ram"]
    headroom = a.headroom * m["ram"]
    reserve = headroom + a.agents * per_agent
    by_mem = int((avail - reserve) // (peak * a.margin)) if peak > 0 else cores
    workers = max(0, min(by_mem, cores - 2))
    print("machine: %.0f GB RAM, %d cores, pressure %s, free %d%% = %.1f GB available, swap %.1f/%.1f GB, "
          "disk for swap %.0f GB, thermal %s, load %.1f" % (m["ram"], cores, LEVELS.get(m["level"]), m["free"], avail,
          m["swap"], m["swap_total"], m["disk"], THERMAL[m["therm"]] if 0 <= m["therm"] < 5 else "?", m["load1"]))
    print("Claude now: %d CLI sessions/agents %.1f GB + %d MCP servers %.1f GB (%.2f GB each), app %.1f GB"
          % (len(cli), gb(cli), len(mcp), gb(mcp), per_agent, gb(app)))
    print("reserve: headroom %.1f GB (%.0f%% of RAM) + %d new agents x %.2f GB = %.1f GB"
          % (headroom, a.headroom * 100, a.agents, per_agent, reserve))
    print("workers = min(floor((%.1f - %.1f) / (%.2f x %.2f)), %d cores - 2) = min(%d, %d) = %d"
          % (avail, reserve, peak, a.margin, cores, by_mem, cores - 2, workers))
    if m["disk"] < m["ram"]:
        print("WARNING: %.0f GB free for swap, under the %.0f GB of RAM; macOS cannot grow swap when the disk is "
              "near full ('low swap: failed to create swapfile'), so free disk first" % (m["disk"], m["ram"]))
    if m["level"] > 1:
        print("WARNING: pressure is already %s; start fewer workers or close sessions" % LEVELS.get(m["level"]))
    print("check: after a few units, `mem-watch.py summary LOG` shows pressure normal and swap flat; if not, drop one")


def cmd_summary(a):
    ticks, events = [], []
    for line in open(a.log):
        try:
            r = json.loads(line)
        except ValueError:                         # a line cut short when the watcher was killed
            continue
        (events if "event" in r else ticks).append(r)
    if not ticks:
        sys.exit("no readings in %s" % a.log)
    cores = int(sh("sysctl", "-n", "hw.ncpu")) or 1
    n = len(ticks)
    frac = lambda f: sum(1 for t in ticks if f(t)) / n
    peak = {}
    for t in ticks:
        for pid, mb, name in t["top"]:
            if mb > peak.get(name, (0,))[0]:
                peak[name] = (mb, pid)
    swap_growth = max(t["swap"] for t in ticks) - ticks[0]["swap"]
    counts = {e: sum(1 for x in events if x["event"] == e) for e in ("pause", "resume", "term")}
    print("span %s to %s, %d readings" % (ticks[0]["t"], ticks[-1]["t"], n))
    print("memory: worst pressure %s (warn %.0f%%, critical %.0f%% of readings), min free %d%%, swap %.1f -> max "
          "%.1f GB, compressor max %.1f GB, disk min %.0f GB, job peak %.2f GB"
          % (LEVELS.get(max(t["level"] for t in ticks)), 100 * frac(lambda t: t["level"] == 2),
             100 * frac(lambda t: t["level"] >= 4), min(t["free"] for t in ticks), ticks[0]["swap"],
             max(t["swap"] for t in ticks), max(t["comp"] for t in ticks), min(t["disk"] for t in ticks),
             max(t["job"] for t in ticks)))
    print("thermal: worst %s, heavy or worse %.0f%% of readings" % (THERMAL[max(0, max(t["therm"] for t in ticks))],
                                                                    100 * frac(lambda t: t["therm"] >= 2)))
    print("cpu: load max %.1f on %d cores, over 2x cores %.0f%% of readings"
          % (max(t["load1"] for t in ticks), cores, 100 * frac(lambda t: t["load1"] > 2 * cores)))
    print("actions: %(pause)d pauses, %(resume)d resumes, %(term)d terminations" % counts)
    print("biggest: " + ", ".join("%s %d MB" % (k, v[0]) for k, v in sorted(peak.items(), key=lambda kv: -kv[1][0])[:5]))
    verdict = []
    if max(t["level"] for t in ticks) >= 2 or swap_growth > 1 or min(t["free"] for t in ticks) < 15:
        verdict.append("memory")
    if frac(lambda t: t["therm"] >= 2) > 0.1:
        verdict.append("thermal")
    if frac(lambda t: t["load1"] > 2 * cores) > 0.1:
        verdict.append("CPU contention")
    print("verdict: " + (" + ".join(verdict) or "no memory, thermal or CPU limit hit; look at the job itself"))


def self_test():
    a = argparse.Namespace(pause_at="warn", min_free=10, swap_gb=2.0, job_gb=0, keep=1, term_after=60, calm=30,
                           min_disk=4)
    g = Governor(a)
    ok = lambda m: dict({"level": 1, "free": 60, "swap": 1.0}, **m)
    ws = [{"pid": 10, "age": 300, "mb": 900}, {"pid": 11, "age": 200, "mb": 900}, {"pid": 12, "age": 100, "mb": 900}]
    ws3 = list(ws)
    fails, n = [], [0]

    def expect(got, want, label):
        n[0] += 1
        got = [(act, w["pid"]) for act, w, _ in got]
        if got != want:
            fails.append("%s: got %s, want %s" % (label, got, want))

    expect(g.step(0, ok({}), ws), [], "calm start")
    expect(g.step(10, ok({"level": 4}), ws), [("pause", 12)], "critical pauses newest")
    expect(g.step(20, ok({"level": 4}), ws), [("pause", 11)], "then the next newest")
    expect(g.step(30, ok({"level": 4}), ws), [], "keeps the last worker")
    expect(g.step(85, ok({"level": 4}), ws), [], "no SIGTERM before term_after of being stuck")
    expect(g.step(90, ok({"level": 4}), ws), [("term", 12)], "terminates newest paused after term_after")
    ws = ws[:2]
    expect(g.step(95, ok({}), ws), [], "calm begins")
    expect(g.step(125, ok({}), ws), [("resume", 11)], "resumes after calm")
    g = Governor(a)
    expect(g.step(0, ok({"level": 2}), ws3), [("pause", 12)], "warn pauses")
    expect(g.step(10, ok({"level": 2}), ws3), [("pause", 11)], "warn pauses the next")
    expect(g.step(300, ok({"level": 2}), ws3), [], "long warn never terminates")
    expect(g.step(310, ok({"level": 4}), ws3), [], "one critical reading after a long warn does not terminate")
    expect(g.step(370, ok({"level": 4}), ws3), [("term", 12)], "critical for term_after does")
    g = Governor(a)
    expect(g.step(0, ok({"swap": 1.0}), ws), [], "swap baseline")
    expect(g.step(10, ok({"swap": 3.5}), ws), [("pause", 11)], "swap rising past +2 GB pauses")
    expect(g.step(20, ok({"swap": 3.5}), ws), [], "flat swap starts calm, no new pause")
    expect(g.step(55, ok({"swap": 3.5}), ws), [("resume", 11)], "flat swap for calm re-arms and resumes")
    expect(g.step(65, ok({"swap": 3.6}), ws), [], "small rise after re-arm is fine")
    g = Governor(argparse.Namespace(**dict(vars(a), job_gb=1.5, pause_at="critical")))
    expect(g.step(0, ok({"level": 2}), ws), [("pause", 11)], "job cap pauses the newest")
    g = Governor(argparse.Namespace(**dict(vars(a), pause_at="critical")))
    expect(g.step(0, ok({"level": 2}), ws), [], "warn alone does not pause when pause_at=critical")
    one = [{"pid": 20, "age": 100, "mb": 10240}]
    g = Governor(a)
    expect(g.step(0, ok({"disk": 3.0}), one), [("term", 20)], "disk under the floor ends the last worker at once")
    g = Governor(a)
    expect(g.step(0, ok({"disk": 9.0}), one), [], "disk above the floor does nothing")
    g = Governor(argparse.Namespace(**dict(vars(a), job_gb=4)))
    expect(g.step(0, ok({}), one), [], "a lone worker over the cap starts the clock")
    expect(g.step(60, ok({}), one), [("term", 20)], "and is ended after term_after, though it is the last")
    for exe, want in [("/Applications/Claude.app/Contents/MacOS/Claude", True),
                      ("/Users/x/Library/Application Support/Claude/claude-code/2.1/claude.app/Contents/MacOS/claude", True),
                      ("claude", True), ("caffeinate", True),
                      ("/usr/local/bin/python3", False), ("/Users/x/Claude/Projects/essay/analysis/run.py", False)]:
        n[0] += 1
        if bool(PROTECT.search(exe)) != want:
            fails.append("protect %s: want %s" % (exe, want))
    print("\n".join(fails) or "self-test: %d checks pass" % n[0])
    return 1 if fails else 0


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd_name", required=True)
    b = sub.add_parser("budget", help="worker count from free memory and one unit's peak")
    b.add_argument("--peak-gb", type=float, help="one worker's peak, if already measured")
    b.add_argument("--agents", type=int, default=0, help="Claude sessions or agents you may start during the run")
    b.add_argument("--headroom", type=float, default=0.15, help="fraction of RAM kept free (default 0.15)")
    b.add_argument("--margin", type=float, default=1.25, help="per-worker safety factor (default 1.25)")
    b.add_argument("cmd", nargs=argparse.REMAINDER, help="-- CMD: one small unit to measure")
    w = sub.add_parser("watch", help="log and govern a running job")
    run = sub.add_parser("run", help="lock, gate, run CMD and govern it: one heavy job at a time machine-wide")
    w.add_argument("--pid", type=int, help="the job's root pid; its descendants are the workers")
    w.add_argument("--match", help="regex on worker command lines (narrows --pid, or alone selects workers)")
    w.add_argument("--min-rss-mb", type=int, default=100, help="without --match, a worker holds at least this")
    w.add_argument("--log", default="mem-watch.jsonl")
    w.add_argument("--every", type=float, default=10, help="seconds between readings (default 10)")
    w.add_argument("--pause-at", choices=["warn", "critical"], default="warn")
    w.add_argument("--min-free", type=int, default=10, help="pause below this memory free %% (default 10)")
    w.add_argument("--swap-gb", type=float, default=2.0, help="pause when swap rises this far past the last calm point")
    w.add_argument("--job-gb", type=float, default=0, help="cap on the job's footprint (0 = off); past it for "
                   "--term-after seconds, the newest worker is ended, the last one too")
    w.add_argument("--min-disk-gb", dest="min_disk", type=float, default=4,
                   help="disk free for swap below this ends the newest worker at once (default 4)")
    w.add_argument("--keep", type=int, default=1, help="workers never paused (default 1)")
    w.add_argument("--term-after", type=float, default=60, help="seconds of severe shortage before a SIGTERM")
    w.add_argument("--calm", type=float, default=30, help="seconds of calm before resuming one worker")
    w.add_argument("--duration", type=float, default=0, help="stop watching after this many seconds (0 = job end)")
    w.add_argument("--no-caffeinate", action="store_true", help="skip the caffeinate -i held while watching")
    for act in w._actions:                         # run takes every watch option (but --pid and --match default off)
        if act.dest not in ("help", "pid", "match"):
            run._add_action(act)
    run.add_argument("--match", help="regex on worker command lines inside the job")
    run.add_argument("--gate-free", type=int, default=25, help="start only with this memory free %% (default 25)")
    run.add_argument("--gate-disk", type=float, default=8, help="start only with this much disk free, GB (default 8)")
    run.add_argument("--gate-wait", type=int, default=0, help="give up after this many seconds (0 = wait)")
    run.add_argument("cmd", nargs=argparse.REMAINDER, help="-- CMD to run")
    s = sub.add_parser("summary", help="read a watch log")
    s.add_argument("log")
    r = sub.add_parser("resume", help="SIGCONT what a killed watcher's log left paused")
    r.add_argument("log")
    a = p.parse_args()
    {"budget": cmd_budget, "watch": cmd_watch, "run": cmd_run, "summary": cmd_summary,
     "resume": cmd_resume}[a.cmd_name](a)


if __name__ == "__main__":
    main()
