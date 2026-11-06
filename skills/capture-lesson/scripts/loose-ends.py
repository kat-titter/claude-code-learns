#!/usr/bin/env python3
"""Gathers the loose ends a person left across their machine, for a daily "what next" nudge.

A program gathers, an agent judges: this script only collects facts a check can trust (git state,
open pull requests, open markers in memory, unrouted lessons, unapplied proposals, sessions waiting
on the person, from an optional session-tidy log) and remembers when each was first seen, so the nudge can say "day 6" and stop nagging.
It never changes a repo. Output: markdown on stdout; --json for a machine. Standard library only.

  python3 loose-ends.py [--roots ~ ~/work] [--depth 3] [--json] [--no-gh] [--test]
"""
import argparse, json, os, re, subprocess, sys, time
from datetime import date, datetime
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG

HOME = Path.home()
CLAUDE = Path(CONFIG)  # the config folder this skill is installed in, so CLAUDE_CONFIG_DIR installs work too
STATE = CLAUDE / "nudges" / "state.json"
SKIP_DIRS = {"Library", ".Trash", "node_modules", ".nvm", ".cache", ".venv", "venv", ".npm", "Applications"}
# Words people and agents use when work is left open. Matched on memory index lines and progress files.
OPEN_MARK = re.compile(r"\b(open(?! the)|next|waits?|waiting|pending|owed|paused|to paste|left to do|todo|"
                       r"not (?:yet )?(?:done|updated|set|merged|pushed)|unset|blocked|can go)\b", re.I)
DAY = 86400


def run(cmd, cwd=None, timeout=20):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def days(ts):
    return int((time.time() - ts) // DAY)


def find_repos(roots, depth):
    """Every git checkout (main or linked worktree) under the roots, skipping caches and app data."""
    found = []
    for root in roots:
        root = Path(root).expanduser()
        for dirpath, dirnames, _ in os.walk(root):
            p = Path(dirpath)
            level = len(p.relative_to(root).parts)
            if (p / ".git").exists():
                found.append(p)
            dirnames[:] = [d for d in dirnames if level < depth and d not in SKIP_DIRS and not d.startswith(".")
                           or d == ".claude" and level == 0]
    return sorted(set(found))


def repo_facts(repo):
    branch = run(["git", "branch", "--show-current"], repo) or "(detached)"
    porcelain = run(["git", "status", "--porcelain"], repo)
    if porcelain is None:
        return None
    lines = [l for l in porcelain.splitlines() if l.strip()]
    mtimes = []
    for l in lines[:400]:
        f = repo / l[3:].split(" -> ")[-1].strip('"')
        try:
            mtimes.append(f.stat().st_mtime)
        except OSError:
            pass
    has_remote = bool(run(["git", "remote"], repo))
    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"], repo)
    if ahead is None and has_remote:  # no upstream: count commits on no remote at all
        ahead = run(["git", "rev-list", "--count", "HEAD", "--not", "--remotes"], repo)
    last = run(["git", "log", "-1", "--format=%ct"], repo)
    stash = run(["git", "stash", "list"], repo)
    linked = (repo / ".git").is_file()
    merged = False
    if linked and not lines:
        base = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], repo) or "origin/main"
        merged = run(["git", "merge-base", "--is-ancestor", "HEAD", base], repo) is not None
    return {
        "repo": str(repo).replace(str(HOME), "~"), "branch": branch, "dirty": len(lines),
        "oldest_change_days": days(min(mtimes)) if mtimes else None,
        "newest_change_days": days(max(mtimes)) if mtimes else None,
        "unpushed": int(ahead or 0), "stashes": len(stash.splitlines()) if stash else 0,
        "last_commit_days": days(int(last)) if last else None,
        "worktree": linked, "merged_clean_worktree": merged, "remote": has_remote,
    }


