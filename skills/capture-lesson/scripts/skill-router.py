#!/usr/bin/env python3
"""UserPromptSubmit hook: when a prompt shares three or more rare words with one skill's description, add one line
naming that skill, so it loads before the work starts. Skills undertrigger: on one real library a strongly matching
skill loaded on its own about 1 time in 5, and about 1 in 2 when the prompt named it. Quiet on most prompts (about 1 in
25 fired there). Never names the personal style skill, a skill the prompt already names, or more than two.

Test it: echo '{"prompt": "the transition is rough, kicks flam when the two tracks overlap"}' | python3 skill-router.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import HARNESS, match_skills, read_hook_input, skill_index


def main():
    prompt = str(read_hook_input(sys.stdin).get('prompt', ''))
    if not prompt or prompt.lstrip().startswith('/') or HARNESS.search(prompt):
        return
    hits = [h for h in match_skills(prompt, skill_index())
            if not h[1].endswith('-style') and not re.search(rf'(?<![\w-]){re.escape(h[1])}(?![\w-])', prompt)][:2]
    if not hits:
        return
    named = '; '.join(f"`{skill}` ({', '.join(ws[:3])})" for _, skill, ws in hits)
    note = f"Skill match: {named}. If it fits the task, load it before the first tool call."
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
