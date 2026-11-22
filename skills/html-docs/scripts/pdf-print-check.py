#!/usr/bin/env python3
"""Measure a printed PDF instead of eyeballing it: how full each page is, what runs past the edge, and one sheet of
every page to look at.

Usage: pdf-print-check.py DOC.pdf [--sheet OUT.png] [--gap 0.25] [--margin-mm 16] [--lr-mm 14]
Needs PyMuPDF and Pillow:  python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf pillow
                           then run this script with ~/.cache/pdfenv/bin/python

Per page it reports fill (how far down the content reaches), tail (the empty run at the foot) and hole (the largest
empty run inside the content), each as a share of the printable height, ignoring the top and bottom margins where a
running footer lives. A tail or hole over --gap is flagged: look at what the next page opens with, because that block
did not fit. It then lists text that runs past the left or right printable edge - clipped on paper. Chrome drops what
lies wholly past the edge, so only words cut mid-way show up; one of them means a whole column may be missing.

Exit 1 when any text is clipped. Tails are reported, not failed: a figure that will not fit leaves one, and splitting
a drawing is worse than the gap.

Validated on a peptide explainer, 2026-11-06: before, 13 of 45 pages more than a quarter blank (worst 89%, a table that
jumped whole to the next page) and 6 cut words, which were the visible edge of a matrix column of notes and citation
markers printed off the page; after the print rules in html-docs section 2, 8 of 47 (each a tall figure; the last
page) and 0 clipped.
"""
import argparse, sys
try:
    import fitz, numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit('needs PyMuPDF and Pillow: python3 -m venv ~/.cache/pdfenv && ~/.cache/pdfenv/bin/pip install pymupdf pillow')

ap = argparse.ArgumentParser()
ap.add_argument('pdf'); ap.add_argument('--sheet'); ap.add_argument('--gap', type=float, default=0.25)
ap.add_argument('--margin-mm', type=float, default=16, help='top and bottom margin, skipped when measuring fill')
ap.add_argument('--lr-mm', type=float, default=14, help='left and right margin, the edge text must stay inside')
a = ap.parse_args()
d = fitz.open(a.pdf); dpi = 50; mm = 72 / 25.4
rows, thumbs, clipped = [], [], []
for k, p in enumerate(d):
    pix = p.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    g = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    m = int(a.margin_mm / 25.4 * dpi)
    ink = (g[m:pix.height - m] < 235).any(axis=1)
    H, idx = len(ink), np.flatnonzero(ink)
    if len(idx):
        first, last = idx[0], idx[-1]
        runs, run = [], 0
        for v in ink[first:last + 1]:
            if v: runs.append(run); run = 0
            else: run += 1
        rows.append((k + 1, (last + 1) / H, (H - 1 - last) / H, max(runs) / H if runs else 0))
    else:
        rows.append((k + 1, 0, 1, 1))
    thumbs.append(pix)
    L, R = a.lr_mm * mm - 2, p.rect.width - a.lr_mm * mm + 2
    for b in p.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            for s in ln['spans']:
                x0, _, x1, _ = s['bbox']
                if s['text'].strip() and (x1 > R or x0 < L):
                    clipped.append((k + 1, s['text'].strip()[:30], round(x0), round(x1)))

flag = lambda r: r[2] > a.gap or r[3] > a.gap
for n, fill, tail, hole in rows:
    note = (' <- tail' if tail > a.gap else '') + (' <- hole' if hole > a.gap else '')
    print(f'p{n:02d}  fill {fill:4.0%}  tail {tail:4.0%}  hole {hole:4.0%}{note}')
print(f'{len(rows)} pages; {sum(map(flag, rows))} with an empty run over {a.gap:.0%}; '
      f'mean fill {np.mean([r[1] for r in rows]):.0%}')
for n, fill, tail, hole in rows:
    if tail > a.gap and n < len(d):
        print(f'  p{n:02d} tail: the next page opens with  ' + ' '.join(d[n].get_text().split())[:70])
print(f'clipped text: {len(clipped)}')
for c in clipped[:20]:
    print(f'  p{c[0]:02d}  {c[1]!r}  x {c[2]}-{c[3]} pt')

if a.sheet:
    w, h = thumbs[0].width, thumbs[0].height
    cols = 9; nrow = -(-len(thumbs) // cols)
    sheet = Image.new('RGB', (cols * (w + 10) + 10, nrow * (h + 26) + 10), (180, 180, 180))
    dr = ImageDraw.Draw(sheet)
    for i, pix in enumerate(thumbs):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 26)
        sheet.paste(Image.frombytes('L', (pix.width, pix.height), pix.samples).convert('RGB'), (x, y))
        r = rows[i]
        dr.text((x + 2, y + h + 4), f'p{r[0]}' + ('  tail' if r[2] > a.gap else '') + ('  hole' if r[3] > a.gap else ''),
                fill=(200, 0, 60) if flag(r) else (0, 0, 0))
    sheet.save(a.sheet)
    print('sheet', a.sheet)
sys.exit(1 if clipped else 0)
