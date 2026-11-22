#!/usr/bin/env python3
"""Prepare, tally, post and gate a pull-request review by three reviewers of different schools.

The judgement comes from three agents (the review-3 workflow); everything with one right answer lives here:
the PR's facts, the audit delta, the 2-of-3 tally, the one GitHub review and the merge gate.

  prep  OWNER/REPO N --repo-dir DIR   snapshot head and base, save the diff and the audit delta; prints the run folder
  tally RUN                           RUN/raw.json (findings + votes) -> tally.json, review.md, comments.json
  post  RUN [--again]                 one COMMENT review: the body, plus inline comments on consensus lines only
  ready RUN                           merge gate; exit 0 only when nothing blocks, and print the merge command
  selftest                            the tally rules on a fixed case; exit 1 if they drift

Rules: 2 of 3 schools agreeing is a consensus finding (act on it); 2 of 3 calling it important blocks the merge;
1 of 3 is a taste call, listed and never blocking. Findings on the same file:line merge into one row, as do
consensus findings within NEAR lines of each other; a finding on a line outside the diff (a doc the PR left stale)
goes in the review body instead of inline. The verdict is also the `review-3` commit status on the head: pending from
prep, success at 0 blocking after post, failure otherwise. Make it a required check and GitHub's merge button waits.
review3-hook.py, beside this file, tells a session to start a review when a PR gets a new head.
"""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

SCHOOLS = ("grug", "ousterhout", "maintainability")
SCHOOL_NAME = {"grug": "grug", "ousterhout": "Ousterhout", "maintainability": "maintainability"}
MARK = {"important": "🔴", "nit": "🟡"}
STATUS = "review-3"  # the commit status context; branch protection requires it by this name
NEAR = 3  # lines: two consensus findings this close in one file are one problem (a run had twins at :82 and :84)
RUNS = Path.home() / ".claude" / "review3"
AUDIT = Path(__file__).with_name("code_audit.py")
PASSING = {"SUCCESS", "NEUTRAL", "SKIPPED"}


def sh(*cmd, cwd=None, stdin=None):
    """Run a command and return stdout; raise with stderr in the message when it fails."""
    p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"{' '.join(map(str, cmd))} failed ({p.returncode}): {p.stderr.strip()[:500]}")
    return p.stdout


def gh_json(*cmd):
    return json.loads(sh("gh", *cmd))


def load(run, name):
    return json.loads((Path(run) / name).read_text())


def save(run, name, data):
    path = Path(run) / name
    path.write_text(data if isinstance(data, str) else json.dumps(data, indent=1, ensure_ascii=False))
    return path


# ---------- prep: the facts the reviewers read ----------

def prep(repo, pr, repo_dir):
    """Mark the head pending, snapshot it and its merge base, save the diff and the audit findings new in the head."""
    info = gh_json("pr", "view", str(pr), "--repo", repo, "--json",
                   "number,title,body,url,headRefOid,baseRefName,files,author")
    sha = info["headRefOid"]
    run = RUNS / f"{repo.replace('/', '-')}-{pr}-{sha[:7]}"
    if (run / "posted.json").exists():  # this head was reviewed: restore its verdict rather than review it twice
        posted = load(run, "posted.json")
        set_status(repo, sha, *final_status(load(run, "tally.json")), posted["url"])
        print(f"already reviewed at {sha[:7]}: {posted['url']}; skip the workflow and run ready", file=sys.stderr)
        print(run)
        return
    set_status(repo, sha, "pending", "three reviewers are reading this head", info["url"])
    sh("git", "-C", repo_dir, "fetch", "-q", "origin", f"pull/{pr}/head", info["baseRefName"])
    base_sha = sh("git", "-C", repo_dir, "merge-base", sha, f"origin/{info['baseRefName']}").strip()
    run.mkdir(parents=True, exist_ok=True)
    snapshot(repo_dir, sha, run / "head")
    snapshot(repo_dir, base_sha, run / "base")
    new, built = audit_delta(run / "base", run / "head")
    save(run, "generated.txt", "".join(f"{page}  made by {src}\n" for page, src in sorted(built.items())))
    save(run, "diff.patch", drop_files(sh("gh", "pr", "diff", str(pr), "--repo", repo), built))
    save(run, "audit_new.txt", "\n".join(new) + "\n" if new else "")
    info.update(repo=repo, repo_dir=str(Path(repo_dir).resolve()), base_sha=base_sha, run=str(run),
                files=[f["path"] for f in info["files"]], author=info["author"]["login"])
    save(run, "pr.json", info)
    print(run)


