#!/usr/bin/env python3
"""review3.py's rules on fixed cases: the 2-of-3 tally, twin merging, the diff parsers, and the merge gate itself:
the review-3 status post and prep set, the draft flag where the check cannot be required (through a fake `gh` on
PATH), and the CI rollups and draft state ready reads.

  python3 review3_test.py     prints what passed, or each case that drifted; exit 1 on any drift
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review3  # noqa: E402
from review3 import (check_blocks, consensus_table, diff_lines, drop_files, final_status, fingerprint, judge,  # noqa: E402
                     merge_twins, post, prep, tally)

SHA = "a" * 40
REVIEW_URL = "https://github.com/o/r/pull/7#pullrequestreview-1"
# a stand-in for gh: logs each call's args and stdin, prints the first canned reply whose key is in the args, cut to
# the fields --json asked for (so a field the code forgot to ask for is missing, as on GitHub); a reply
# {"fail": text} exits 1 with gh's error line instead, as `gh api` does on an HTTP error
FAKE_GH = """#!/usr/bin/env python3
import json, os, sys
home, args = os.environ["FAKE_GH_HOME"], " ".join(sys.argv[1:])
stdin = sys.stdin.read() if "--input" in sys.argv else ""
with open(os.path.join(home, "calls.jsonl"), "a") as log:
    log.write(json.dumps({"args": sys.argv[1:], "stdin": stdin}) + "\\n")
canned = json.load(open(os.path.join(home, "canned.json")))
reply = next((reply for key, reply in canned.items() if key in args), {})
if isinstance(reply, dict) and "fail" in reply:
    sys.exit("gh: " + reply["fail"])
if isinstance(reply, dict) and "--json" in sys.argv:
    wanted = sys.argv[sys.argv.index("--json") + 1].split(",")
    reply = {k: v for k, v in reply.items() if k in wanted}
print(reply if isinstance(reply, str) else json.dumps(reply))
"""


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
    bad += selftest_twins(f, v) + selftest_status() + selftest_drop() + selftest_tally()
    bad += selftest_post() + selftest_post_draft() + selftest_prep() + selftest_prep_restore()
    bad += selftest_check_blocks() + selftest_ready_draft() + selftest_next_steps() + selftest_hook()
    print("\n".join(bad) or f"selftest: {len(cases)} tally cases, twins, status, the diff parsers, the gate and the "
          "draft flag pass")
    sys.exit(1 if bad else 0)


def selftest_twins(f, v):
    cons = lambda i, s, line: judge(f(i, s, line, "nit"), [v("grug", True)], True)
    taste = lambda i, s, line: judge(f(i, s, line, "nit"), [v("grug", False)], True)
    cases = [  # rows -> (kept id, its also) per kept row
        ([taste("m3", "maintainability", 2), cons("o3", "ousterhout", 2)], [("o3", []), ("m3", [])]),
        ([cons("m4", "maintainability", 82), cons("o4", "ousterhout", 84)], [("m4", ["o4 (Ousterhout, line 84): o4"])]),
        ([cons("m7", "maintainability", 9), cons("g7", "grug", 9)], [("m7", ["g7 (grug): g7"])]),
        ([cons("g8", "grug", 10), cons("g9", "grug", 12)], [("g8", []), ("g9", [])]),
        ([cons("m5", "maintainability", 82), taste("o5", "ousterhout", 84)], [("m5", []), ("o5", [])]),
        ([cons("m6", "maintainability", 82), cons("o6", "ousterhout", 86)], [("m6", []), ("o6", [])]),
    ]
    got = [[(r["id"], r["also"]) for r in merge_twins(rows)] for rows, _ in cases]
    bad = [f"merge_twins: got {g}, want {want}" for g, (_, want) in zip(got, cases) if g != want]
    # a twin's title is agent text: a | or a line break in it must not split the table row
    row = merge_twins([cons("m8", "maintainability", 5), dict(cons("o8", "ousterhout", 5), title="a | b\nc")])
    table_row = consensus_table(row)[2]
    if table_row.replace("\\|", "").count("|") != consensus_table([])[0].count("|") or "\n" in table_row:
        bad.append(f"consensus_table: a twin title broke the row: {table_row!r}")
    return bad


def selftest_status():
    want = [({"blocking": 0, "consensus": 2, "taste": 1}, ("success", "0 blocking · 2 consensus · 1 taste calls")),
            ({"blocking": 2, "consensus": 3, "taste": 0}, ("failure", "2 blocking · 3 consensus · 0 taste calls"))]
    return [f"final_status{t}: got {final_status(t)}, want {w}" for t, w in want if final_status(t) != w]


def selftest_drop():
    patch = ("diff --git a/index.html b/index.html\n+++ b/index.html\n@@ -1 +1 @@\n+<p>\n"
             "diff --git a/build.py b/build.py\n+++ b/build.py\n@@ -1 +1 @@\n+x = 1\n")
    kept = drop_files(patch, {"index.html": "build.py"})
    return [] if diff_lines(kept) == {"build.py": {1}} else [f"drop_files kept: {diff_lines(kept)}"]


def write(run, name, data):
    Path(run, name).write_text(data if isinstance(data, str) else json.dumps(data))


def captured(fn, *args, **kw):
    """Run fn with stdout and stderr captured; return both."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        fn(*args, **kw)
    return out.getvalue(), err.getvalue()


