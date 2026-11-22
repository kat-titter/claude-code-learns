#!/usr/bin/env python3
"""review3.py's rules on fixed cases: the 2-of-3 tally, twin merging, the commit status and the diff parsers.

  python3 review3_test.py     prints what passed, or each case that drifted; exit 1 on any drift
"""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review3 import diff_lines, drop_files, final_status, fingerprint, judge, merge_twins, tally  # noqa: E402


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
    print("\n".join(bad) or f"selftest: {len(cases)} tally cases, twins, status and the diff parsers pass")
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



def selftest_tally():
    """tally end to end on a run folder shaped as review-3.js writes it: the raw.json contract, the copy check, the
    files the post reads. One blocker (2 of 3 important on a diff line), one taste call, and a torn copy refused."""
    f = lambda i, s, line, sev: {"file": "a.py", "line": line, "severity": sev, "title": i, "why": "w", "fix": "x",
                                 "id": i, "school": s}
    v = lambda i, agree, sev="nit": {"id": i, "agree": agree, "severity": sev, "reason": "r"}
    findings = [f("g1", "grug", 2, "important"), f("o1", "ousterhout", 3, "nit")]
    votes = {"grug": [v("o1", False)], "ousterhout": [v("g1", True, "important")],
             "maintainability": [v("g1", False), v("o1", False)]}
    bad = []
    with tempfile.TemporaryDirectory() as run:
        write = lambda name, data: Path(run, name).write_text(data if isinstance(data, str) else json.dumps(data))
        write("pr.json", {"headRefOid": "a" * 40})
        write("diff.patch", "+++ b/a.py\n@@ -0,0 +1,3 @@\n+x = 1\n+y = 2\n+z = 3\n")
        write("audit_new.txt", "")
        write("raw.json", {"findings": findings, "votes": votes, "counts": fingerprint(findings, votes)})
        with contextlib.redirect_stdout(io.StringIO()):
            tally(run)
        t, comments = json.loads(Path(run, "tally.json").read_text()), json.loads(Path(run, "comments.json").read_text())
        got = (t["blocking"], t["consensus"], t["taste"], [c["line"] for c in comments])
        if got != (1, 1, 1, [2]):
            bad.append(f"tally end to end: got {got}, want (1, 1, 1, [2])")
        if "Not ready: 1 blocking" not in Path(run, "review.md").read_text():
            bad.append("tally end to end: review.md has no verdict line")
        torn = [{k: x for k, x in findings[0].items() if k != "school"}, findings[1]]  # what run 3's copy did
        write("raw.json", {"findings": torn, "votes": votes, "counts": fingerprint(torn, votes)})
        try:
            tally(run)
            bad.append("tally accepted a raw.json that lost a key")
        except SystemExit:
            pass
    return bad


if __name__ == "__main__":
    selftest()