def snapshot(repo_dir, sha, dest):
    """A throwaway clone at one commit; --shared borrows the objects, so it is fast and registers nothing."""
    if dest.exists():
        return
    sh("git", "clone", "-q", "--shared", "--no-checkout", str(repo_dir), str(dest))
    sh("git", "-C", str(dest), "checkout", "-q", "--detach", sha)


def audit_findings(repo):
    """code_audit.py on one tree: its built pages (page -> the script that makes it) and its findings, keyed so a
    line shift alone does not make a finding new."""
    spec = importlib.util.spec_from_file_location("code_audit", AUDIT)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    opts = SimpleNamespace(fn_lines=60, file_lines=500, dup_lines=8, top_level=15, binary_kb=1024)
    built, res, _, _ = audit.audit(str(repo), opts)
    return built, {(rule, path, re.sub(r"\d+", "#", msg)): f"{rule:8}{path}:{line}  {msg}"
                   for rule, hits in res.items() for path, line, msg in hits}


def audit_delta(base, head):
    """The findings new in head, and head's built pages."""
    (_, before), (built, after) = audit_findings(base), audit_findings(head)
    return sorted(text for key, text in after.items() if key not in before), built


def drop_files(patch, paths):
    """The diff without the sections for these files. Reviewers judge a built page at the script that builds it,
    and a built page's diff can be most of a PR's tokens (5k lines on one run)."""
    sections = re.split(r"(?m)^(?=diff --git )", patch)
    return "".join(s for s in sections if (m := re.match(r"diff --git a/\S+ b/(\S+)", s)) is None
                   or m.group(1) not in paths)


def diff_lines(patch):
    """Lines on the new side of each hunk, per file: the lines GitHub accepts inline comments on."""
    lines, path, n = {}, None, 0
    for row in patch.splitlines():
        if row.startswith("+++ "):
            path = row[6:] if row.startswith("+++ b/") else None
            continue
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", row)
        if hunk:
            n = int(hunk.group(1))
        elif path and row[:1] in (" ", "+") and not row.startswith("+++"):
            lines.setdefault(path, set()).add(n)
            n += 1
    return lines


# ---------- tally: 2 of 3, in code ----------

def judge(finding, votes, in_diff):
    """One finding plus the other schools' votes -> its kind, severity and whether it blocks."""
    agree = [{"school": finding["school"], "severity": finding["severity"], "reason": "raised it"}]
    agree += [v for v in votes if v["agree"]]
    dissent = [v for v in votes if not v["agree"]]
    voted = {finding["school"]} | {v["school"] for v in votes}
    kind = "consensus" if len(agree) >= 2 else "taste"
    important = sum(a["severity"] == "important" for a in agree)
    severity = "important" if important >= 2 else "nit"
    return dict(finding, agree=agree, dissent=dissent, kind=kind, severity=severity, in_diff=in_diff,
                abstained=[s for s in SCHOOLS if s not in voted],
                blocking=kind == "consensus" and severity == "important")


def tally(run):
    if (Path(run) / "posted.json").exists():  # a new tally would no longer match the review on GitHub
        raise SystemExit(f"already posted: {load(run, 'posted.json')['url']}; tally would overwrite what it says")
    raw, pr = load(run, "raw.json"), load(run, "pr.json")
    findings, votes = raw["findings"], raw["votes"]
    counted = {"findings": len(findings), "votes": sum(len(v) for v in votes.values())}
    if raw.get("counts") != counted:
        raise SystemExit(f"raw.json was not copied whole: says {raw.get('counts')}, holds {counted}")
    lines = diff_lines((Path(run) / "diff.patch").read_text())
    by_id = {}
    for school, ballot in votes.items():
        for v in ballot:
            by_id.setdefault(v["id"], []).append(dict(v, school=school))
    rows = merge_twins([judge(f, by_id.get(f["id"], []), f["line"] in lines.get(f["file"], ())) for f in findings])
    result = {"head_sha": pr["headRefOid"], "rows": rows, "summaries": raw.get("summaries", {}),
              "missing_reviewers": raw.get("missing_reviewers", []),
              "blocking": sum(r["blocking"] for r in rows),
              "consensus": sum(r["kind"] == "consensus" for r in rows),
              "taste": sum(r["kind"] == "taste" for r in rows)}
    save(run, "tally.json", result)
    save(run, "review.md", render_body(pr, result, (Path(run) / "audit_new.txt").read_text().splitlines()))
    save(run, "comments.json", inline_comments(rows))
    print(f"{result['blocking']} blocking, {result['consensus']} consensus, {result['taste']} taste calls")


