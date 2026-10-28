#!/usr/bin/env python3
"""view-audit.py INDEX OUTDIR [--labels 01,02a,...] (a one-file deck whose slides are <template id="tN"> mounted in shadow
roots, as this skill builds): every view mounted as the deck mounts it (stage layer), after its motion settles; lists
each visible icon (an svg with a 24x24 viewBox) with its rendered size and the visible text beside it, and every visible
text run's rendered font size. Writes OUTDIR/audit.json.

Views come from the deck's META list (slide k has as many views as its `steps` lists are long), named 01, 02a, 02b ...;
--labels renames them in order. Without META, one view per template. CHROME overrides the Chrome path."""
import argparse, html, json, os, re, subprocess, sys
from pathlib import Path
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
ap = argparse.ArgumentParser(usage='view-audit.py INDEX.html OUTDIR [--labels L]')
ap.add_argument('index'); ap.add_argument('out'); ap.add_argument('--labels', default='')
a = ap.parse_args()
if not Path(a.index).is_file():
    sys.exit(f'no such deck: {a.index}')
s = open(a.index).read(); out = Path(a.out).resolve(); out.mkdir(exist_ok=True)
CH = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
if not os.path.exists(CH):
    sys.exit(f'Chrome not found at {CH}: set CHROME to its path')


def views(deck):
    """(label, template index, step) for every view, read from the deck's META list, else one per template."""
    m = re.search(r'\bMETA\s*=\s*(\[.*?\])\s*;', deck, re.S)
    try:
        meta = json.loads(m.group(1)) if m else None
    except ValueError:
        meta = None
    if meta is None:
        print('no JSON META list in the deck: one view per template', file=sys.stderr)
        meta = [{} for _ in re.findall(r'<template id="t\d+">', deck)]
    found = []
    for i, slide in enumerate(meta):
        steps = slide.get('steps') if isinstance(slide, dict) else None
        lists = steps.values() if isinstance(steps, dict) else [steps] if isinstance(steps, list) else []
        n = max([len(v) for v in lists if isinstance(v, list)] or [1])
        found += [(f'{i + 1:02d}' + ('abcdefghij'[k] if n > 1 else ''), i, k) for k in range(n)]
    return found


VIEWS = views(s)
if a.labels:
    names = a.labels.split(',')
    if len(names) != len(VIEWS):
        sys.exit(f'{len(names)} labels for {len(VIEWS)} views: the deck and its labels disagree (a view added or dropped?)')
    VIEWS = [(n, i, k) for n, (_, i, k) in zip(names, VIEWS)]
JS = r'''
const vis = e => { for (let n = e; n && n !== r.host; n = n.parentNode || n.host) { if (n.nodeType !== 1) continue; const c = getComputedStyle(n);
  if (c.display === 'none' || c.visibility === 'hidden' || parseFloat(c.opacity) < 0.05) return false; } const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
const icons = [], texts = [];
r.querySelectorAll('svg').forEach(sv => { const vb = (sv.getAttribute('viewBox') || '').trim(); if (vb !== '0 0 24 24' || !vis(sv)) return;
  const b = sv.getBoundingClientRect(); let p = sv.parentElement, t = '';
  for (let k = 0; k < 3 && p && !t; k++, p = p.parentElement) { t = [...p.childNodes].filter(n => n !== sv && !(n.contains && n.contains(sv))).map(n => n.nodeType === 3 ? n.textContent : (vis(n) ? n.innerText || n.textContent : '')).join(' ').trim(); }
  icons.push({w: Math.round(b.width), x: Math.round(b.left), y: Math.round(b.top), text: t.slice(0, 40)}); });
const walker = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let n;
while ((n = walker.nextNode())) { const t = n.textContent.trim(); if (!t) continue; const e = n.parentElement; if (!e || !vis(e)) continue;
  let px; if (e instanceof SVGElement) { const fs = parseFloat(getComputedStyle(e).fontSize); const m = e.getScreenCTM(); px = fs * (m ? Math.hypot(m.a, m.b) : 1); } else px = parseFloat(getComputedStyle(e).fontSize);
  const c = getComputedStyle(e); const b = e.getBoundingClientRect(); const h2 = !!e.closest('h2');
  texts.push({t: t.slice(0, 30), px: Math.round(px * 10) / 10, w: c.fontWeight, i: c.fontStyle === 'italic', f: c.fontFamily.includes('Mono') ? 'mono' : 'sans',
              x: Math.round(b.left), y: Math.round(b.top), anchor: e.getAttribute && e.getAttribute('text-anchor') || 'start', h2}); }
document.body.setAttribute('data-out', JSON.stringify({icons, texts}));
'''
res = {}
for name, i, step in VIEWS:
    t0 = s.find(f'<template id="t{i}">')
    if t0 < 0:
        print(f'view {name}: no <template id="t{i}"> in the deck', file=sys.stderr); sys.exit(2)
    t1 = s.find('</template>', t0) + len('</template>')
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#14171a}</style>' + s[t0:t1]
            + f'<div id="st" class="in" style="width:1280px;height:720px"></div><script>const r=document.getElementById("st").attachShadow({{mode:"open"}});'
            f'r.appendChild(document.getElementById("t{i}").content.cloneNode(true));const h=document.createElement("style");h.textContent=".pdf{{display:none!important}}.pdfv{{visibility:hidden!important}}*{{animation-duration:0s!important;animation-delay:0s!important;transition:none!important}}";r.appendChild(h);'
            f'const f=r.querySelector("[class*=step-]");if(f)f.className=f.className.replace(/step-\\d/,"step-{step}");setTimeout(()=>{{{JS}}},1500);</script>')
    p = out / f'{name}.html'; p.write_text(page)
    dom = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=1280,720', '--virtual-time-budget=9000', '--dump-dom', p.as_uri()], capture_output=True, text=True).stdout
    m = re.search(r'data-out="([^"]*)"', dom)
    res[name] = json.loads(html.unescape(m.group(1))) if m else None
(out / 'audit.json').write_text(json.dumps(res, indent=1))
def near_miss(ts):
    xs = sorted({t['x'] for t in ts if not t['h2'] and t['anchor'] == 'start' and t['y'] > 190})
    return [(a, b) for a, b in zip(xs, xs[1:]) if 2 <= b - a <= 10]
for name, v in res.items():
    if not v: print(name, 'NO DATA'); continue
    bold = [t['t'][:16] for t in v['texts'] if not t['h2'] and str(t['w']) in ('600', '700', '800', 'bold')]
    ital = [t['t'][:16] for t in v['texts'] if t['i']]
    print(f"{name}: bold {len(bold)} {bold[:8]} | italic {ital[:4]} | near-miss left edges {near_miss(v['texts'])[:6]}")
    small = [x for x in v['icons'] if x['w'] < 24]; orphan = [x for x in v['icons'] if not x['text']]
    sizes = sorted({x['px'] for x in v['texts']})
    print(f"{name}: icons {len(v['icons'])}, small {[(x['w'], x['text'][:16]) for x in small][:6]}, orphan {[(x['w'], x['x'], x['y']) for x in orphan][:6]}")
    print(f"     text sizes {sizes[:14]}{' ...' if len(sizes) > 14 else ''}; under 18px: {[(x['t'][:18], x['px']) for x in v['texts'] if x['px'] < 18][:6]}")
