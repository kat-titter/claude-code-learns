#!/usr/bin/env python3
"""UserPromptSubmit hook: when the user's prompt reads as dictated (3 to 300 words with two or more likely typos, or a
run-on of 40+ words with at most one sentence break), add one line of context asking the session to rewrite it
silently into a brief (prompt-practice section 1). Quiet otherwise, so plain questions and short replies pass
untouched. Never blocks the prompt.

Why typos, not lowercase: a person who types in lowercase tripped the old test (lowercase start or no end mark) on 132
of 139 prompts; this one fires on about a quarter, mostly garbled requests (measured on 80 sessions, 2026-11-05).

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
NOTE = ("Dictated prompt: rewrite it silently into a brief first (prompt-practice §1): outcome, deliverable, "
        "context, the field's words, prior work, a check that can fail, the skills that apply. Say the reading only if it changes the work.")


DICT = '/usr/share/dict/words'
# words a dictionary lacks but prompts use: contractions typed without the apostrophe, and tool names
EXTRA = set('''im ive id youre dont cant wont isnt doesnt didnt wasnt arent hasnt havent shouldnt couldnt wouldnt thats whats lets
theres heres ok okay repo repos github api apis html css json url urls ui ux app apps pdf pdfs svg png jpg mp3 wav flac
todo claude anthropic etc vs desktop laptop macbook soundcloud spotify beatport moodboard midjourney suno youtube
instagram'''.split())
SUFFIXES = (('ies', 'y'), ('ied', 'y'), ('ing', ''), ('ing', 'e'), ('ed', ''), ('ed', 'e'), ('es', ''), ('s', ''),
            ('ly', ''), ('er', ''), ('ers', ''))


def known_words():
    try:
        with open(DICT) as f:
            return {w.strip().lower() for w in f} | EXTRA
    except OSError:
        return None


def known(w, vocab):
    if w in vocab:
        return True
    for suf, add in SUFFIXES:
        if w.endswith(suf):
            base = w[: -len(suf)] + add
            if base in vocab:
                return True
            if suf in ('ing', 'ed') and len(base) > 2 and base[-1] == base[-2] and base[:-1] in vocab:
                return True
    return False


def typos(text, vocab):
    text = re.sub(r'\S*(https?://|www\.)\S*', ' ', text)
    return [w for w in re.findall(r"(?<![\w./#@-])[a-z]{3,}(?![\w./#@-])", text) if not known(w, vocab)]


def dictated(prompt, vocab):
    text = prompt.strip()
    words = len(text.split())
    if text.startswith('/') or not 3 <= words <= 300:
        return False
    runon = words >= 40 and len(re.findall(r'[.?!](\s|$)', text)) <= 1
    return runon or (vocab is not None and len(typos(text, vocab)) >= 2)


def main():
    try:
        data = json.loads(sys.stdin.read() or '{}')
    except Exception:
        return
    prompt = str(data.get('prompt', ''))
    if not prompt or HARNESS.search(prompt) or not dictated(prompt, known_words()):
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
