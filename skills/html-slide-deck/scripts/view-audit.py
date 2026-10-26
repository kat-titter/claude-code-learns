"""view-audit.py INDEX OUTDIR (a one-file deck whose slides are <template id="tN"> mounted in shadow roots, as this skill builds): every talk view mounted as the deck mounts it (stage layer), after its motion settles; lists each
visible icon (an svg with a 24x24 viewBox) with its rendered size and the visible text beside it, and every visible text
run's rendered font size. Writes OUTDIR/audit.json."""
import json, subprocess, sys
from pathlib import Path
s = open(sys.argv[1]).read(); out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
VIEWS = [('01', 0, 0), ('02a', 1, 0), ('02b', 1, 1), ('02c', 1, 2), ('03a', 2, 0), ('03b', 2, 1), ('04a', 3, 0), ('04b', 3, 1), ('04c', 3, 2),
         ('05', 4, 0), ('06', 5, 0), ('07', 6, 0), ('08', 7, 0), ('09', 8, 0), ('10', 9, 0)]
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
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
res = {}
for name, i, step in VIEWS:
    t0 = s.find(f'<template id="t{i}">'); t1 = s.find('</template>', t0) + len('</template>')
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#14171a}</style>' + s[t0:t1]
            + f'<div id="st" class="in" style="width:1280px;height:720px"></div><script>const r=document.getElementById("st").attachShadow({{mode:"open"}});'
            f'r.appendChild(document.getElementById("t{i}").content.cloneNode(true));const h=document.createElement("style");h.textContent=".pdf{{display:none!important}}.pdfv{{visibility:hidden!important}}*{{animation-duration:0s!important;animation-delay:0s!important;transition:none!important}}";r.appendChild(h);'
            f'const f=r.querySelector("[class*=step-]");if(f)f.className=f.className.replace(/step-\\d/,"step-{step}");setTimeout(()=>{{{JS}}},1500);</script>')
    p = out / f'{name}.html'; p.write_text(page)
    dom = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=1280,720', '--virtual-time-budget=9000', '--dump-dom', p.as_uri()], capture_output=True, text=True).stdout
    import re, html
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
