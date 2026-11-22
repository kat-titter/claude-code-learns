#!/usr/bin/env python3
"""Count a page's design budget: type faces, base type sizes, colours, CSS classes, shadows, gradients.

usage: design_budget.py PAGE.html [--faces 3] [--sizes 6] [--colours 24] [--classes 40] [--shadows 0] [--gradients 0]

Legibility checks fail only on contrast, overlap and tiny text; a page can pass them and still be a mess.
This fails when the system itself has grown: more faces, sizes, colours or component classes than the budget.
Sizes are CSS font sizes outside @media blocks (var() resolved); SVG font-size attributes are listed apart,
since they scale with the viewBox. Colours count every hex in the CSS, so both themes count. Exit 1 when over.
"""
import re, sys, argparse

ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
ap.add_argument('page')
for k, v in dict(faces=3, sizes=6, colours=24, classes=40, shadows=0, gradients=0).items():
    ap.add_argument('--' + k, type=int, default=v)
a = ap.parse_args()
try:
    h = open(a.page, encoding='utf-8').read()
except OSError as e:
    sys.exit(f'design_budget: cannot read {a.page}: {e.strerror}')

css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', h, re.S))
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)

def strip_media(s):                       # drop @media { ... } blocks, brace-matched
    out, i = [], 0
    while True:
        m = re.search(r'@media[^{]*\{', s[i:])
        if not m:
            return ''.join(out) + s[i:]
        out.append(s[i:i + m.start()]); j, depth = i + m.end(), 1
        while depth and j < len(s):
            depth += {'{': 1, '}': -1}.get(s[j], 0); j += 1
        i = j

base = strip_media(css)
var = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;}]+)', base))
def resolve(v):
    for _ in range(4):
        v = re.sub(r'var\((--[\w-]+)[^)]*\)', lambda m: var.get(m.group(1), m.group(0)), v)
    return v

sizes = set()
for v in re.findall(r'font-size\s*:\s*([^;}]+)', base):
    sizes |= set(re.findall(r'(\d+(?:\.\d+)?)px', resolve(v)))
for v in re.findall(r'(?<![\w-])font\s*:\s*([^;}]+)', base):
    m = re.search(r'(\d+(?:\.\d+)?)px\s*(?:/|\s)', resolve(v) + ' ')
    if m: sizes.add(m.group(1))
svg_sizes = set(re.findall(r'font-size="(\d+(?:\.\d+)?)"', h))

faces = set()
for fam in re.findall(r'family=([\w+]+)', h):
    faces.add(fam.replace('+', ' '))
for v in re.findall(r'font-family\s*:\s*([^;}]+)|(?<![\w-])font\s*:[^;}]*?(?:px|em)[^;}]*?\s([^;}]+)', css):
    first = resolve(next(x for x in v if x)).split(',')[0].strip().strip('"\'')
    if first and not first.startswith('var(') and first not in ('inherit', 'serif', 'sans-serif', 'monospace'):
        faces.add(first)

colours = {c.lower() for c in re.findall(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', css)}
classes = set(re.findall(r'\.([a-zA-Z][\w-]*)', css))
shadows = len(re.findall(r'box-shadow\s*:(?!\s*none)', css)) + len(re.findall(r'drop-shadow', h))
gradients = len(re.findall(r'gradient\(', css)) + len(re.findall(r'<(?:linear|radial)Gradient', h))

rows = [('faces', len(faces), a.faces, ', '.join(sorted(faces))),
        ('sizes', len(sizes), a.sizes, ' '.join(sorted(sizes, key=float)) + ' px'),
        ('colours', len(colours), a.colours, ''),
        ('classes', len(classes), a.classes, ''),
        ('shadows', shadows, a.shadows, ''),
        ('gradients', gradients, a.gradients, '')]
over = 0
for name, n, cap, note in rows:
    flag = 'OVER' if n > cap else 'ok'
    over += n > cap
    print(f'{name:<10}{n:>5}  / {cap:<4}{flag:<5} {note}')
print(f'svg text sizes (scale with viewBox): {" ".join(sorted(svg_sizes, key=float)) or "none"}')
print('PASS' if not over else f'FAIL: {over} over budget; remove devices until it holds')
sys.exit(1 if over else 0)