def open_prs():
    out = run(["gh", "search", "prs", "--author", "@me", "--state", "open", "--limit", "30",
               "--json", "repository,number,title,url,createdAt,isDraft"], timeout=30)
    if out is None:
        return None
    prs = json.loads(out or "[]")
    for p in prs:
        p["repo"] = p.pop("repository", {}).get("nameWithOwner", "")
        created = datetime.strptime(p["createdAt"][:19], "%Y-%m-%dT%H:%M:%S").timestamp() - time.timezone
        p["age_days"] = days(created)
    return prs


def memory_open():
    """Open markers in each memory index (one line per memory), with how long since that memory changed."""
    items = []
    for index in sorted(CLAUDE.glob("projects/*/memory/MEMORY.md")):
        for line in index.read_text(errors="ignore").splitlines():
            if not line.startswith("- ") or not OPEN_MARK.search(line):
                continue
            m = re.match(r"- \[(.*)\]\(([^)\s]+\.md)\)(.*)", line)
            f = index.parent / m.group(2) if m else None
            if f and f.exists() and not re.search(r"^\s*type:\s*project", f.read_text(errors="ignore")[:600], re.M):
                continue  # feedback, user and reference memories hold rules, not open work
            age = days(f.stat().st_mtime) if f and f.exists() else None
            text = m.group(1) + m.group(3) if m else line[2:]
            items.append({"memory": text, "file": str(f).replace(str(HOME), "~") if f else None,
                          "changed_days": age})
    return items


def progress_files(roots):
    """PROGRESS.md / TODO.md files touched in the last 60 days, with their first open lines."""
    out, hashes = [], set()
    for root in roots:
        root = Path(root).expanduser()
        for dirpath, dirnames, files in os.walk(root):
            p = Path(dirpath)
            level = len(p.relative_to(root).parts)
            dirnames[:] = [d for d in dirnames if level < 4 and d not in SKIP_DIRS and not d.startswith(".")]
            for name in ("PROGRESS.md", "TODO.md"):
                if name in files:
                    f = p / name
                    age = days(f.stat().st_mtime)
                    text = f.read_text(errors="ignore")
                    lines = open_lines(text)
                    if age > 60 or tuple(lines) in hashes:  # copies of one file show once
                        continue
                    hashes.add(tuple(lines))
                    out.append({"file": str(f).replace(str(HOME), "~"), "changed_days": age, "open": lines})
    return out


def open_lines(text, n=4):
    """Lines under a Next / Open / TODO / Waiting heading, else unchecked boxes and marker lines."""
    lines, picked, inside = text.splitlines(), [], False
    for l in lines:
        if re.match(r"\s*(#+\s*)?(next|open|todo|waiting|left|blocked)\b.*$", l, re.I) and len(l) < 60:
            inside = True
            continue
        if inside and re.match(r"\s*#", l):
            inside = False
        if inside and l.strip():
            picked.append(l.strip()[:160])
    if not picked:
        picked = [l.strip()[:160] for l in lines if re.match(r"\s*- \[ \]", l) or OPEN_MARK.search(l)]
    return picked[:n]


def latest(folder, pattern="2*.md"):
    files = sorted(Path(folder).glob(pattern))
    return files[-1] if files else None


