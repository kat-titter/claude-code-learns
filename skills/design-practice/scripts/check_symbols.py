#!/usr/bin/env python3
"""Check a set of symbols or short codes: one per thing, and no collisions with notations they sit beside.

Usage:
  check_symbols.py PAGE.html --class pt-sym [--chem] [--reserved "Ck Cc Pl"] [--base]
  check_symbols.py --list "Sw Tk Ro ..." [--chem] [--reserved ...]
--class   take the text of every element with this class (nested markup included)
--chem    also flag collisions with the 118 chemical element symbols (for tables that borrow chemistry's look)
--reserved   codes already used nearby (a companion page, a key, a legend)
Elements also marked 'sample' or 'pt-sample' (a key's worked example) are skipped.
--base    compare only the leading letters (Ro in Ro∫²), for symbols built from a base plus marks
Exit 1 on duplicates or collisions. Stdlib only.
"""
import argparse
import re
import sys
from html.parser import HTMLParser

CHEM = set('''H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr
Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb
Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'''.split())


class Grab(HTMLParser):
    def __init__(self, cls):
        super().__init__()
        self.cls, self.depth, self.buf, self.out = cls, 0, [], []

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif self.cls in (dict(attrs).get('class') or '').split() and 'pt-sample' not in (dict(attrs).get('class') or '').split() and 'sample' not in (dict(attrs).get('class') or '').split():
            self.depth, self.buf = 1, []

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if not self.depth:
                self.out.append(''.join(self.buf).strip())

    def handle_data(self, d):
        if self.depth:
            self.buf.append(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page', nargs='?')
    ap.add_argument('--class', dest='cls')
    ap.add_argument('--list')
    ap.add_argument('--chem', action='store_true')
    ap.add_argument('--reserved', default='')
    ap.add_argument('--base', action='store_true')
    a = ap.parse_args()
    if a.list:
        syms = a.list.split()
    else:
        g = Grab(a.cls)
        g.feed(open(a.page, encoding='utf-8').read())
        syms = g.out
    keys = [re.match(r'[A-Za-z]+', s).group(0) if a.base and re.match(r'[A-Za-z]+', s) else s for s in syms]
    full_dupes = sorted({s for s in syms if syms.count(s) > 1})
    avoid = set(a.reserved.split()) | (CHEM if a.chem else set())
    clashes = sorted({k for k in keys if k in avoid})
    print(f'{len(syms)} symbols, {len(set(syms))} distinct')
    if full_dupes:
        print('duplicates:', ' '.join(full_dupes))
    if clashes:
        print('collide with', 'chemistry or the reserved list:' if a.chem else 'the reserved list:', ' '.join(clashes))
    sys.exit(1 if full_dupes or clashes else 0)


if __name__ == '__main__':
    main()
