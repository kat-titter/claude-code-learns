#!/usr/bin/env python3
"""Count every hex colour per figure block of an HTML page, so an accent used outside its meaning shows up as a number.

  python3 accent_census.py PAGE.html --accent ec3c6e=rose --accent 8da4bc=slate [--block 'fig|html']

Blocks are the page's generated figure markers (<!--fig:NAME--> ... <!--/fig:NAME-->, <!--html:NAME--> ... ), then
the rest of the page as "(page itself)", where CSS var(--NAME) uses are counted too. Prints one row per block with each
accent's count and the other colours' total; exit 0 (it lists, you judge: a rose count on a figure whose meaning has no
"kept" in it is the finding). Case: a DJ tool's about page, 2026-11-03: deck A slate and deck B rose on four figures and
rose headline phrases, found as 34 rose and 45 slate uses in figures that mean neither kept nor to-review."""
import argparse, re, sys

ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
ap.add_argument("page"); ap.add_argument("--accent", action="append", default=[], help="hex=name, repeatable")
ap.add_argument("--block", default="fig|html", help="marker kinds, a regex alternation")
a = ap.parse_args()
acc = dict(x.split("=", 1) for x in a.accent) or {"ec3c6e": "rose", "8da4bc": "slate"}
s = open(a.page, encoding="utf-8").read()
pat = re.compile(rf"<!--({a.block}):([a-z0-9_-]+)-->(.*?)<!--/\1:\2-->", re.S)
rows = [(name, body) for _, name, body in pat.findall(s)] + [("(page itself)", pat.sub("", s))]
names = list(acc.values())
print(f"{'block':18}" + "".join(f"{n:>8}" for n in names) + f"{'other':>8}  var(--accent) uses")
tot = {n: 0 for n in names}
for name, body in rows:
    hx = [h.lower() for h in re.findall(r"#([0-9a-fA-F]{6})\b", body)]
    counts = {acc[h]: hx.count(h) for h in acc}
    other = len(hx) - sum(counts.values())
    for n in names: tot[n] += counts[n]
    vars_ = ", ".join(f"--{v}:{body.count(f'var(--{v})')}" for v in ("pink", "cyan", "kept", "work", "mix") if f"var(--{v})" in body)
    if any(counts.values()) or name == "(page itself)":
        print(f"{name:18}" + "".join(f"{counts[n]:8}" for n in names) + f"{other:8}  {vars_}")
print(f"{'total':18}" + "".join(f"{tot[n]:8}" for n in names))
