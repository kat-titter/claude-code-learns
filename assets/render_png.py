#!/usr/bin/env python3
"""Render SVGs to PNGs at each SVG's own width and height, with headless Chrome, so the site's PNGs can be made again.

Usage: python3 assets/draw.py && python3 assets/render_png.py [NAME.svg ...]
  with no names: apple-touch-icon.svg (the home-screen icon) and share-card.svg (the og:image link preview)
Sizes and fonts are decided in draw.py: this script reads the size from the SVG's root and fetches each @import url
the SVG carries before rendering, so an offline run stops instead of saving the card in a fallback font. Needs Google
Chrome or Chromium (set CHROME to its path if it is not found). Exits 1 if a fetch fails, a PNG's size differs from its
SVG's, or a PNG reaches 300 KB (the share-card rule in github-practice; a bigger card loads slowly in link previews).
These PNGs are the repo's only binaries: .gitignore lets exactly them through.
"""
import os, re, shutil, struct, subprocess, sys, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = ['apple-touch-icon.svg', 'share-card.svg']
MAX_BYTES = 300_000


def chrome():
    for c in (os.environ.get('CHROME'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')):
        if c and os.path.exists(c):
            return c
    sys.exit('no Chrome found: set CHROME to the path of Google Chrome or Chromium')


def png_size(path):
    with open(path, 'rb') as f:
        return struct.unpack('>II', f.read(24)[16:24])


def render(exe, svg_path, tmp):
    svg = open(svg_path).read()
    root = re.search(r'<svg\b[^>]*>', svg)[0]
    w, h = (int(re.search(rf'\b{k}="(\d+)"', root)[1]) for k in ('width', 'height'))
    for url in re.findall(r'@import url\(([^)]+)\)', svg):
        try:
            urllib.request.urlopen(url, timeout=10).read()
        except OSError as e:
            sys.exit(f'cannot fetch {url} ({e}): the PNG would fall back to another font')
    page = os.path.join(tmp, 'page.html')
    with open(page, 'w') as f:
        f.write('<style>body{margin:0}</style>' + svg)
    out = svg_path[:-4] + '.png'
    subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    f'--window-size={w},{h}', '--virtual-time-budget=5000', f'--screenshot={out}', f'file://{page}'],
                   check=True, capture_output=True)
    got, size = png_size(out), os.path.getsize(out)
    ok = got == (w, h) and size < MAX_BYTES
    print(f'{"ok  " if ok else "FAIL"} {os.path.basename(out)}  {got[0]} x {got[1]} (SVG {w} x {h})  {size / 1000:.0f} KB')
    return ok


def main():
    exe = chrome()
    names = sys.argv[1:] or DEFAULT
    with tempfile.TemporaryDirectory() as tmp:
        results = [render(exe, n if os.path.isabs(n) else os.path.join(HERE, os.path.basename(n)), tmp) for n in names]
    sys.exit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