def quiet(fn, *args, **kw):
    return captured(fn, *args, **kw)[0]


def tallied_run(run):
    """A run folder shaped as prep and review-3.js leave it, tallied: one blocker (2 of 3 important on a diff line)
    and one taste call. Returns the findings and votes it was built from."""
    f = lambda i, s, line, sev: {"file": "a.py", "line": line, "severity": sev, "title": i, "why": "w", "fix": "x",
                                 "id": i, "school": s}
    v = lambda i, agree, sev="nit": {"id": i, "agree": agree, "severity": sev, "reason": "r"}
    findings = [f("g1", "grug", 2, "important"), f("o1", "ousterhout", 3, "nit")]
    votes = {"grug": [v("o1", False)], "ousterhout": [v("g1", True, "important")],
             "maintainability": [v("g1", False), v("o1", False)]}
    write(run, "pr.json", {"headRefOid": SHA, "repo": "o/r", "number": 7, "url": "https://github.com/o/r/pull/7"})
    write(run, "diff.patch", "+++ b/a.py\n@@ -0,0 +1,3 @@\n+x = 1\n+y = 2\n+z = 3\n")
    write(run, "audit_new.txt", "")
    write(run, "raw.json", {"findings": findings, "votes": votes, "counts": fingerprint(findings, votes)})
    quiet(tally, run)
    return findings, votes


def selftest_tally():
    """tally end to end on a run folder shaped as review-3.js writes it: the raw.json contract, the copy check, the
    files the post reads, and a torn copy refused."""
    bad = []
    with tempfile.TemporaryDirectory() as run:
        findings, votes = tallied_run(run)
        t, comments = json.loads(Path(run, "tally.json").read_text()), json.loads(Path(run, "comments.json").read_text())
        got = (t["blocking"], t["consensus"], t["taste"], [c["line"] for c in comments])
        if got != (1, 1, 1, [2]):
            bad.append(f"tally end to end: got {got}, want (1, 1, 1, [2])")
        if "Not ready: 1 blocking" not in Path(run, "review.md").read_text():
            bad.append("tally end to end: review.md has no verdict line")
        torn = [{k: x for k, x in findings[0].items() if k != "school"}, findings[1]]  # what run 3's copy did
        write(run, "raw.json", {"findings": torn, "votes": votes, "counts": fingerprint(torn, votes)})
        try:
            tally(run)
            bad.append("tally accepted a raw.json that lost a key")
        except SystemExit:
            pass
    return bad


@contextlib.contextmanager
def fake_gh(canned):
    """FAKE_GH first on PATH for the block; yields a function returning the calls so far, oldest first."""
    with tempfile.TemporaryDirectory() as home:
        Path(home, "gh").write_text(FAKE_GH)
        Path(home, "gh").chmod(0o755)
        write(home, "canned.json", canned)
        old = dict(os.environ)
        os.environ.update(PATH=home + os.pathsep + old["PATH"], FAKE_GH_HOME=home)
        log = Path(home, "calls.jsonl")
        try:
            yield lambda: [json.loads(row) for row in log.read_text().splitlines()] if log.exists() else []
        finally:
            os.environ.clear()
            os.environ.update(old)


def statuses(calls):
    """The commit status calls among gh calls, as (state, context, sha, target_url)."""
    out = []
    for c in calls:
        a = c["args"]  # api repos/O/R/statuses/SHA -f k=v -f k=v ...
        if a[:1] == ["api"] and "/statuses/" in a[1]:
            fields = dict(kv.split("=", 1) for kv in a[3::2])
            out.append((fields["state"], fields["context"], a[1].rsplit("/", 1)[1], fields["target_url"]))
    return out


