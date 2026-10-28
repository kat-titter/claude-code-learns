#!/usr/bin/env python3
"""
Hook for PreToolUse (matcher Skill) and UserPromptExpansion: append one line per skill
use to <config>/skill-usage.log, so dead and undertriggering skills show up over time.

Line: ISO time <tab> skill <tab> how (model = Claude called the Skill tool, typed = /name)
<tab> session id. PreToolUse misses typed /name; UserPromptExpansion covers it.
Never fails the turn.

Summary: python3 skill-usage-log.py --report [DAYS]
"""
import collections, datetime, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG, read_hook_input

LOG = os.path.join(CONFIG, "skill-usage.log")


def log():
    d = read_hook_input(sys.stdin)
    ev = d.get("hook_event_name")
    if ev == "PreToolUse" and d.get("tool_name") == "Skill":
        name, how = (d.get("tool_input") or {}).get("skill", ""), "model"
    elif ev == "UserPromptExpansion" and d.get("expansion_type") == "slash_command":
        name, how = d.get("command_name", ""), "typed"
    else:
        return
    if name and not re.search(r'-skill-[0-9a-f]{8}$', name):     # a trigger eval's scratch copy
        now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        with open(LOG, "a") as f:
            f.write(f"{now}\t{name}\t{how}\t{d.get('session_id', '')}\n")


def report(days):
    since = datetime.datetime.now().astimezone() - datetime.timedelta(days=days)
    uses = collections.Counter()
    try:
        for line in open(LOG):
            try:
                t, name, how, *_ = line.rstrip("\n").split("\t")
                if datetime.datetime.fromisoformat(t) >= since:
                    uses[name] += 1
            except ValueError:
                continue        # a torn or hand-edited line
    except FileNotFoundError:
        print(f"no log yet at {LOG}")
    sk = os.path.join(CONFIG, "skills")
    skills = sorted(s for s in (os.listdir(sk) if os.path.isdir(sk) else [])
                    if os.path.isfile(os.path.join(sk, s, "SKILL.md")))
    print(f"skill uses in the last {days} days ({LOG})")
    for s in sorted(skills, key=lambda s: (-uses[s], s)):
        print(f"{uses[s]:5}  {s}{'   <- unused' if not uses[s] else ''}")
    for s in sorted(set(uses) - set(skills)):
        print(f"{uses[s]:5}  {s} (plugin or built-in)")


if __name__ == "__main__":
    if sys.argv[1:2] in (["-h"], ["--help"]):
        print(__doc__.strip())
        sys.exit(0)
    if sys.argv[1:2] == ["--report"]:
        report(int(sys.argv[2]) if len(sys.argv) > 2 else 30)
        sys.exit(0)
    try:
        log()
    except Exception:
        pass
    sys.exit(0)
