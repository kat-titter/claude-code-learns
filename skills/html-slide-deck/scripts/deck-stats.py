#!/usr/bin/env python3
"""Measure a printed deck instead of eyeballing it: per page, words on the page, the smallest text in CSS px, how many
text runs sit under the stage floor, decimals, and separator dots. Use it before and after a pass, so "less text" and
"bigger text" are numbers.

Usage: deck-stats.py DECK.pdf [--css-width 1280] [--floor 15] [--pages 1-18] [--labels "01,02a,..."]
Needs PyMuPDF (see render-pages.py). Chrome prints CSS pixels at 0.75 pt, so px = pt * css_width / page_width_pt.
Print the stage view (the talk as presented) and the reader's PDF separately if the deck has two layers.
"""
import argparse, os, re, sys
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import fitz
except ImportError:
    sys.exit('PyMuPDF missing: python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf')
ap = argparse.ArgumentParser(usage='deck-stats.py DECK.pdf [--css-width 1280] [--floor 15] [--pages 1-18] [--labels L]')
ap.add_argument('pdf'); ap.add_argument('--css-width', type=float, default=1280)
ap.add_argument('--floor', type=float, default=15); ap.add_argument('--pages', default=''); ap.add_argument('--labels', default='')
a = ap.parse_args()
if not os.path.isfile(a.pdf):
    sys.exit(f'no such PDF: {a.pdf}')
d = fitz.open(a.pdf)
labels = a.labels.split(',') if a.labels else [str(k + 1) for k in range(len(d))]
lo, hi = (int(x) for x in a.pages.split('-')) if a.pages else (1, len(d))
DEC, DOT = re.compile(r'\b\d+\.\d+\b'), re.compile(r'\s[·•]\s|&#183;')
tot = {'words': 0, 'under': 0, 'decimals': 0, 'dots': 0}
print(f'{"page":>6} {"words":>6} {"min px":>7} {"<floor":>7} {"decimals":>9} {"dots":>5}')
for k in range(lo - 1, hi):
    p = d[k]; scale = a.css_width / p.rect.width; words = 0; sizes = []; under = 0; text = []
    for b in p.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for s in line['spans']:
                t = s['text'].strip()
                if not t:
                    continue
                px = s['size'] * scale; sizes.append(px); words += len(t.split()); text.append(t)
                under += px < a.floor - 0.01
    joined = ' '.join(text); dec = len(DEC.findall(joined)); dots = len(DOT.findall(' ' + joined + ' '))
    tot['words'] += words; tot['under'] += under; tot['decimals'] += dec; tot['dots'] += dots
    print(f'{labels[k] if k < len(labels) else k + 1:>6} {words:>6} {min(sizes) if sizes else 0:>7.1f} {under:>7} {dec:>9} {dots:>5}')
print(f'{"total":>6} {tot["words"]:>6} {"":>7} {tot["under"]:>7} {tot["decimals"]:>9} {tot["dots"]:>5}')
