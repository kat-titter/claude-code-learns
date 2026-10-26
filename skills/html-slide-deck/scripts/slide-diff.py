"""slide-diff.py BEFORE_DIR AFTER_DIR [--min 8]: how much each rendered view changed between two renders (PNG per view, same
names, as stage_render or render-pages writes them). Prints, per view, the share of pixels that changed visibly (any channel
off by more than 24 of 255, after a 2 px blur so anti-aliasing does not count) and flags views under --min percent as
"barely changed". Use after a round that was asked to revise every slide: each named slide either clears the bar or the
report says why it was left as it was."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

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