def is_twin(kept, r):
    """Two consensus findings in one file within NEAR lines (the same line included): one problem, raised twice."""
    return (kept["file"] == r["file"] and abs(kept["line"] - r["line"]) <= NEAR
            and kept["kind"] == r["kind"] == "consensus")


def merge_twins(rows):
    """One row per problem: keep the strongest of each set of twins and note each other's id, line and title, so
    nothing raised drops out of the review. Taste calls never merge: each is one reviewer's separate opinion."""
    kept = []
    for r in sorted(rows, key=lambda r: (r["kind"] != "consensus", not r["blocking"], -len(r["agree"]))):
        twin = next((k for k in kept if is_twin(k, r)), None)
        if twin is None:
            kept.append(dict(r, also=[]))
            continue
        moved = "" if twin["line"] == r["line"] else f", line {r['line']}"
        twin["also"].append(f"{r['id']} ({SCHOOL_NAME[r['school']]}{moved}): {r['title']}")
    return kept


# ---------- render: one review a person reads in a minute ----------

def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def names(votes):
    return ", ".join(SCHOOL_NAME[v["school"]] for v in votes) or "nobody"


def consensus_table(rows):
    out = ["| | Finding | Where | Agree | Dissent |", "|---|---|---|---|---|"]
    for r in rows:
        dissent = "; ".join(f"{SCHOOL_NAME[v['school']]}: {v['reason']}" for v in r["dissent"]) or "none"
        where = f"`{r['file']}:{r['line']}`" + ("" if r["in_diff"] else " (outside the diff)")
        also = f" Also raised as {'; '.join(r['also'])}." if r["also"] else ""
        out.append(f"| {MARK[r['severity']]} | **{cell(r['title'])}** {cell(r['fix'])}{also} | {where} "
                   f"| {len(r['agree'])}/3 {names(r['agree'])} | {cell(dissent)} |")
    return out


def taste_table(rows):
    out = ["| Reviewer | Position | Why | The other two |", "|---|---|---|---|"]
    for r in rows:
        others = "; ".join(f"{SCHOOL_NAME[v['school']]}: {v['reason']}" for v in r["dissent"]) or "did not vote"
        out.append(f"| {SCHOOL_NAME[r['school']]} | **{cell(r['title'])}** `{r['file']}:{r['line']}` "
                   f"| {cell(r['why'])} | {cell(others)} |")
    return out


def verdict_line(t):
    if t["blocking"]:
        return f"**Not ready: {t['blocking']} blocking.**"
    return "**No blockers.** The review passes; `review3.py ready` checks CI, conflicts and other sessions."


def render_body(pr, t, audit_new):
    rows = t["rows"]
    cons = [r for r in rows if r["kind"] == "consensus"]
    taste = [r for r in rows if r["kind"] == "taste"]
    out = ["## Review by three: grug · Ousterhout · maintainability", "",
           f"{verdict_line(t)} {t['blocking']} blocking · {t['consensus']} consensus · {t['taste']} taste calls "
           f"· head `{t['head_sha'][:7]}`", "",
           "Two of three agreeing makes a finding; two of three calling it important blocks the merge. "
           "One of three is a taste call: listed for you, never blocking. Votes were blind.", ""]
    if t["missing_reviewers"]:
        out += [f"Missing reviewer: {', '.join(t['missing_reviewers'])} (its votes count as abstentions).", ""]
    out += ["### Consensus", ""] + (consensus_table(cons) if cons else ["None."]) + [""]
    out += ["### Taste calls (your call, never blocking)", ""] + (taste_table(taste) if taste else ["None."]) + [""]
    out += details("Audit delta: code_audit.py findings new in this PR", audit_new or ["None new."])
    out += details("Each reviewer in one line", [f"- **{SCHOOL_NAME.get(s, s)}**: {cell(v)}"
                                                 for s, v in t["summaries"].items()])
    stamp = {k: t[k] for k in ("blocking", "consensus", "taste")} | {"head": t["head_sha"]}
    return "\n".join(out + [f"<!-- review3 {json.dumps(stamp)} -->", ""])


