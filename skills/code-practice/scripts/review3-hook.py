#!/usr/bin/env python3
"""PostToolUse hook on Bash: when a command opens, readies or pushes to a pull request, ask for a review by three.

It prints one line of context, and only for an open, non-draft PR in a repo the gh user owns whose head has no
review-3 status yet; on every other command it prints nothing (about 45 ms). GitHub's status is the record of a
reviewed head, so the hook never reads push output: a push that changed nothing, was refused or printed nothing (-q)
leaves a head that has its status or does not. It never blocks and always exits 0. Keep a PR in draft while pushing
fixes and it stays quiet; `gh pr ready` starts the review. The review itself is review3.py and the review-3 workflow.

  settings.json: "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "timeout": 15,
                  "command": "python3 \"$HOME/.claude/skills/code-practice/scripts/review3-hook.py\""}]}]
  python3 review3-hook.py --test     the command parser and the PR-head rule on fixed cases; exit 1 if they drift
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW3 = HERE / "review3.py"
sys.path.insert(0, str(HERE))
PR_URL = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+")
# a command starts a line or follows ; & | or (, so a push on the last line of a multi-line command counts
CREATE = re.compile(r"(?:^|[;&|(]\s*)gh\s+pr\s+create\b", re.M)
READY = re.compile(r"(?:^|[;&|(]\s*)gh\s+pr\s+ready\b([^;&|)\n]*)", re.M)
PUSH = re.compile(r"(?:^|[;&|(]\s*)git((?:\s+-C\s+\S+)?)\s+push\b([^;&|)\n]*)", re.M)
CD = re.compile(r"(?:^|[;&|]\s*)cd\s+(\S+)\s*&&", re.M)


def target(command, output):
    """Which PR a Bash command opened, readied or pushed to, as (what `gh pr view` takes: a URL, number,
    branch or "" for the current branch; the folder to ask in, or None for the session's; the local ref a push sent,
    or None). None when it did none."""
    if CREATE.search(command):
        url = PR_URL.search(output)
        return (url.group(0) if url else "", None, None)
    ready = READY.search(command)
    if ready:
        args = ready.group(1).split()
        return None if "--undo" in args else (next((a for a in args if not a.startswith("-")), ""), None, None)
    push = PUSH.search(command)
    if push is None:
        return None
    args = push.group(2).split()
    if any(a in ("--delete", "-d", "--tags", "--dry-run", "-n") or a.startswith(":") for a in args):
        return None
    named = [a for a in args if not a.startswith("-")]  # remote, then refspec (local:remote, or one name for both)
    sent, branch = (named[1].split(":")[0], named[1].split(":")[-1]) if len(named) > 1 else ("HEAD", "")
    cd = CD.search(command)
    where = push.group(1).split()[-1] if push.group(1) else (cd.group(1) if cd else None)
    return ("" if branch == "HEAD" else branch, where, sent)


def needs_review(pr, owner, pushed=None):
    """True for an open, non-draft PR in a repo the gh user owns whose head has no review-3 status: not reviewed,
    and no review running (prep sets pending first). pushed is the commit a push just sent: GitHub moves the PR to it
    a moment after the push, so while it still reports another head, the pushed commit is the unreviewed one."""
    from review3 import STATUS  # here, not at the top: most Bash calls never get this far
    contexts = {c.get("context") for c in pr.get("statusCheckRollup") or []}
    lagging = pushed is not None and pushed != pr["headRefOid"]
    return (pr["state"] == "OPEN" and not pr["isDraft"] and pr["url"].split("/")[3] == owner
            and (lagging or STATUS not in contexts))


def nudge(d):
    """The one line for this hook input, or None."""
    res = d.get("tool_response") or {}
    out = res if isinstance(res, str) else f"{res.get('stdout', '')}\n{res.get('stderr', '')}"
    hit = target((d.get("tool_input") or {}).get("command", ""), out)
    if hit is None:
        return None
    selector, where, sent = hit
    where = os.path.abspath(os.path.expanduser((where or d.get("cwd") or ".").strip("'\"")))
    # four calls at most, each well inside the 15 s hook timeout
    run = lambda *cmd: subprocess.run(cmd, cwd=where, capture_output=True, text=True, timeout=4)
    view = run("gh", "pr", "view", *([selector] if selector else []), "--json",
               "number,url,isDraft,state,headRefOid,statusCheckRollup")
    if view.returncode:
        return None
    pr = json.loads(view.stdout)
    owner = run("gh", "config", "get", "user", "-h", "github.com").stdout.strip()
    git = run("git", "rev-parse", "--show-toplevel", *([sent] if sent else [])).stdout.splitlines()
    top, pushed = (git[0] if git else where), (git[1] if len(git) > 1 else None)
    if not needs_review(pr, owner, pushed):
        return None
    repo, head = "/".join(pr["url"].split("/")[3:5]), pushed or pr["headRefOid"]
    return (f"review-3: {pr['url']} head {head[:7]} has no review-3 status (code-practice, Review by "
            f"three). Run `python3 {shlex.quote(str(REVIEW3))} prep {repo} {pr['number']} --repo-dir "
            f"{shlex.quote(top)}` and do what it prints. Pushing again soon? Review after the last push: the merge "
            f"waits for the review-3 check on the head either way.")


def selftest():
    url = "https://github.com/o/r/pull/7"
    cases = [
        ("gh pr create --fill", f"Creating pull request\n{url}\n", (url, None, None)),
        ("git add -A && git commit -m 'x' && git push -u origin feat", "To github.com:o/r.git", ("feat", None, "feat")),
        ("cd /tmp/r && git push origin HEAD:feat", "", ("feat", "/tmp/r", "HEAD")),
        ("git -C /tmp/r push", "", ("", "/tmp/r", "HEAD")),
        ("git push origin HEAD", "", ("", None, "HEAD")),
        ("git push origin wip:feat", "", ("feat", None, "wip")),
        ("gh pr ready 12", "", ("12", None, None)),
        ("gh pr ready --undo 12", "", None),
        ("git push origin --delete feat", "", None),
        ("git push", "Everything up-to-date", ("", None, "HEAD")),  # the head's own status decides, not the output
        ("git push origin feat", " ! [rejected]        feat -> feat (fetch first)", ("feat", None, "feat")),
        ("git status && echo 'gh pr view'", "", None),
        ("git commit -q -F - <<'EOF'\nmsg\nEOF\ngit push -q origin feat; git rev-parse HEAD", "", ("feat", None, "feat")),
    ]
    bad = [f"target({c!r}): got {target(c, o)}, want {w}" for c, o, w in cases if target(c, o) != w]
    pr = lambda rollup=(), state="OPEN", draft=False, owner="o": {"url": f"https://github.com/{owner}/r/pull/7",
                                                                  "state": state, "isDraft": draft, "headRefOid": "a",
                                                                  "statusCheckRollup": list(rollup)}
    ctx = lambda name, state: {"__typename": "StatusContext", "context": name, "state": state}
    check = {"__typename": "CheckRun", "name": "python", "status": "COMPLETED", "conclusion": "SUCCESS"}
    prs = [
        (pr(), True),
        (pr([check]), True),
        (pr([check, ctx("review-3", "PENDING")]), False),
        (pr([ctx("review-3", "SUCCESS")]), False),
        (pr(draft=True), False),
        (pr(state="MERGED"), False),
        (pr(owner="someone-else"), False),
    ]
    reviewed = pr([ctx("review-3", "SUCCESS")])  # head "a" reviewed; a push of "b" that GitHub has not shown yet
    pushes = [(reviewed, "b", True), (reviewed, "a", False), (pr(draft=True), "b", False)]
    bad += [f"needs_review({p}): got {needs_review(p, 'o')}, want {w}" for p, w in prs if needs_review(p, "o") != w]
    bad += [f"needs_review(pushed {s!r}): got {needs_review(p, 'o', s)}, want {w}" for p, s, w in pushes
            if needs_review(p, "o", s) != w]
    print("\n".join(bad) or f"selftest: {len(cases)} commands parse and {len(prs) + len(pushes)} PR heads judge as "
          "expected")
    sys.exit(1 if bad else 0)


def main():
    if sys.argv[1:] == ["--test"]:
        selftest()
    try:
        line = nudge(json.load(sys.stdin))
        if line:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": line}}))
    except Exception:  # a hook never breaks the session it serves
        pass


if __name__ == "__main__":
    main()
