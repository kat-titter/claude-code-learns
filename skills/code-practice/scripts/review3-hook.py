#!/usr/bin/env python3
"""PostToolUse hook on Bash: when a command opens, readies or pushes to a pull request, ask for a review by three.

It prints one line of context, and only for an open, non-draft PR the gh user owns that just got a new head; on every
other command it prints nothing (about 45 ms). It never blocks and always exits 0. Keep a PR in draft while pushing
fixes and it stays quiet; `gh pr ready` starts the review. The review itself is review3.py and the review-3 workflow.

  settings.json: "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "timeout": 15,
                  "command": "python3 \"$HOME/.claude/skills/code-practice/scripts/review3-hook.py\""}]}]
  python3 review3-hook.py --test     the command parser on fixed cases; exit 1 if it drifts
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REVIEW3 = Path(__file__).resolve().with_name("review3.py")
PR_URL = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+")
CREATE = re.compile(r"(?:^|[;&|(]\s*)gh\s+pr\s+create\b")
READY = re.compile(r"(?:^|[;&|(]\s*)gh\s+pr\s+ready\b([^;&|)]*)")
PUSH = re.compile(r"(?:^|[;&|(]\s*)git((?:\s+-C\s+\S+)?)\s+push\b([^;&|)]*)")
CD = re.compile(r"(?:^|[;&|]\s*)cd\s+(\S+)\s*&&")
NO_NEW_HEAD = re.compile(r"Everything up-to-date|\[rejected\]|^error:|^fatal:", re.M)


def target(command, output):
    """Which PR a Bash command opened, readied or gave a new head, as (what `gh pr view` takes: a URL, number,
    branch or "" for the current branch; the folder to ask in, or None for the session's). None when it did none."""
    if CREATE.search(command):
        url = PR_URL.search(output)
        return (url.group(0) if url else "", None)
    ready = READY.search(command)
    if ready:
        args = ready.group(1).split()
        return None if "--undo" in args else (next((a for a in args if not a.startswith("-")), ""), None)
    push = PUSH.search(command)
    if push is None or NO_NEW_HEAD.search(output):
        return None
    args = push.group(2).split()
    if any(a in ("--delete", "-d", "--tags", "--dry-run", "-n") or a.startswith(":") for a in args):
        return None
    named = [a for a in args if not a.startswith("-")]  # remote, then refspec
    branch = named[1].split(":")[-1] if len(named) > 1 else ""
    cd = CD.search(command)
    where = push.group(1).split()[-1] if push.group(1) else (cd.group(1) if cd else None)
    return ("" if branch == "HEAD" else branch, where)


def nudge(d):
    """The one line for this hook input, or None."""
    res = d.get("tool_response") or {}
    out = res if isinstance(res, str) else f"{res.get('stdout', '')}\n{res.get('stderr', '')}"
    hit = target((d.get("tool_input") or {}).get("command", ""), out)
    if hit is None:
        return None
    selector, where = hit
    where = os.path.abspath(os.path.expanduser((where or d.get("cwd") or ".").strip("'\"")))
    # three calls at most, each well inside the 15 s hook timeout
    run = lambda *cmd: subprocess.run(cmd, cwd=where, capture_output=True, text=True, timeout=4)
    view = run("gh", "pr", "view", *([selector] if selector else []), "--json", "number,url,isDraft,state")
    if view.returncode:
        return None
    pr = json.loads(view.stdout)
    repo, n = "/".join(pr["url"].split("/")[3:5]), pr["number"]
    owner = run("gh", "config", "get", "user", "-h", "github.com").stdout.strip()
    if pr["state"] != "OPEN" or pr["isDraft"] or repo.split("/")[0] != owner:
        return None
    top = run("git", "rev-parse", "--show-toplevel").stdout.strip() or where
    return (f"review-3: {pr['url']} has a new head to review (code-practice, Review by three). Run "
            f"`python3 {REVIEW3} prep {repo} {n} --repo-dir {top}`, then Workflow({{name: 'review-3', args: "
            f"{{run: <the folder prep printed>, repo: '{repo}', pr: {n}}}}}), then `review3.py ready RUN`. Pushing "
            f"again soon? Review after the last push: the merge waits for the review-3 check on the head either way.")


def selftest():
    url = "https://github.com/o/r/pull/7"
    cases = [
        ("gh pr create --fill", f"Creating pull request\n{url}\n", (url, None)),
        ("git add -A && git commit -m 'x' && git push -u origin feat", "To github.com:o/r.git", ("feat", None)),
        ("cd /tmp/r && git push origin HEAD:feat", "", ("feat", "/tmp/r")),
        ("git -C /tmp/r push", "", ("", "/tmp/r")),
        ("git push origin HEAD", "", ("", None)),
        ("gh pr ready 12", "", ("12", None)),
        ("gh pr ready --undo 12", "", None),
        ("git push origin --delete feat", "", None),
        ("git push", "Everything up-to-date", None),
        ("git push origin feat", " ! [rejected]        feat -> feat (fetch first)", None),
        ("git status && echo 'gh pr view'", "", None),
    ]
    bad = [f"target({c!r}): got {target(c, o)}, want {w}" for c, o, w in cases if target(c, o) != w]
    print("\n".join(bad) or f"selftest: {len(cases)} commands parse as expected")
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