def selftest_post():
    """post files one COMMENT review on the head, then sets review-3 on that head: failure while a finding blocks,
    success at 0 blocking, each linked to the review."""
    bad = []
    with tempfile.TemporaryDirectory() as run, fake_gh({"pulls/7/reviews": {"html_url": REVIEW_URL, "id": 1}}) as calls:
        tallied_run(run)
        quiet(post, run)
        payload = json.loads(next(c["stdin"] for c in calls() if c["args"][1:2] == ["repos/o/r/pulls/7/reviews"]))
        if (payload["event"], payload["commit_id"]) != ("COMMENT", SHA):
            bad.append(f"post: review event {payload['event']} on {payload['commit_id'][:7]}, want COMMENT on the head")
        if statuses(calls()) != [("failure", "review-3", SHA, REVIEW_URL)]:
            bad.append(f"post with 1 blocking set {statuses(calls())}, want one review-3 failure on the head")
        t = json.loads(Path(run, "tally.json").read_text())
        write(run, "tally.json", dict(t, blocking=0, rows=[dict(r, blocking=False) for r in t["rows"]]))
        quiet(post, run, again=True)
        if statuses(calls())[1:] != [("success", "review-3", SHA, REVIEW_URL)]:
            bad.append(f"post with 0 blocking set {statuses(calls())[1:]}, want one review-3 success")
    return bad


def ready_calls(calls):
    """The `gh pr ready` calls among gh calls, each as its args after `ready`."""
    return [c["args"][2:] for c in calls if c["args"][:2] == ["pr", "ready"]]


def selftest_post_draft():
    """On a PR prep drafted (its mark exists), post marks it ready only at 0 blocking on the head the review read, and
    then drops the mark; with blockers, or a head pushed during the review, it stays a draft and keeps the mark. On a
    PR prep left alone (the check is required, or the author made the draft), post never touches the draft flag. A
    marked PR closed or merged during the review is left alone and its mark dropped, with one line saying so."""
    bad, undo, ready = [], [["7", "--repo", "o/r", "--undo"]], [["7", "--repo", "o/r"]]
    gone = "left #7 alone: it was {} during the review; dropped its draft mark"
    cases = [  # (marked, blocking, live head, live state) -> gh pr ready calls, mark kept, a line on stderr
        (True, 1, SHA, "OPEN", undo, True, ""), (True, 0, SHA, "OPEN", ready, False, ""),
        (True, 0, "b" * 40, "OPEN", undo, True, ""), (False, 1, SHA, "OPEN", [], False, ""),
        (False, 0, SHA, "OPEN", [], False, ""), (True, 0, SHA, "MERGED", [], False, gone.format("merged")),
        (True, 1, SHA, "CLOSED", [], False, gone.format("closed"))]
    for marked, blocking, head, state, want, kept, told in cases:
        canned = {"pulls/7/reviews": {"html_url": REVIEW_URL, "id": 1}, "pr view": {"headRefOid": head, "state": state}}
        with tempfile.TemporaryDirectory() as run, fake_gh(canned) as calls, runs_in(run):
            tallied_run(run)
            if marked:
                review3.draft_mark("o/r", 7).write_text(SHA)
            if not blocking:
                t = review3.load(run, "tally.json")
                write(run, "tally.json", dict(t, blocking=0, rows=[dict(r, blocking=False) for r in t["rows"]]))
            err = captured(post, run)[1]
            got = ready_calls(calls()), review3.draft_mark("o/r", 7).exists()
        if got != (want, kept) or told not in err.splitlines() + [""]:
            bad.append(f"post (marked {marked}, {blocking} blocking, head {head[:7]}, {state}): gh pr ready {got[0]}, "
                       f"mark {got[1]}, said {err!r}; want {want}, mark {kept}, {told!r}")
    return bad