def details(summary, lines):
    body = ["```", *lines, "```"] if lines and not lines[0].startswith("- ") else lines
    return [f"<details><summary>{summary}</summary>", "", *body, "", "</details>", ""]


def inline_comments(rows):
    """Inline comments for consensus findings on diff lines only; taste calls stay in the table."""
    out = []
    for r in rows:
        if r["kind"] != "consensus" or not r["in_diff"]:
            continue
        label = "Important, blocks merge" if r["blocking"] else "Nit, fix if cheap"
        body = (f"{MARK[r['severity']]} **{label}** · {len(r['agree'])}/3 agree ({names(r['agree'])})\n\n"
                f"**{r['title']}**\n\n{r['why']}\n\nFix: {r['fix']}")
        if r["dissent"]:
            body += "\n\nDissent: " + "; ".join(f"{SCHOOL_NAME[v['school']]}: {v['reason']}" for v in r["dissent"])
        out.append({"path": r["file"], "line": r["line"], "side": "RIGHT", "body": body})
    return out


# ---------- post: one review on GitHub ----------

def private_hits(run, repo, text):
    """What the PR head's own tests/privacy.py finds in the review (emails, home paths, private words), so the word
    list has one parser. Only claude-code-learns has that check; there, a missing one refuses the post."""
    if not repo.endswith("/claude-code-learns"):
        return []
    checker = Path(run) / "head" / "tests" / "privacy.py"
    spec = importlib.util.spec_from_file_location("privacy", checker)
    privacy = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(privacy)
        own, word = privacy.own_address_rx(repo.split("/")[0]), privacy.word_rx(privacy.private_words())
    except (OSError, AttributeError) as e:
        raise SystemExit(f"cannot run {checker} ({e}): the review was not checked for private words, not posted")
    return sorted({kind for line in text.splitlines() for kind in privacy.leaks(line, own, word)})


def post(run, again=False):
    pr, t = load(run, "pr.json"), load(run, "tally.json")
    if (Path(run) / "posted.json").exists() and not again:
        raise SystemExit(f"already posted: {load(run, 'posted.json')['url']} (pass --again to post another)")
    body, comments = (Path(run) / "review.md").read_text(), load(run, "comments.json")
    hits = private_hits(run, pr["repo"], body + "\n" + "\n".join(c["body"] for c in comments))
    if hits:
        raise SystemExit(f"the review holds {', '.join(hits)}: not posted")
    payload = {"commit_id": t["head_sha"], "event": "COMMENT", "body": body, "comments": comments}
    endpoint = f"repos/{pr['repo']}/pulls/{pr['number']}/reviews"
    p = subprocess.run(["gh", "api", endpoint, "--input", "-"], input=json.dumps(payload), capture_output=True, text=True)
    if p.returncode and comments:
        print(f"inline comments refused ({p.stdout.strip()[:300]}); posting them in the body instead", file=sys.stderr)
        payload.update(comments=[], body=body + "\n### Inline (GitHub refused the line positions)\n\n" +
                       "\n\n".join(f"`{c['path']}:{c['line']}` {c['body']}" for c in comments))
        p = subprocess.run(["gh", "api", endpoint, "--input", "-"], input=json.dumps(payload), capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"post failed: {p.stdout.strip()[:500]} {p.stderr.strip()[:300]}")
    review = json.loads(p.stdout)
    save(run, "posted.json", {"url": review["html_url"], "id": review["id"], "head_sha": t["head_sha"]})
    set_status(pr["repo"], t["head_sha"], *final_status(t), review["html_url"])
    print(review["html_url"])


def final_status(t):
    """The review-3 state and description a tally earns: success at 0 blocking, failure otherwise."""
    counts = f"{t['blocking']} blocking · {t['consensus']} consensus · {t['taste']} taste calls"
    return ("failure" if t["blocking"] else "success"), counts


def set_status(repo, sha, state, description, url):
    """The review-3 commit status on one sha: what a required check on the default branch waits for."""
    sh("gh", "api", f"repos/{repo}/statuses/{sha}", "-f", f"state={state}", "-f", f"context={STATUS}",
       "-f", f"description={description[:140]}", "-f", f"target_url={url}")


