#!/usr/bin/env python3
"""UserPromptSubmit hook: when a prompt shares three or more rare words with one skill's description, add one line
naming that skill, so it loads before the work starts. Skills undertrigger: on one real library a strongly matching
skill loaded on its own about 1 time in 5, and about 1 in 2 when the prompt named it. Quiet on most prompts (about 1 in
25 fired there). Never names the personal style skill, a skill the prompt already names, or more than two.

A vague prompt shares few rare words with anything, so it gets the skill pick instead: when no description matches,
the prompt has six words or more and is not a bare "continue" or "yes", and the session has loaded no skill yet, one
line asks Claude to choose from the skill list itself before the first tool call. On one library over 30 days, 260 of
315 big turns (ten or more tool calls) in sessions with no skill loaded yet loaded none; the router named a right skill
for 6 of 73 that did. The pick fires on about a third of prompts, catches 192 of the 260, and goes quiet once a skill
loads. (A folder's own history named a right skill in its top three for 24 of 73, too few to suggest names from.)

Test it: echo '{"prompt": "two of the references in the report look made up and the numbering drifted"}' | python3 skill-router.py
         echo '{"prompt": "make the readme better and check it all still holds up"}' | python3 skill-router.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import HARNESS, match_skills, read_hook_input, scan_transcript, skill_index

REPLY = re.compile(r'^(continue|resume|go on|go ahead|keep going|yes|y|ok|okay|sure|next|proceed|do it|merge|push|commit)'
                   r'\b[\s.!]*$', re.I)
PICK = ("Skill pick: no skill is loaded in this session and none matched the prompt's words. Before the first tool "
        "call, read the skill list against this task's outcome, medium and field, load the one to three that apply, and "
        "name them in the plan's first step, or say that none apply.")



def main():
    data = read_hook_input(sys.stdin)
    prompt = str(data.get('prompt', ''))
    if not prompt or prompt.lstrip().startswith('/') or HARNESS.search(prompt):
        return
    hits = [h for h in match_skills(prompt, skill_index())
            if not h[1].endswith('-style') and not re.search(rf'(?<![\w-]){re.escape(h[1])}(?![\w-])', prompt)][:2]
    if hits:
        named = '; '.join(f"`{skill}` ({', '.join(ws[:3])})" for _, skill, ws in hits)
        note = f"Skill match: {named}. If it fits the task, load it before the first tool call."
    elif (len(prompt.split()) >= 6 and not REPLY.search(prompt.strip())
          and not scan_transcript(data.get('transcript_path', ''), 0)[1]):
        note = PICK
    else:
        return
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