def pr_clone(where):
    """A clone whose origin holds main and pull/7/head, as GitHub's does: what a fresh prep fetches and snapshots.
    Returns the clone and the PR's head sha."""
    def git(*args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=where, check=True,
                              capture_output=True, text=True).stdout.strip()
    git("init", "-q", "--bare", "origin.git")
    git("clone", "-q", "origin.git", "clone")
    for n, ref in ((1, "main"), (2, "refs/pull/7/head")):
        Path(where, "clone", "a.py").write_text(f'"""Say {n}."""\nprint({n})\n')
        git("-C", "clone", "add", "a.py")
        git("-C", "clone", "commit", "-qm", f"c{n}")
        git("-C", "clone", "push", "-q", "origin", f"HEAD:{ref}")
    return Path(where, "clone"), git("-C", "clone", "rev-parse", "HEAD")


@contextlib.contextmanager
def runs_in(folder):
    saved, review3.RUNS = review3.RUNS, Path(folder)
    try:
        yield
    finally:
        review3.RUNS = saved


def selftest_prep():
    """A fresh prep marks the head pending and asks the base branch's protection whether review-3 is required. Only a
    list naming it counts: then the draft flag is never touched. A 404 (no protection), a 403 (a private repo on the
    free plan), any other failure or a list without it writes the PR's mark and drafts it. An author's own draft is
    left alone and unmarked, with a line saying so, so post never readies it. Once marked, prep keeps the draft as its
    own: on a rerun or after a crash (still a draft) and in the next round (readied by `gh pr ready` to start it). A
    check required only by a ruleset counts: the protection endpoint answers 404 there, and the branch's rules name
    it (vercel/next.js read live, 2026-11-22)."""
    protected = {"contexts": ["review-3"], "checks": [{"context": "review-3", "app_id": None}]}
    free_plan = {"fail": "Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)"}
    gone = {"fail": "Not Found (HTTP 404)"}
    ruleset = lambda *names: [{"type": "deletion", "ruleset_id": 1}, {"type": "required_status_checks", "parameters": {
        "required_status_checks": [{"context": n} for n in names], "strict_required_status_checks_policy": False}}]
    author = "left #7 as the author's draft: post will not ready it"
    cases = [  # (protection, rules, already a draft, marked before) -> prep drafts and marks it, a line on stderr
        (gone, [], False, False, True, "drafting #7 while it is reviewed: main does not require review-3"),
        (free_plan, free_plan, False, False, True, "drafting #7 while it is reviewed: main cannot require review-3 "
         "here (gh: Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403))"),
        ({"fail": "Bad Gateway (HTTP 502)"}, [], False, False, True, ""),
        ({"contexts": ["python"], "checks": [{"context": "python", "app_id": 15368}]}, [], False, False, True, ""),
        (protected, [], False, False, False, ""), (gone, ruleset("python", "review-3"), False, False, False, ""),
        (gone, ruleset("python"), False, False, True, ""), (gone, [], True, False, False, author),
        (gone, [], True, True, True, ""), (gone, [], False, True, True, "")]
    bad = []
    with tempfile.TemporaryDirectory() as where:
        clone, head = pr_clone(where)
        pr_view = {"number": 7, "title": "t", "body": "", "url": "https://github.com/o/r/pull/7", "headRefOid": head,
                   "baseRefName": "main", "files": [{"path": "a.py"}], "author": {"login": "o"}, "isDraft": False}
        patch = "diff --git a/a.py b/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n-\"\"\"Say 1.\"\"\"\n+\"\"\"Say 2.\"\"\"\n"
        for i, (answer, rules, draft, marked, want, told) in enumerate(cases):
            canned = {"pr view": dict(pr_view, isDraft=draft), "required_status_checks": answer,
                      "rules/branches/main": rules, "pr diff": patch}
            with fake_gh(canned) as calls, runs_in(Path(where, f"runs{i}")):
                if marked:
                    Path(where, f"runs{i}").mkdir()
                    review3.draft_mark("o/r", 7).write_text(head)
                err = captured(prep, "o/r", 7, str(clone))[1]
                got = review3.draft_mark("o/r", 7).exists()
                drafts = ready_calls(calls())
                pending = statuses(calls())[:1] == [("pending", "review-3", head, pr_view["url"])]
            want_drafts = [["7", "--repo", "o/r", "--undo"]] if want else []
            if (got, drafts, pending) != (want, want_drafts, True) or told not in err.splitlines() + [""]:
                bad.append(f"prep with protection {answer}, rules {rules}, a draft already {draft}, marked {marked}: "
                           f"mark {got}, gh pr ready {drafts}, pending {pending}, said {err!r}; want mark {want}, "
                           f"{told!r}")
    return bad


