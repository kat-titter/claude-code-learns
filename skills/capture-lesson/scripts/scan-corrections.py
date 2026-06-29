#!/usr/bin/env python3
"""
Stop-hook: scan the just-finished session for correction moments and log them as
candidates in ~/.claude/lessons-inbox.md (the fast store). Never fails the turn.

Reads the hook JSON on stdin (expects transcript_path). Extracts recent USER
messages, matches correction signals, de-dupes by content hash, appends candidates.
Promotion to a real Skill happens later, via the capture-lesson skill.
"""
import sys, os, json, re, hashlib, datetime

HOME = os.path.expanduser("~")
INBOX = os.path.join(HOME, ".claude", "lessons-inbox.md")
SEEN  = os.path.join(HOME, ".claude", ".corrections-seen")

# higher-precision correction signals (avoid common words like "fix"/"instead")
SIGNAL = re.compile(
    r"(that'?s wrong|not right|incorrect|you forgot|you missed|doesn'?t work|"
    r"isn'?t working|that'?s not (right|what)|not what i (meant|asked)|i meant|"
    r"seems? like a lot|too (slow|long|much|many|big)|why is it|no sass|"
    r"^\s*(no|nope)\b)", re.I)

def fail_safe(fn):
    try: fn()
    except Exception:
        pass            # a hook must never break the session
    sys.exit(0)

def texts_from_transcript(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try: obj = json.loads(line)
                except Exception: continue
                # only user turns
                role = obj.get("role") or (obj.get("message") or {}).get("role") or obj.get("type")
                if role != "user": continue
                msg = obj.get("message", obj)
                content = msg.get("content", "")
                if isinstance(content, str):
                    out.append(content)
                elif isinstance(content, list):
                    out.append(" ".join(b.get("text", "") for b in content if isinstance(b, dict)))
    except Exception:
        pass
    return out[-8:]      # only the last few user messages

def run():
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    data = json.loads(raw) if raw.strip() else {}
    tpath = data.get("transcript_path", "")
    if not tpath or not os.path.exists(tpath):
        return
    seen = set()
    if os.path.exists(SEEN):
        seen = set(open(SEEN, encoding="utf-8").read().split())
    new = []
    for t in texts_from_transcript(tpath):
        t = t.strip()
        if not t or not SIGNAL.search(t):
            continue
        h = hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]
        if h in seen:
            continue
        seen.add(h)
        snip = re.sub(r"\s+", " ", t)[:120]
        new.append((h, snip))
    if not new:
        return
    date = datetime.date.today().isoformat()
    with open(INBOX, "a", encoding="utf-8") as f:
        for h, snip in new:
            f.write(f"- {date} · candidate · \"{snip}\" → review\n")
    with open(SEEN, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(seen)))

fail_safe(run)