# ---------- ready: the merge gate ----------

def pr_state(repo, number):
    """The PR as GitHub sees it now; mergeable is computed lazily, so ask again while it reads UNKNOWN."""
    fields = "state,baseRefName,headRefOid,mergeable,statusCheckRollup,files,url"
    for _ in range(4):
        state = gh_json("pr", "view", str(number), "--repo", repo, "--json", fields)
        if state["mergeable"] != "UNKNOWN":
            break
        time.sleep(3)
    return state


def check_blocks(t, now, default):
    blocks, warns = [], []
    if now["state"] != "OPEN":
        blocks.append(f"PR is {now['state']}")
    if now["baseRefName"] != default:
        blocks.append(f"based on {now['baseRefName']}, not {default}: retarget it first")
    if now["mergeable"] != "MERGEABLE":
        blocks.append(f"mergeable is {now['mergeable']}: bring {default} into the branch and resolve")
    if now["headRefOid"] != t["head_sha"]:
        blocks.append(f"review covers {t['head_sha'][:7]}, head is now {now['headRefOid'][:7]}: review again")
    blocks += [f"blocking finding: {r['title']} ({r['file']}:{r['line']})" for r in t["rows"] if r["blocking"]]
    # review-3 is this script's own status, and its verdict is already in the blocking findings above
    checks = [c for c in now["statusCheckRollup"] or [] if c.get("context") != STATUS]
    failing = [c.get("name") or c.get("context") for c in checks
               if (c.get("conclusion") or c.get("state")) not in PASSING | {None, "PENDING", "EXPECTED"}]
    pending = [c.get("name") or c.get("context") for c in checks
               if c.get("status") not in (None, "COMPLETED") or c.get("state") in ("PENDING", "EXPECTED")]
    blocks += [f"CI failing: {n}" for n in failing] + [f"CI still running: {n}" for n in pending]
    if not checks:
        warns.append("no CI checks on this PR: nothing but the review and the audit has run")
    return blocks, warns


def collisions(pr, now):
    """Warnings, not blocks: other open PRs editing the same files, and uncommitted edits to them in worktrees."""
    mine, warns = {f["path"] for f in now["files"]}, []
    others = gh_json("pr", "list", "--repo", pr["repo"], "--state", "open", "--json", "number,title,files")
    for o in others:
        shared = mine & {f["path"] for f in o["files"]}
        if o["number"] != pr["number"] and shared:
            first, second = sorted((o["number"], pr["number"]))
            warns.append(f"#{o['number']} also edits {', '.join(sorted(shared))}: merge #{first} first, "
                         f"then bring main into #{second}")
    porcelain = sh("git", "-C", pr["repo_dir"], "worktree", "list", "--porcelain")
    for tree in re.findall(r"^worktree (.+)$", porcelain, re.M):
        if not Path(tree).exists():
            continue
        dirty = {line[3:] for line in sh("git", "-C", tree, "status", "--porcelain").splitlines()}
        if dirty & mine:
            warns.append(f"uncommitted edits to {', '.join(sorted(dirty & mine))} in {tree}: a session may be working there")
    return warns


def ready(run):
    pr, t = load(run, "pr.json"), load(run, "tally.json")
    now = pr_state(pr["repo"], pr["number"])
    default = gh_json("repo", "view", pr["repo"], "--json", "defaultBranchRef")["defaultBranchRef"]["name"]
    blocks, warns = check_blocks(t, now, default)
    warns += collisions(pr, now)
    save(run, "ready.json", {"blocks": blocks, "warns": warns, "head_sha": now["headRefOid"]})
    for b in blocks:
        print(f"BLOCK  {b}")
    for w in warns:
        print(f"WARN   {w}")
    if blocks:
        print(f"NOT READY: {len(blocks)} blocking")
        sys.exit(1)
    print(f"READY: gh pr merge {pr['number']} --repo {pr['repo']} --squash --match-head-commit {now['headRefOid']}")


# ---------- selftest: the rules on a fixed case ----------

