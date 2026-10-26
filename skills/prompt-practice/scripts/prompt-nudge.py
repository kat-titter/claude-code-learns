#!/usr/bin/env python3
"""UserPromptSubmit hook: when the user's prompt reads as dictated or terse (starts in lowercase or ends without
punctuation, 3 to 300 words), add one line of context asking the session to rewrite it silently into a brief
(prompt-practice section 1). Quiet otherwise. Never blocks the prompt.
"""
import json, re, sys

HARNESS = re.compile(r'This session is being continued|Base directory for this skill|<task-notification>|<system-reminder>|'
                     r'<command-name>|<side-sessions-event>|<ci-monitor-event>')
NOTE = ("This prompt reads as dictated or terse. Before the first tool call, rewrite it silently into a brief "
        "(prompt-practice section 1): the outcome and where the work is heading, the deliverable and its reader, "
        "context from memory, notes and sibling sessions, the field's words for any slip, the prior work to build on, "
        "and the check that can fail. Say the reading in one line only when it changes the work.")

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

try:
    main()
except Exception:
    pass
sys.exit(0)
