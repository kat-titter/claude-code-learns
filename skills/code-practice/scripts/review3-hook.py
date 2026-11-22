#!/usr/bin/env python3
"""PostToolUse hook on Bash: when a command opens, readies or pushes to a pull request, ask for a review by three.

It prints one line of context, and only for an open, non-draft PR in a repo the gh user owns whose head has no
review-3 status yet; on every other command it prints nothing (about 45 ms). GitHub keeps the record, never local
git or push output: the head's review-3 status, and the PR branch's own commit, since GitHub moves the PR to a pushed
commit a moment after the push. A push that changed nothing, was refused or printed nothing (-q) leaves both as they
were, so it stays quiet on a reviewed head. It never blocks and always exits 0. Keep a PR in draft while pushing
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
    branch or "" for the current branch; the folder to ask in, or None for the session's). None when it did none."""
    if CREATE.search(command):
        url = PR_URL.search(output)
        return (url.group(0) if url else "", None)
    ready = READY.search(command)
    if ready:
        args = ready.group(1).split()
        return None if "--undo" in args else (next((a for a in args if not a.startswith("-")), ""), None)
    push = PUSH.search(command)
    if push is None:
        return None
    args = push.group(2).split()
    if any(a in ("--delete", "-d", "--tags", "--dry-run", "-n") or a.startswith(":") for a in args):
        return None
    named = [a for a in args if not a.startswith("-")]  # remote, then refspec
    branch = named[1].split(":")[-1] if len(named) > 1 else ""
    cds = [m.group(1) for m in CD.finditer(command) if m.start() < push.start()]  # the last cd before the push
    where = push.group(1).split()[-1] if push.group(1) else (cds[-1] if cds else None)
    return ("" if branch == "HEAD" else branch, where)


def needs_review(pr, owner, branch_sha=None):
    """True for an open, non-draft PR in a repo the gh user owns whose head has no review-3 status: not reviewed,
    and no review running (prep sets pending first). branch_sha is the PR branch's commit on GitHub: while the PR
    still reports an older head (it catches up a moment after a push), that newer commit is the unreviewed one."""
    from review3 import STATUS  # here, not at the top: most Bash calls never get this far
    contexts = {c.get("context") for c in pr.get("statusCheckRollup") or []}
    lagging = branch_sha not in (None, pr["headRefOid"])
    return (pr["state"] == "OPEN" and not pr["isDraft"] and pr["url"].split("/")[3] == owner
            and (lagging or STATUS not in contexts))


def nudge(d):
    """The one line for this hook input, or None."""
    res = d.get("tool_response") or {}
    out = res if isinstance(res, str) else f"{res.get('stdout', '')}\n{res.get('stderr', '')}"
    hit = target((d.get("tool_input") or {}).get("command", ""), out)
    if hit is None:
        return None
    selector, where = hit
    where = os.path.abspath(os.path.expanduser((where or d.get("cwd") or ".").strip("'\"")))
    # four calls at most, 3 s each: 12 s inside the 15 s hook timeout
    run = lambda *cmd: subprocess.run(cmd, cwd=where, capture_output=True, text=True, timeout=3)
    view = run("gh", "pr", "view", *([selector] if selector else []), "--json",
               "number,url,isDraft,state,headRefOid,headRefName,headRepository,headRepositoryOwner,statusCheckRollup")
    if view.returncode:
        return None
    pr = json.loads(view.stdout)
    repo = "/".join(pr["url"].split("/")[3:5])
    owner = run("gh", "config", "get", "user", "-h", "github.com").stdout.strip()
    # the branch lives in the head repo: a fork's branch can share its name with a different one in the base repo
    head_repo = pr.get("headRepository") and f"{pr['headRepositoryOwner']['login']}/{pr['headRepository']['name']}"
    ref = head_repo and run("gh", "api", f"repos/{head_repo}/git/ref/heads/{pr['headRefName']}", "--jq", ".object.sha")
    branch_sha = ref.stdout.strip() if ref and ref.returncode == 0 else None
    if not needs_review(pr, owner, branch_sha):
        return None
    head, top = branch_sha or pr["headRefOid"], run("git", "rev-parse", "--show-toplevel").stdout.strip() or where
    return (f"review-3: {pr['url']} head {head[:7]} has no review-3 status (code-practice, Review by "
            f"three). Run `python3 {shlex.quote(str(REVIEW3))} prep {repo} {pr['number']} --repo-dir "
            f"{shlex.quote(top)}` and do what it prints. Pushing again soon? Review after the last push: the merge "
            f"waits for the review-3 check on the head either way.")


def selftest():
    url = "https://github.com/o/r/pull/7"
    cases = [
        ("gh pr create --fill", f"Creating pull request\n{url}\n", (url, None)),
        ("git add -A && git commit -m 'x' && git push -u origin feat", "To github.com:o/r.git", ("feat", None)),
        ("cd /tmp/r && git push origin HEAD:feat", "", ("feat", "/tmp/r")),
        ("cd /lib && git commit -qm x\ncd /tmp/r && git push -q origin feat", "", ("feat", "/tmp/r")),
        ("git -C /tmp/r push", "", ("", "/tmp/r")),
        ("git push origin HEAD", "", ("", None)),
        ("git push origin wip:feat", "", ("feat", None)),
        ("gh pr ready 12", "", ("12", None)),
        ("gh pr ready --undo 12", "", None),
        ("git push origin --delete feat", "", None),
        ("git push", "Everything up-to-date", ("", None)),  # GitHub's records decide, not the output
        ("git push origin feat", " ! [rejected]        feat -> feat (fetch first)", ("feat", None)),
        ("git status && echo 'gh pr view'", "", None),
        ("git commit -q -F - <<'EOF'\nmsg\nEOF\ngit push -q origin feat; git rev-parse HEAD", "", ("feat", None)),
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
    reviewed = pr([ctx("review-3", "SUCCESS")])  # head "a" reviewed; the branch on GitHub is at "b" or still "a"
    pushes = [(reviewed, "b", True), (reviewed, "a", False), (pr(draft=True), "b", False)]
    bad += [f"needs_review({p}): got {needs_review(p, 'o')}, want {w}" for p, w in prs if needs_review(p, "o") != w]
    bad += [f"needs_review(branch at {s!r}): got {needs_review(p, 'o', s)}, want {w}" for p, s, w in pushes
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
