#!/usr/bin/env python3
"""Flag coined/emergent terms in user-facing text and suggest the field's own word. Exit 1 on any hit."""
import argparse, html, json, os, re, sys

def visible_text(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    if path.endswith((".html", ".htm", ".svg")):
        s = re.sub(r"(?is)<(script|style)\b.*?</\1>", lambda m: "\n" * m.group(0).count("\n"), s)
        keep = re.findall(r'(?:title|alt|aria-label)="([^"]*)"', s)
        s = re.sub(r"(?s)<[^>]+>", lambda m: "\n" * m.group(0).count("\n") + " ", s)
        s = html.unescape(s) + "\n" + "\n".join(keep)
    return s.splitlines()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glossary", required=True)
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    g = json.load(open(a.glossary)); banned = {**g.get("banned", {}), **g.get("prefer", {})}; ignore = g.get("ignore", [])
    exts = (".html", ".htm", ".md", ".txt", ".svg")
    files = []
    for p in a.paths:
        if os.path.isdir(p):
            for r, _, fs in os.walk(p):
                files += [os.path.join(r, f) for f in fs if f.endswith(exts)]
        else:
            files.append(p)
    hits = 0
    for f in sorted(files):
        for i, line in enumerate(visible_text(f), 1):
            if any(x in line for x in ignore):
                continue
            for term, sug in banned.items():
                if re.search(rf"(?i)\b{re.escape(term)}s?\b", line):
                    hits += 1
                    print(f"{f}:{i}: {term} -> {sug}: {line.strip()[:120]}")
    print(f"{hits} hit(s) in {len(files)} file(s)")
    sys.exit(1 if hits else 0)

if __name__ == "__main__":
    main()