def section(text, heading):
    m = re.search(rf"^##+ {re.escape(heading)}.*?$(.*?)(?=^## |\Z)", text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def harness_open():
    """Lessons waiting for review, the watch's proposals, and sessions waiting on the person."""
    h = {}
    inbox = CLAUDE / "lessons-inbox.md"
    if inbox.exists():
        lines = inbox.read_text(errors="ignore").splitlines()
        h["lessons_to_review"] = sum(1 for l in lines if "→ review" in l or "-> review" in l)
    watch = latest(CLAUDE / "skills-watch")
    if watch:
        prop = section(watch.read_text(errors="ignore"), "Proposed")
        h["watch_report"] = str(watch).replace(str(HOME), "~")
        h["watch_proposals"] = [l.strip()[:200] for l in prop.splitlines() if re.match(r"\s*(\d+\.|-) ", l)][:5]
    tidy = latest(CLAUDE / "session-tidy")
    if tidy:
        rows = section(tidy.read_text(errors="ignore"), "Kept, waiting on you") or \
               section(tidy.read_text(errors="ignore"), "waiting on you")
        h["tidy_log"] = str(tidy).replace(str(HOME), "~")
        h["tidy_age_days"] = days(tidy.stat().st_mtime)
        h["sessions_waiting"] = [
            {"session": c[0], "ask": c[1]} for c in
            ([x.strip() for x in r.strip("|").split("|")] for r in rows.splitlines() if r.startswith("|"))
            if len(c) >= 2 and c[0] not in ("session", "") and not set(c[0]) <= set("-: ")]
    pending = [p for p in (CLAUDE / "skills-watch").glob("next-*prompt*.md")] if (CLAUDE / "skills-watch").exists() else []
    h["prompts_to_paste"] = [str(p).replace(str(HOME), "~") for p in pending]
    return h


def keyed(facts):
    """A stable key per loose end, so first-seen dates survive between runs."""
    keys = {}
    for r in facts["repos"]:
        if r["dirty"]:
            keys[f"dirty:{r['repo']}"] = r
        if r["unpushed"] and r["remote"]:
            keys[f"unpushed:{r['repo']}:{r['branch']}"] = r
        if r["merged_clean_worktree"]:
            keys[f"cango:{r['repo']}"] = r
    for p in facts["prs"] or []:
        keys[f"pr:{p['url']}"] = p
    for m in facts["memory"]:
        keys[f"mem:{m['file']}"] = m
    for s in facts["harness"].get("sessions_waiting", []):
        keys[f"wait:{s['session']}"] = s
    return keys


def stamp(facts, state_path=STATE, today=None):
    today = today or date.today().isoformat()
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    keys = keyed(facts)
    new_state = {k: state.get(k, today) for k in keys}
    for k, item in keys.items():
        item.setdefault("seen_days", {})
        item["seen_days"][k.split(":")[0]] = (date.fromisoformat(today) - date.fromisoformat(new_state[k])).days
    facts["closed_since_last_run"] = sorted(k for k in state if k not in keys)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(new_state, indent=1, sort_keys=True))
    return facts


def gather(roots, depth, use_gh):
    repos = [f for f in (repo_facts(r) for r in find_repos(roots, depth)) if f]
    return {"date": date.today().isoformat(), "repos": repos, "prs": open_prs() if use_gh else None,
            "memory": memory_open(), "progress": progress_files(roots), "harness": harness_open()}


def seen(item, kind):
    d = item.get("seen_days", {}).get(kind)
    return f" · seen {d} d" if d else " · new" if d == 0 else ""


