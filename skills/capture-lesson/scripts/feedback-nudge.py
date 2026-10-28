#!/usr/bin/env python3
"""UserPromptSubmit hook: when the person's message reads like feedback (a correction, a preference, a style note,
surprise at a result), add one line of context asking the session to route the lesson: general skill, personal style
skill, or project memory. Quiet otherwise (most prompts add nothing). Never blocks the prompt.

Test it: echo '{"prompt": "no, from now on keep legends outside the plot"}' | python3 feedback-nudge.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import FEEDBACK, HARNESS, read_hook_input, style_skill


def main():
    prompt = str(read_hook_input(sys.stdin).get('prompt', ''))
    if not prompt or HARNESS.search(prompt) or not FEEDBACK.search(prompt):
        return
    note = ("This message may carry reusable feedback. After acting on it, ask: does it apply beyond this task? "
            "If it does, route it with the capture-lesson skill: a general guideline goes into the matching general skill, "
            f"personal taste into the {style_skill()} skill, and a project fact into the project's memory. Phrase it as a "
            "positive guideline with an example, and mention the update in one line of the reply.")
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': note}}))


if __name__ == '__main__':
    if sys.argv[1:2] in (['-h'], ['--help']):
        print(__doc__.strip())
        sys.exit(0)
    try:
        main()
    except Exception:
        pass            # a hook must never break the session
    sys.exit(0)
