#!/usr/bin/env python3
"""Stop hook (runs after each reply): find feedback in the person's recent prompts that the session may not have
captured, and log each new one once as a candidate in <config>/lessons-inbox.md (the fast store). Promotion to a
skill happens later, through the capture-lesson skill. Never fails the turn.

Reads only the transcript's tail and only the person's own prompts (tool results, injected skill text and harness
messages also arrive as "user" turns and are skipped). A hash of each logged prompt goes to <config>/.corrections-seen
so a prompt is logged once however many replies follow it.

Test it: python3 scan-corrections.py --dry-run TRANSCRIPT.jsonl
"""
import datetime, hashlib, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG, FEEDBACK, read_hook_input, user_prompts

INBOX = os.path.join(CONFIG, 'lessons-inbox.md')
SEEN = os.path.join(CONFIG, '.corrections-seen')
RECENT = 8          # prompts checked per reply; earlier ones were checked by earlier replies
KEEP_SEEN = 5000    # hashes remembered, newest kept


def candidates(transcript, seen):
    out = []
    for text in user_prompts(transcript)[-RECENT:]:
        m = FEEDBACK.search(text)
        if not m:
            continue
        h = hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]
        if h not in seen:
            seen.append(h)
            snip = text[max(0, m.start() - 40): m.start() + 80]      # the words around the feedback, not the opening
            out.append(re.sub(r'\s+', ' ', snip).strip().replace('"', "'"))
    return out


def run(transcript, dry=False):
    if not transcript or not os.path.exists(transcript):
        return
    seen = open(SEEN, encoding='utf-8').read().split() if os.path.exists(SEEN) else []
    new = candidates(transcript, seen)
    if dry:
        print('\n'.join(new) or 'no new feedback')
        return
    if not new:
        return
    date = datetime.date.today().isoformat()
    with open(INBOX, 'a', encoding='utf-8') as f:
        f.writelines(f'- {date} · candidate · "{snip}" → review\n' for snip in new)
    with open(SEEN, 'w', encoding='utf-8') as f:
        f.write('\n'.join(seen[-KEEP_SEEN:]))


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] in (['-h'], ['--help']):
        print(__doc__.strip())
        sys.exit(0)
    try:
        if args[:1] == ['--dry-run']:
            run(args[1] if len(args) > 1 else '', dry=True)
        else:
            run(read_hook_input(sys.stdin).get('transcript_path', ''))
    except Exception:
        pass            # a hook must never break the session
    sys.exit(0)
