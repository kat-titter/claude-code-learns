#!/usr/bin/env python3
"""Render every page of a PDF to PNG for review: look at each click view as the room will see it.

Usage: render-pages.py DECK.pdf OUTDIR [--dpi 96] [--labels "01,02a,02b,..."] [--only 02a,A1]
Needs PyMuPDF:  python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf
                then run this script with ~/.cache/pdfenv/bin/python
Writes OUTDIR/NN-LABEL.png (labels default to page numbers). Read the PNGs, don't trust the HTML: overflow, text under
an overlay, a caption crossing a column only show up rendered.
"""
import argparse, os, sys
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import fitz
except ImportError:
    sys.exit('PyMuPDF missing: python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf')
ap = argparse.ArgumentParser(usage='render-pages.py DECK.pdf OUTDIR [--dpi 96] [--labels L] [--only L]')
ap.add_argument('pdf'); ap.add_argument('out')
ap.add_argument('--dpi', type=int, default=96); ap.add_argument('--labels', default=''); ap.add_argument('--only', default='')
a = ap.parse_args()
if not os.path.isfile(a.pdf):
    sys.exit(f'no such PDF: {a.pdf}')
os.makedirs(a.out, exist_ok=True)
d = fitz.open(a.pdf)
labels = a.labels.split(',') if a.labels else [str(k + 1) for k in range(len(d))]
if len(labels) != len(d):
    sys.exit(f'{len(labels)} labels for {len(d)} pages: the deck and its labels disagree (a view added or dropped?)')
only = set(a.only.split(',')) if a.only else None
for k, p in enumerate(d):
    if only and labels[k] not in only:
        continue
    p.get_pixmap(dpi=a.dpi).save(f'{a.out}/{k + 1:02d}-{labels[k]}.png')
print(len(d), 'pages:', ' '.join(labels))