def selftest():
    patch = "+++ b/a.py\n@@ -0,0 +1,3 @@\n+x = 1\n+y = 2\n+z = 3\n"
    lines = diff_lines(patch)
    f = lambda i, s, line, sev: {"id": i, "school": s, "file": "a.py", "line": line, "severity": sev, "title": i,
                                  "why": "", "fix": ""}
    v = lambda s, agree, sev="nit": {"school": s, "agree": agree, "severity": sev, "reason": "r"}
    cases = [
        (f("g1", "grug", 2, "important"), [v("ousterhout", True, "important"), v("maintainability", False)],
         ("consensus", "important", True)),
        (f("g2", "grug", 2, "important"), [v("ousterhout", True, "nit"), v("maintainability", False)],
         ("consensus", "nit", False)),
        (f("o1", "ousterhout", 3, "nit"), [v("grug", False), v("maintainability", False)], ("taste", "nit", False)),
        (f("m1", "maintainability", 9, "important"), [v("grug", True, "important")], ("consensus", "important", True)),
        (f("m2", "maintainability", 1, "important"), [], ("taste", "nit", False)),
    ]
    bad = []
    for finding, votes, want in cases:
        r = judge(finding, votes, finding["line"] in lines.get("a.py", ()))
        if (r["kind"], r["severity"], r["blocking"]) != want:
            bad.append(f"{finding['id']}: got {(r['kind'], r['severity'], r['blocking'])}, want {want}")
    if lines != {"a.py": {1, 2, 3}}:
        bad.append(f"diff_lines: {lines}")
    bad += selftest_twins(f, v) + selftest_status() + selftest_drop()
    print("\n".join(bad) or f"selftest: {len(cases)} tally cases, twins, status and the diff parsers pass")
    sys.exit(1 if bad else 0)


def selftest_twins(f, v):
    cons = lambda i, s, line: judge(f(i, s, line, "nit"), [v("grug", True)], True)
    taste = lambda i, s, line: judge(f(i, s, line, "nit"), [v("grug", False)], True)
    cases = [  # rows -> (kept id, its also) per kept row
        ([taste("m3", "maintainability", 2), cons("o3", "ousterhout", 2)], [("o3", []), ("m3", [])]),
        ([cons("m4", "maintainability", 82), cons("o4", "ousterhout", 84)], [("m4", ["o4 (Ousterhout, line 84): o4"])]),
        ([cons("m7", "maintainability", 9), cons("g7", "grug", 9)], [("m7", ["g7 (grug): g7"])]),
        ([cons("m5", "maintainability", 82), taste("o5", "ousterhout", 84)], [("m5", []), ("o5", [])]),
        ([cons("m6", "maintainability", 82), cons("o6", "ousterhout", 86)], [("m6", []), ("o6", [])]),
    ]
    got = [[(r["id"], r["also"]) for r in merge_twins(rows)] for rows, _ in cases]
    return [f"merge_twins: got {g}, want {want}" for g, (_, want) in zip(got, cases) if g != want]


def selftest_status():
    want = [({"blocking": 0, "consensus": 2, "taste": 1}, ("success", "0 blocking · 2 consensus · 1 taste calls")),
            ({"blocking": 2, "consensus": 3, "taste": 0}, ("failure", "2 blocking · 3 consensus · 0 taste calls"))]
    return [f"final_status{t}: got {final_status(t)}, want {w}" for t, w in want if final_status(t) != w]


def selftest_drop():
    patch = ("diff --git a/index.html b/index.html\n+++ b/index.html\n@@ -1 +1 @@\n+<p>\n"
             "diff --git a/build.py b/build.py\n+++ b/build.py\n@@ -1 +1 @@\n+x = 1\n")
    kept = drop_files(patch, {"index.html": "build.py"})
    return [] if diff_lines(kept) == {"build.py": {1}} else [f"drop_files kept: {diff_lines(kept)}"]


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("prep")
    a.add_argument("repo")
    a.add_argument("pr", type=int)
    a.add_argument("--repo-dir", required=True, help="a local clone of the repo")
    for name in ("tally", "post", "ready"):
        sub.add_parser(name).add_argument("run")
    sub.choices["post"].add_argument("--again", action="store_true")
    sub.add_parser("selftest")
    args = p.parse_args()
    if args.cmd == "prep":
        prep(args.repo, args.pr, args.repo_dir)
    elif args.cmd == "post":
        post(args.run, args.again)
    elif args.cmd == "selftest":
        selftest()
    else:
        {"tally": tally, "ready": ready}[args.cmd](args.run)


if __name__ == "__main__":
    main()
