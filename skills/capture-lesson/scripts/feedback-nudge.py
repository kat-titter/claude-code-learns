#!/usr/bin/env python3
"""UserPromptSubmit hook: when the user's message reads like feedback (a correction, a preference, a style note, surprise
at a result), add one line of context asking the session to route the lesson: general skill, personal style skill, or
project memory. Quiet otherwise. Never blocks the prompt.
"""
import json, os, re, sys

# the Claude config folder this skill is installed in: <config>/skills/capture-lesson/scripts/<this file>
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def style_skill(skills_dir=os.path.join(CONFIG, 'skills')):
    """The personal style skill: $CLAUDE_STYLE_SKILL, else the one skill folder named <name>-style, else my-style."""
    name = os.environ.get('CLAUDE_STYLE_SKILL')
    if name:
        return name
    found = sorted(d for d in os.listdir(skills_dir) if d.endswith('-style')) if os.path.isdir(skills_dir) else []
    return found[0] if len(found) == 1 else 'my-style'

FEEDBACK = re.compile(
    r"(that'?s (wrong|not)|not (right|quite|what i)|you (forgot|missed)|i meant|instead\b|should (be|have|use|show|look|go)|"
    r"\bplease (use|keep|make|add|show|focus)|\bprefer\b|\bi (like|love|want)\b|\bfeels? (off|stale|forced|salesy|boring)|"
    r"\btoo (much|many|long|slow|small|big|dense)\b|why (is|are|does|taking)|taking so long|\bdon'?t\b|\bdont\b|\bnever\b|"
    r"\balways\b|\bno more\b|\bremember (this|that)\b|\bfrom now on\b|\bin each chat\b|\bkeep .{0,30} separate\b)", re.I)
HARNESS = re.compile(r'This session is being continued|Base directory for this skill|<task-notification>|<system-reminder>|<command-name>')

def main():
    try:
        data = json.loads(sys.stdin.read() or '{}')
    except Exception:
        return
    prompt = str(data.get('prompt', ''))
    if not prompt or HARNESS.search(prompt) or not FEEDBACK.search(prompt):
        return
    note = ("This message may carry reusable feedback. After acting on it, ask: does it apply beyond this task? "
            "If it does, route it with the capture-lesson skill: a general guideline goes into the matching general skill, "
            f"personal taste into the {style_skill()} skill, and a project fact into the project's memory. Phrase it as a positive "
            "guideline with an example, and mention the update in one line of the reply.")
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': note}}))

try:
    main()
except Exception:
    pass
sys.exit(0)
