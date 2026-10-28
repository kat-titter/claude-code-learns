#!/usr/bin/env python3
"""slide-diff.py BEFORE_DIR AFTER_DIR [--min 8]: how much each rendered view changed between two folders of PNGs (one per
view, same names, as render-pages.py writes them from the PDF before and after). Prints, per view, the share of pixels that changed visibly (any channel
off by more than 24 of 255, after a 2 px blur so anti-aliasing does not count) and flags views under --min percent as
"barely changed". Use after a round that was asked to revise every slide: each named slide either clears the bar or the
report says why it was left as it was."""
import sys
from pathlib import Path

if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import numpy as np
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit('needs numpy and Pillow: pip install numpy pillow (or the venv with them)')
if len(sys.argv) < 3 or not all(Path(d).is_dir() for d in sys.argv[1:3]):
    sys.exit('usage: slide-diff.py BEFORE_DIR AFTER_DIR [--min 8] (both folders must exist)')

a, b = Path(sys.argv[1]), Path(sys.argv[2])
low = float(sys.argv[sys.argv.index('--min') + 1]) if '--min' in sys.argv else 8.0
rows, flat = [], 0
for p in sorted(b.glob('*.png')):
    q = a / p.name
    if not q.exists():
        rows.append((p.stem, None)); continue
    x, y = (np.asarray(Image.open(f).convert('RGB').resize((640, 360)).filter(ImageFilter.GaussianBlur(1)), dtype=np.int16) for f in (q, p))
    share = 100 * float((np.abs(x - y).max(axis=2) > 24).mean())
    rows.append((p.stem, share)); flat += share < low
for name, share in rows:
    print(f'{name:12s} {"new view" if share is None else f"{share:5.1f}%"}{"   barely changed" if share is not None and share < low else ""}')
print(f'{flat} of {len(rows)} views under {low:g}%')