def render(f):
    o = [f"# Loose ends, {f['date']}", ""]
    active = [r for r in f["repos"] if r["dirty"] or (r["unpushed"] and r["remote"]) or r["stashes"]]
    recent = lambda d: d is not None and d <= 14
    hot = [r for r in active if recent(r["newest_change_days"]) or recent(r["last_commit_days"])]
    cold = [r for r in active if r not in hot]
    o += ["## Repos with work not saved to a remote", "",
          "| repo | branch | uncommitted | oldest change | unpushed | stashes | last commit |", "|---|---|---|---|---|---|---|"]
    for r in sorted(hot, key=lambda r: (r["newest_change_days"] or 99)):
        oldest = "–" if r["oldest_change_days"] is None else f"{r['oldest_change_days']} d{seen(r, 'dirty')}"
        unpushed = "no remote" if not r["remote"] else f"{r['unpushed']}{seen(r, 'unpushed')}"
        o.append(f"| {r['repo']} | {r['branch']} | {r['dirty']} | {oldest} | {unpushed} | {r['stashes']} | "
                 f"{r['last_commit_days']} d |")
    if cold:
        o += ["", "Cold (no change in 14+ days): " + ", ".join(f"{r['repo']} ({r['dirty']} uncommitted, "
              f"{str(r['unpushed']) + ' unpushed' if r['remote'] else 'no remote'}, last commit {r['last_commit_days']} d)"
              for r in cold)]
    cango = [r for r in f["repos"] if r["merged_clean_worktree"]]
    if cango:
        o += ["", "Worktrees merged and clean, can go: " + ", ".join(f"{r['repo']} ({r['branch']})" for r in cango)]
    o += ["", "## Open pull requests", ""]
    if f["prs"] is None:
        o.append("gh unavailable or signed out: not checked.")
    for p in f["prs"] or []:
        o.append(f"- {p['repo']}#{p['number']} {p['title']} ({p['age_days']} d{', draft' if p['isDraft'] else ''}"
                 f"{seen(p, 'pr')}) {p['url']}")
    if f["prs"] == []:
        o.append("None open.")
    h = f["harness"]
    if h.get("sessions_waiting"):
        o += ["", f"## Sessions waiting on you (from {h['tidy_log']}, {h['tidy_age_days']} d old)", ""]
        o += [f"- {s['session']}: {s['ask']}{seen(s, 'wait')}" for s in h["sessions_waiting"]]
    o += ["", "## Open in memory", ""]
    for m in sorted(f["memory"], key=lambda m: m["changed_days"] if m["changed_days"] is not None else 999):
        o.append(f"- {m['memory']} (changed {m['changed_days']} d{seen(m, 'mem')})")
    if f["progress"]:
        o += ["", "## Progress files", ""]
        for p in f["progress"]:
            o.append(f"- {p['file']} (changed {p['changed_days']} d)" + "".join(f"\n  - {l}" for l in p["open"]))
    o += ["", "## Harness", ""]
    if "lessons_to_review" in h:
        o.append(f"- Lessons inbox: {h['lessons_to_review']} candidates marked review.")
    if h.get("watch_proposals"):
        o.append(f"- Watch proposals in {h['watch_report']}:" + "".join(f"\n  - {l}" for l in h["watch_proposals"]))
    for p in h.get("prompts_to_paste", []):
        o.append(f"- Prompt waiting to be pasted: {p}")
    if f.get("closed_since_last_run"):
        o += ["", "## Closed since the last run", ""] + [f"- {k}" for k in f["closed_since_last_run"]]
    return "\n".join(o) + "\n"


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "proj"
        repo.mkdir()
        for c in (["git", "init", "-q"], ["git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-q",
                                          "--allow-empty", "-m", "x"]):
            subprocess.run(c, cwd=repo, check=True)
        (repo / "a.txt").write_text("hi")
        facts = {"date": "2026-01-02", "repos": [f for f in (repo_facts(r) for r in find_repos([t], 2)) if f],
                 "prs": [], "memory": [], "progress": [], "harness": {}}
        assert len(facts["repos"]) == 1 and facts["repos"][0]["dirty"] == 1, facts
        assert facts["repos"][0]["remote"] is False and facts["repos"][0]["unpushed"] == 0, facts["repos"][0]
        assert open_lines("# x\n## Next\n- a\n- b\n## Done\n- c") == ["- a", "- b"]
        st = t / "state.json"
        stamp(facts, st, "2026-01-01")
        f2 = stamp(json.loads(json.dumps({**facts, "repos": [dict(facts["repos"][0], seen_days={})]})), st, "2026-01-07")
        assert f2["repos"][0]["seen_days"]["dirty"] == 6, f2["repos"][0]
        (repo / "a.txt").unlink()
        f3 = stamp({**facts, "repos": [repo_facts(repo)]}, st, "2026-01-08")
        assert any(k.startswith("dirty:") for k in f3["closed_since_last_run"]), f3["closed_since_last_run"]
        assert "## Repos" in render(f3)
        assert OPEN_MARK.search("open: pick a domain") and not OPEN_MARK.search("Open the file to read it")
    print("loose-ends self-test: ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--roots", nargs="*", default=[str(HOME)])
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-gh", action="store_true")
    ap.add_argument("--no-state", action="store_true", help="read only: do not update first-seen dates")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        sys.exit(self_test())
    facts = gather(a.roots, a.depth, not a.no_gh)
    if not a.no_state:
        facts = stamp(facts)
    print(json.dumps(facts, indent=1) if a.json else render(facts))
