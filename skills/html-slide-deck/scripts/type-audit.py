"""type-audit.py STAGE.pdf --labels 01,02a,... [--talk N] [--scale 22,28,44,72,92,104] [--fonts Unnamed-T3,IBMPlexMono]

Every talk view's text runs against the deck's type scale. A run fails when its size is more than 0.35 px from every size on
the scale, or when its font is not one of the deck's (a fallback such as Menlo or Helvetica Neue, which is what a typed arrow
or a Greek letter turns into when the web font's subset lacks it). Chrome embeds a variable web font as Type 3, so the deck's
text face shows as "Unnamed-T3". Prints each view's sizes and fonts, then every failing run; exits 1 if any fails.
Use on the stage PDF (the talk layer printed), so the reader's small notes do not count."""
import argparse
import collections
import sys

import fitz

ap = argparse.ArgumentParser()
ap.add_argument('pdf')
ap.add_argument('--labels', required=True, help='comma-separated view names, in page order, or a file holding them')
ap.add_argument('--talk', type=int, help='how many pages are talk views (default: labels not starting with A)')
ap.add_argument('--scale', default='22,28,44,72,92,104')
ap.add_argument('--fonts', default='Unnamed-T3,IBMPlexMono')
a = ap.parse_args()
labels = (open(a.labels).read() if a.labels.endswith('.txt') else a.labels).strip().split(',')
scale = [float(x) for x in a.scale.split(',')]
fonts = tuple(a.fonts.split(','))
talk = a.talk or sum(1 for l in labels if not l.startswith('A'))
bad = []
for i, page in enumerate(fitz.open(a.pdf)):
    if i >= talk:
        break
    seen = collections.defaultdict(list)
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for s in line['spans']:
                t = s['text'].strip()
                if not t:
                    continue
                size = round(s['size'] * 1280 / page.rect.width, 1)
                font = s['font'].split('+')[-1].replace('-Regular', '')
                seen[(size, font)].append(t)
                if min(abs(size - z) for z in scale) > 0.35 or not font.startswith(fonts):
                    bad.append((labels[i], size, font, t))
    print(f'{labels[i]:4s} {len({z for z, _ in seen})} sizes {sorted({z for z, _ in seen})}  fonts {sorted({f for _, f in seen})}')
for v, size, font, t in bad:
    print(f'  OFF {v:4s} {size:5.1f} {font:18s} {t[:70]}')
print(f'{len(bad)} runs off the scale' if bad else 'every talk run on the scale, in the deck\'s fonts')
sys.exit(1 if bad else 0)
