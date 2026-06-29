#!/usr/bin/env python3
"""
check-citations.py — verify numbered-citation indexing integrity in an HTML doc.

Catches the recurring bug: in-text superscript numbers desyncing from the
reference list (often because a 2nd+ <ol> restarts auto-numbering at 1 without a
matching start=). Grouped reference lists are FINE as long as each list after the
first sets start= to continue the running count.

Method: compute each <li>'s DISPLAYED number (its <ol>'s start + position) and
require it to equal the id number — i.e. a superscript that links to #rN lands on
a list item that visibly shows N.

Usage:  python3 check-citations.py file.html      (exit 0 = clean, 1 = problems)
"""
import sys, re

def main(path):
    html = open(path, encoding="utf-8").read()
    problems, notes = [], []

    # in-text superscripts: <a href="#rN"...>M</a>  — shown M must equal target N
    sups = re.findall(r'href="#r(\d+)"[^>]*>\s*(\d+)\s*<', html)
    for tgt, shown in sups:
        if tgt != shown:
            problems.append(f"superscript shows [{shown}] but links to #r{tgt}")
    cited = [int(s) for _, s in sups]

    # reference lists (<ol class="refs">) in document order → displayed number per id
    disp, order = {}, []
    for m in re.finditer(r'<ol\b([^>]*)>(.*?)</ol>', html, re.S):
        attrs, body = m.group(1), m.group(2)
        if "refs" not in attrs:            # only the reference list(s)
            continue
        sm = re.search(r'start="(\d+)"', attrs)
        start = int(sm.group(1)) if sm else 1      # HTML default is 1 (restart!)
        for i, idn in enumerate(int(n) for n in re.findall(r'<li[^>]*\bid="r(\d+)"', body)):
            disp[idn] = start + i
            order.append(idn)

    if not order:
        notes.append("no <ol class=refs> reference list found")
    if order != list(range(1, len(order) + 1)):
        problems.append(f"<li> ids not in document order 1..N: {order}")
    # the real check: a ref's displayed number must equal its id (else #rN ≠ shown N)
    for idn, d in sorted(disp.items()):
        if d != idn:
            problems.append(f"ref r{idn} DISPLAYS as [{d}] — add/fix start= on its <ol> "
                            f"(superscript {idn} would land on the wrong number)")
            break  # one is enough to signal the restart; avoid noise

    cset, rset = set(cited), set(disp)
    if cset - rset: problems.append(f"cited but no matching ref: {sorted(cset-rset)}")
    if rset - cset: notes.append(f"refs listed but never cited in text: {sorted(rset-cset)}")

    print(f"citations: {len(sups)} in-text · {len(order)} references "
          f"· {len(re.findall(r'<ol[^>]*refs', html))} list(s)")
    for n in notes: print(f"  note: {n}")
    if problems:
        print("FAIL:")
        for p in problems: print(f"  ✗ {p}")
        return 1
    print("PASS ✓  (every superscript's number == its #rN == the number shown in the list)")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check-citations.py file.html"); sys.exit(2)
    sys.exit(main(sys.argv[1]))
