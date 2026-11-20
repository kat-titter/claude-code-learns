#!/usr/bin/env python3
"""UserPromptSubmit hook: when the session's context passes CONTEXT_NUDGE_AT tokens (default 150000), add one line of
context asking the session to write a PROGRESS note and hand off to a fresh one (token-budget section 6, item 1).
Fires once per step: at 150k, then again at each further 150k; a drop (compaction) re-arms it. Context is the last
assistant call's input + cache read + cache write, read from the end of the transcript. Quiet otherwise. Never blocks
the prompt.
"""
import json, os, sys

# the Claude config folder this skill is installed in: <config>/skills/token-budget/scripts/<this file>
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATE = os.path.join(CONFIG, "context-nudge.json")  # {session_id: last step fired}
CHUNK = 1 << 18

def context(path):
    """Context of the last assistant call with usage, reading the transcript backwards in chunks."""
    with open(path, "rb") as f:
        pos = f.seek(0, 2)
        tail = b""
        while pos > 0:
            step = min(CHUNK, pos)
            pos -= step
            f.seek(pos)
            lines = (f.read(step) + tail).split(b"\n")
            tail = lines.pop(0)  # may be cut at the chunk edge: finish it with the next chunk
            for line in reversed(([tail] if pos == 0 else []) + lines):
                if b'"assistant"' not in line or b'"usage"' not in line:
                    continue
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                u = (m.get("message") or {}).get("usage")
                if m.get("type") != "assistant" or m.get("isSidechain") or not u:
                    continue
                n = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                if n:  # synthetic messages carry zero usage
                    return n
    return 0

def main():
    data = json.loads(sys.stdin.read() or "{}")
    sid, path = data.get("session_id"), data.get("transcript_path")
    if not sid or not path or not os.path.isfile(path):
        return
    at = int(os.environ.get("CONTEXT_NUDGE_AT", 150000))
    ctx = context(path)
    step = ctx // at
    try:
        state = json.load(open(STATE))
    except Exception:
        state = {}
    prev = state.pop(sid, 0)
    if step == prev:
        return
    state[sid] = step  # a lower step after compaction re-arms the nudge
    with open(STATE, "w") as f:
        json.dump(dict(list(state.items())[-200:]), f)
    if step < prev or step < 1:
        return
    note = (f"Context is now {ctx // 1000}k tokens, and every call re-reads all of it. At the next natural break, write a "
            "short PROGRESS note (what is done, file paths, results, what is next), then hand off with "
            "mcp__ccd_session__hand_off_to_session, or offer start_session with that note as the brief "
            "(token-budget section 6, item 1).")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}}))

if __name__ == "__main__":
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__.strip())
        sys.exit(0)
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
