"""pdf-overlaps.py DECK.pdf [--labels 01,02a,...]: text that sits on other text in a printed deck.

The reader's layer prints captions and notes the stage never shows, so a stage check misses them landing on a card,
a legend or a figure label. This reads every text run of the PDF and reports pairs whose glyph cores overlap. A run
drawn twice in the same place (a text shadow, a duplicate layer) is skipped. Exits 1 when any pair overlaps.
"""
import argparse
import sys

import fitz


def runs(page):
    """Each text run's glyph core (the line box minus its leading) and its text."""
    out = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                text = span['text'].strip()
                if text:
                    r = fitz.Rect(span['bbox'])
                    r.y0 += r.height * 0.2
                    r.y1 -= r.height * 0.2
                    out.append((r, text))
    return out


def same_run(a, b):
    """The same text drawn twice within a pixel or two: a shadow or a duplicate layer, not a collision."""
    (ra, ta), (rb, tb) = a, b
    return ta == tb and abs(ra.x0 - rb.x0) < 3 and abs(ra.y0 - rb.y0) < 3


def overlaps(page):
    spans = runs(page)
    hits = []
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            inter = spans[i][0] & spans[j][0]
            if not inter.is_empty and inter.width > 2 and inter.height > 2 and not same_run(spans[i], spans[j]):
                hits.append((spans[i][1][:30], spans[j][1][:30], tuple(round(v) for v in spans[i][0].tl)))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('pdf')
    ap.add_argument('--labels', default='', help='comma-separated page names, e.g. 01,02a,02b')
    args = ap.parse_args()
    doc = fitz.open(args.pdf)
    labels = [s for s in args.labels.split(',') if s]
    total = 0
    for k, page in enumerate(doc):
        hits = overlaps(page)
        if hits:
            total += len(hits)
            name = labels[k] if k < len(labels) else str(k + 1)
            print(f'{name}: {len(hits)} overlapping, e.g. {hits[:3]}')
    print(f'{total} overlapping text pairs in {len(doc)} pages')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