def selftest_prep_restore():
    """prep on a head already posted puts that review's verdict back whole (a pending status from a rerun of prep
    would hold the merge forever): the status and, on a PR it drafted (marked), the draft flag, which heals a post cut
    off before its `gh pr ready`. It touches nothing else: no fetch, no snapshot, no new review."""
    pr_view = {"headRefOid": SHA, "url": "https://github.com/o/r/pull/7", "baseRefName": "main", "state": "OPEN"}
    with tempfile.TemporaryDirectory() as runs, fake_gh({"pr view": pr_view}) as calls, runs_in(runs):
        run = Path(runs, f"o-r-7-{SHA[:7]}")
        run.mkdir()
        write(run, "posted.json", {"url": REVIEW_URL, "id": 1, "head_sha": SHA})
        write(run, "pr.json", {"repo": "o/r", "number": 7, "headRefOid": SHA})
        review3.draft_mark("o/r", 7).write_text(SHA)
        write(run, "tally.json", {"head_sha": SHA, "blocking": 0, "consensus": 2, "taste": 1})
        try:
            out = quiet(prep, "o/r", 7, str(Path(runs, "no-clone")))  # a fetch here would fail: there is no clone
        except SystemExit as e:
            out = f"prep went on to review the head again: {e}"
        got = statuses(calls()), ready_calls(calls()), review3.draft_mark("o/r", 7).exists()
    want = [("success", "review-3", SHA, REVIEW_URL)], [["7", "--repo", "o/r"]], False
    told = str(run) in out and " ready " in out and "Workflow" not in out  # the head was reviewed: ready, no rerun
    return [] if got == want and told else [f"prep restore set {got}, printed {out!r}; want {want} and ready only"]


def selftest_ready_draft():
    """ready end to end on a PR still in draft after a blocking review: GitHub's isDraft reaches the gate, which
    blocks and says how the next round starts."""
    now = {"number": 7, "state": "OPEN", "isDraft": True, "baseRefName": "main", "headRefOid": SHA,
           "mergeable": "MERGEABLE", "files": [{"path": "a.py"}], "url": "https://github.com/o/r/pull/7",
           "statusCheckRollup": [{"__typename": "CheckRun", "name": "test", "status": "COMPLETED",
                                  "conclusion": "SUCCESS"}]}
    canned = {"pr view": now, "repo view": {"defaultBranchRef": {"name": "main"}}, "pr list": []}
    with tempfile.TemporaryDirectory() as run, fake_gh(canned), contextlib.redirect_stdout(io.StringIO()) as out:
        tallied_run(run)
        subprocess.run(["git", "init", "-q", run], check=True)
        write(run, "pr.json", dict(review3.load(run, "pr.json"), repo_dir=run))
        write(run, "posted.json", {"url": REVIEW_URL, "id": 1, "head_sha": SHA})
        try:
            review3.ready(run)
        except SystemExit:
            pass
    want = "BLOCK  still a draft: fix the blockers, then `gh pr ready 7` starts the next review"
    return [] if want in out.getvalue().splitlines() else [f"ready on a draft printed {out.getvalue()!r}; want {want!r}"]


def selftest_next_steps():
    """The Workflow call prep prints names the review-3.js beside review3.py and hands it review3.py's own resolved
    path, so the pair runs together wherever the skill is installed; the ready line splits back into its words in a
    shell, whatever the path holds (a space included)."""
    first, then = review3.next_steps(Path("/runs/o-r-7"), "o/r", 7).splitlines()
    m = re.fullmatch(r'next: Workflow\(\{scriptPath: ("(?:[^"\\]|\\.)*"), args: (\{.*\})\}\)', first)
    path, args = (json.loads(m[1]), json.loads(m[2])) if m else (None, None)
    here = Path(review3.__file__).resolve()
    want = {"run": "/runs/o-r-7", "repo": "o/r", "pr": 7, "script": str(here)}
    words = shlex.split(then.removeprefix("then: "))
    if path != str(here.with_name("review-3.js")) or args != want or words != ["python3", str(here), "ready", "/runs/o-r-7"]:
        return [f"next_steps printed {first!r} / {then!r}; want review-3.js and args {want}, then ready"]
    return []


