#!/usr/bin/env python3
"""UserPromptSubmit hook: when the user's prompt reads as dictated or terse (starts in lowercase or ends without
punctuation, 3 to 300 words), add one line of context asking the session to rewrite it silently into a brief
(prompt-practice section 1). Quiet otherwise. Never blocks the prompt.

Install: {"type": "command", "command": "python3 ~/.claude/skills/prompt-practice/scripts/prompt-nudge.py"} under
UserPromptSubmit in settings.json. Reads the hook's JSON on stdin.
"""
import json, re, sys

# text the harness injects as a "user" turn; kept in step with capture-lesson/scripts/lessonlib.py HARNESS
# (copied, not imported, so prompt-practice stands alone)
HARNESS = re.compile(
    r'This session is being continued|The user sent a new message while you were working|Base directory for this skill|'
    r'<task-notification>|<system-reminder>|<command-name>|<local-command-|<side-sessions-event>|<ci-monitor-event>|'
    r'^Background \(from the session|<agent-message |<cross-session-message |<scheduled-task |\[Subagent hand-back\]|\[SYSTEM NOTIFICATION|\[Request interrupted')
NOTE = ("Terse or dictated prompt: rewrite it silently into a brief first (prompt-practice §1): outcome, deliverable, "
        "context, the field's words, prior work, a check that can fail. Say the reading only if it changes the work.")


def terse(prompt):
    text = prompt.strip()
    words = len(text.split())
    if text.startswith('/') or not 3 <= words <= 300:
        return False
    first = next((c for c in text if c.isalpha()), '')
    return first.islower() or text[-1] not in '.?!)"\'`'


def main():
    try:
        data = json.loads(sys.stdin.read() or '{}')
    except Exception:
        return
    prompt = str(data.get('prompt', ''))
    if not prompt or HARNESS.search(prompt) or not terse(prompt):
        return
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': NOTE}}))


if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__)
    sys.exit(0)
if sys.stdin.isatty():
    print('prompt-nudge.py: no hook input on stdin (it runs as a UserPromptSubmit hook); --help for more', file=sys.stderr)
    sys.exit(0)
try:
    main()
except Exception:
    pass
sys.exit(0)
