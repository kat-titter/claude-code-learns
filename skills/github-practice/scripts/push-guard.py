#!/usr/bin/env python3
"""
PreToolUse hook (Bash): block `git push` to main/master and every force-push.

Blocks: --force, -f (also inside -uf), --force-with-lease, --force-if-includes, --mirror,
+refspecs, --all (it includes main), refspecs that land on main or master, and a bare
`git push` while the current branch is main or master. Exit 2 sends the reason to Claude.
Never fails the turn on its own errors: anything unexpected allows the call.

Test: python3 push-guard.py --test
"""
import json, os, re, shlex, subprocess, sys

PROTECTED = {"main", "master"}
FORCE_LONG = {"--force", "--force-with-lease", "--force-if-includes", "--mirror", "--all"}
SPLIT = re.compile(r"&&|\|\||;|\||\n|\$\(|`")


def current_branch(cwd):
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                             capture_output=True, text=True, timeout=3)
        return out.stdout.strip()
    except Exception:
        return ""


def check_push(words, cwd):
    """words: tokens after `git`. Returns a reason string or None."""
    # git -C dir push ...  /  git -c k=v push ...
    i = 0
    while i < len(words) and words[i] != "push":
        if words[i] in ("-C", "-c") and i + 1 < len(words):
            if words[i] == "-C":
                cwd = os.path.join(cwd, os.path.expanduser(words[i + 1]))
            i += 2
            continue
        if words[i].startswith("-"):
            i += 1
            continue
        return None                      # another subcommand, not push
    if i >= len(words):
        return None
    args = words[i + 1:]
    flags = [a for a in args if a.startswith("-")]
    for f in flags:
        name = f.split("=", 1)[0]
        if name in FORCE_LONG or (re.fullmatch(r"-[a-zA-Z]+", f) and "f" in f[1:]):
            return f"force-push flag {f}"
    positional = [a for a in args if not a.startswith("-")]
    refspecs = positional[1:]            # first positional is the remote
    for r in refspecs:
        if r.startswith("+"):
            return f"force refspec {r}"
        dst = r.split(":", 1)[-1].removeprefix("refs/heads/")
        if dst in PROTECTED:
            return f"push to {dst}"
    if not refspecs and current_branch(cwd) in PROTECTED:
        return f"push from {current_branch(cwd)} with no refspec"
    return None


def reason_for(command, cwd):
    for part in SPLIT.split(command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", words[0]):
            words = words[1:]            # env assignments: FOO=1 git push
        if words[:1] in (["sudo"], ["command"], ["env"]):
            words = words[1:]
        if words and os.path.basename(words[0]) == "git":
            r = check_push(words[1:], cwd)
            if r:
                return r
    return None


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    if "push" not in cmd:
        return 0
    r = reason_for(cmd, data.get("cwd") or os.getcwd())
    if r:
        print(f"push-guard blocked this ({r}). Pushes to main/master and force-pushes "
              f"are the person's to run. Stop and ask them to run it themselves, with the exact "
              f"command and why.", file=sys.stderr)
        return 2
    return 0


def test():
    cases = {
        "git push origin main": True, "git push origin HEAD:main": True,
        "git push -f origin feat": True, "git push -uf origin feat": True,
        "git push --force-with-lease origin feat": True, "git push origin +feat": True,
        "git push --mirror": True, "git push --all origin": True,
        "cd x && git push origin refs/heads/master": True,
        "git -C repo push --force": True, "FOO=1 git push origin main": True,
        "git push origin feat": False, "git push -u origin feat": False,
        "git push origin feat:feat": False, "git status && echo push": False,
        "git log --format=push": False, "echo 'git push origin main' > notes.txt": False,
    }
    bad = 0
    for c, want in cases.items():
        got = bool(reason_for(c, "/nonexistent"))
        if got != want:
            bad += 1
            print("FAIL", c, "->", got)
    print(f"{len(cases) - bad}/{len(cases)} pass")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        sys.exit(test())
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)                      # a broken guard must not break the session