def selftest_check_blocks():
    """ready's decision on fixed rollups shaped as `gh pr view --json statusCheckRollup` returns them: a CheckRun
    has status, then conclusion once COMPLETED; a StatusContext has state alone; review-3 is ready's own verdict."""
    run = lambda name, status, conclusion="": {"__typename": "CheckRun", "name": name, "status": status,
                                               "conclusion": conclusion}
    ctx = lambda name, state: {"__typename": "StatusContext", "context": name, "state": state}
    now = lambda rollup, head=SHA, draft=False: {"number": 7, "state": "OPEN", "isDraft": draft,
                                                 "baseRefName": "main", "mergeable": "MERGEABLE", "headRefOid": head,
                                                 "statusCheckRollup": rollup}
    clean = {"head_sha": SHA, "rows": []}
    no_ci = ["no CI checks on this PR: nothing but the review and the audit has run"]
    blocker = {"head_sha": SHA, "rows": [{"blocking": True, "title": "t", "file": "a.py", "line": 2}]}
    cases = [
        (clean, now([run("build", "IN_PROGRESS"), ctx("ci/lint", "PENDING"), ctx("review-3", "FAILURE"),
                     run("test", "COMPLETED", "SUCCESS")]),
         (["CI still running: build", "CI still running: ci/lint"], [])),
        (clean, now([run("test", "COMPLETED", "FAILURE"), ctx("ci/lint", "ERROR"), ctx("review-3", "PENDING"),
                     run("docs", "COMPLETED", "SKIPPED")]),
         (["CI failing: test", "CI failing: ci/lint"], [])),
        (clean, now([ctx("review-3", "SUCCESS")]), ([], no_ci)),
        (blocker, now([run("test", "COMPLETED", "SUCCESS")], head="b" * 40),
         ([f"review covers {SHA[:7]}, head is now bbbbbbb: review again", "blocking finding: t (a.py:2)"], [])),
        (blocker, now([run("test", "COMPLETED", "SUCCESS")], draft=True),
         (["still a draft: fix the blockers, then `gh pr ready 7` starts the next review",
           "blocking finding: t (a.py:2)"], [])),
        (clean, now([run("test", "COMPLETED", "SUCCESS")], draft=True),
         (["still a draft: `gh pr ready 7`, then run ready again"], [])),
    ]
    out = []
    for t, state, want in cases:
        got = check_blocks(t, state, "main")
        if got != want:
            out.append(f"check_blocks: got {got}, want {want}")
    return out


def selftest_hook():
    """review3-hook.py's nudge() end to end through the fake gh: after a push, GitHub's records decide. A refused push
    leaves the branch at the reviewed head (quiet); a PR GitHub has not moved yet to its branch's new commit gets a
    nudge naming that commit; a head with no review-3 status gets one naming the head. A PR from a fork reads its
    branch in the fork, never a branch of the same name in the base repo; a deleted fork falls back to the head."""
    spec = importlib.util.spec_from_file_location("review3_hook", Path(__file__).with_name("review3-hook.py"))
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    status = [{"__typename": "StatusContext", "context": "review-3", "state": "SUCCESS"}]
    view = lambda rollup, fork="o": {"number": 7, "url": "https://github.com/o/r/pull/7", "isDraft": False,
                                     "state": "OPEN", "headRefOid": SHA, "headRefName": "feat",
                                     "headRepository": {"name": "r"}, "headRepositoryOwner": {"login": fork},
                                     "statusCheckRollup": rollup}
    refs = lambda base, fork=None: {"repos/f/r/git/ref/heads/feat": fork, "repos/o/r/git/ref/heads/feat": base}
    cases = [(view(status), refs(SHA), None), (view(status), refs("b" * 40), "bbbbbbb"), (view([]), refs(SHA), SHA[:7]),
             (view(status, fork="f"), refs("c" * 40, fork=SHA), None),  # base's own feat moved, the fork's did not
             (view(status, fork="f"), refs(SHA, fork="b" * 40), "bbbbbbb"),
             (dict(view([]), headRepository=None, headRepositoryOwner=None), refs("b" * 40), SHA[:7]),
             (dict(view(status), headRepository=None, headRepositoryOwner=None), refs("b" * 40), None)]
    bad = []
    with tempfile.TemporaryDirectory() as where:
        for pr_view, branch, want in cases:
            with fake_gh({"pr view": pr_view, "config get user": "o", **branch}):
                line = hook.nudge({"tool_input": {"command": "git push -q origin feat"}, "cwd": where})
            got = line and line.split(" head ")[1][:7]
            if got != want:
                bad.append(f"hook: branches {branch}, PR head {SHA[:7]}: nudged about {got}, want {want}")
    return bad


if __name__ == "__main__":
    selftest()
