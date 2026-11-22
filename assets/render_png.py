#!/usr/bin/env python3
"""Render the site's two PNGs from the SVGs draw.py writes, with headless Chrome, so they can be made again.

Usage: python3 assets/draw.py && python3 assets/render_png.py
  apple-touch-icon.svg -> apple-touch-icon.png   180 x 180, the home-screen icon
  share-card.svg       -> share-card.png         1200 x 630, the link preview (og:image)
Needs Google Chrome or Chromium (set CHROME to its path if it is not found) and a network connection, since the
card's IBM Plex Mono loads from Google Fonts. Exits 1 if a PNG comes out the wrong size or the card reaches 300 KB.
These two PNGs are the repo's only binaries: .gitignore lets exactly them through.
"""
import os, shutil, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap'
JOBS = [('apple-touch-icon', 180, 180, 50_000), ('share-card', 1200, 630, 300_000)]   # name, width, height, max bytes


def chrome():
    for c in (os.environ.get('CHROME'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')):
        if c and os.path.exists(c):
            return c
    sys.exit('no Chrome found: set CHROME to the path of Google Chrome or Chromium')


def png_size(path):
    with open(path, 'rb') as f:
        return struct.unpack('>II', f.read(24)[16:24])


def main():
    exe, failed = chrome(), False
    with tempfile.TemporaryDirectory() as tmp:
        for name, w, h, cap in JOBS:
            page = os.path.join(tmp, f'{name}.html')
            with open(page, 'w') as f:
                f.write(f'<link rel="stylesheet" href="{FONTS}"><style>body{{margin:0}}</style>'
                        + open(os.path.join(HERE, f'{name}.svg')).read())
            out = os.path.join(HERE, f'{name}.png')
            subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            f'--window-size={w},{h}', '--virtual-time-budget=5000', f'--screenshot={out}',
                            f'file://{page}'], check=True, capture_output=True)
            size, dims = os.path.getsize(out), png_size(out)
            ok = dims == (w, h) and size < cap
            failed |= not ok
            print(f'{"ok  " if ok else "FAIL"} {name}.png  {dims[0]} x {dims[1]}  {size / 1000:.0f} KB (limit {cap // 1000})')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
