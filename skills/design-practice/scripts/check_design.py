#!/usr/bin/env python3
"""Flag separator dots in visible text and short phrases repeated on the same page. Exit 1 if separator dots found."""
import collections, html, re, sys

SEP = re.compile(r"\s[·•∙]\s|&middot;")

def visible(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", "\n", s)
    return [l.strip() for l in html.unescape(s).splitlines() if l.strip()]

if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
missing = [p for p in sys.argv[1:] if not p.startswith('-') and not __import__('os').path.isfile(p)]
if not sys.argv[1:] or missing:
    sys.exit(f'usage: check_design.py PAGE.html ... (missing: {", ".join(missing) or "no file given"})')
rc = 0
for p in sys.argv[1:]:
    lines = visible(p)
    dots = [l for l in lines if SEP.search(" " + l + " ")]
    for l in dots[:20]:
        print(f"{p}: separator dot: {l[:100]}")
    if dots:
        rc = 1
    phrases = collections.Counter(l for l in lines if 3 <= len(l) <= 40 and not l.isdigit())
    reps = [(t, n) for t, n in phrases.items() if n > 1]
    for t, n in sorted(reps, key=lambda x: -x[1])[:15]:
        print(f"{p}: repeated x{n}: {t}")
    print(f"{p}: {len(dots)} separator-dot line(s), {len(reps)} repeated phrase(s)")
sys.exit(rc)
