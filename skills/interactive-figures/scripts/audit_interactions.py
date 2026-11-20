#!/usr/bin/env python3
"""Audit a page's interactive figures for the things that make interaction feel clunky or shut people out.

Usage: python3 audit_interactions.py PAGE.html|URL [--width 400] [--json]
Needs Playwright (pip install playwright) and an installed Chrome (channel 'chrome'); falls back to Playwright's Chromium.

Checks, at the given width:
  targets    controls smaller than 44 x 44 px (inline links inside running text are exempt, as in WCAG 2.5.8)
  names      controls with no accessible name (aria-label, text, title or alt)
  focus      controls that show no visible change when reached with Tab
  clicks     page errors raised by clicking each control
  motion     figures that keep moving when the reader asks for reduced motion
  no-js      figures that are empty with JavaScript off (every figure should draw a first frame without it)
Each finding is something to look at, not a verdict. Stdlib plus Playwright.
"""
import json
import pathlib
import sys

if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit('playwright missing: pip install playwright && playwright install chromium (or the venv that has it)')

CONTROLS = """[...document.querySelectorAll('button, a[href], input, select, textarea, [role=button], [tabindex]:not([tabindex="-1"])')]
  .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; })"""


def launch(p):
    try:
        return p.chromium.launch(channel='chrome', args=['--disable-gpu'])
    except Exception:
        return p.chromium.launch(args=['--disable-gpu'])


def audit(url, width):
    out = {'targets': [], 'names': [], 'focus': [], 'clicks': [], 'motion': [], 'no-js': []}
    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={'width': width, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_timeout(800)
        info = pg.evaluate("() => " + CONTROLS + """.map((e, i) => { e.dataset.auditI = i; const r = e.getBoundingClientRect();
            const name = (e.getAttribute('aria-label') || (e.labels && e.labels[0] ? e.labels[0].textContent : '') || e.textContent || e.title || e.getAttribute('alt') || e.getAttribute('placeholder') || '').trim().slice(0, 50);
            const inline = e.tagName === 'A' && !!e.closest('p, li, figcaption, td');
            return {i, tag: e.tagName.toLowerCase(), cls: String(e.className.baseVal ?? e.className).slice(0, 30), w: Math.round(r.width), h: Math.round(r.height), name, inline}; })""")
        for c in info:
            label = f"{c['tag']}.{c['cls']} '{c['name'][:30]}'"
            if not c['inline'] and min(c['w'], c['h']) < 44:
                out['targets'].append(f"{label} {c['w']}x{c['h']}")
            if not c['name']:
                out['names'].append(label)
        # keyboard: Tab through and see whether the focused control looks different
        pg.mouse.click(1, 1)
        seen = set()
        for _ in range(min(len(info) + 5, 120)):
            pg.keyboard.press('Tab')
            r = pg.evaluate("""() => { const e = document.activeElement; if (!e || !e.dataset.auditI) return null;
                const s = getComputedStyle(e), shown = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none';
                const svg = e.querySelector('circle, rect, path'); const inner = svg ? getComputedStyle(svg).strokeWidth : '';
                return {i: e.dataset.auditI, shown, inner}; }""")
            if not r or r['i'] in seen:
                continue
            seen.add(r['i'])
            if not r['shown']:
                blur = pg.evaluate("i => { const e = document.querySelector('[data-audit-i=\"' + i + '\"]'); e.blur(); const svg = e.querySelector('circle, rect, path'); return svg ? getComputedStyle(svg).strokeWidth : ''; }", r['i'])
                if blur == r['inner']:
                    c = info[int(r['i'])]
                    out['focus'].append(f"{c['tag']}.{c['cls']} '{c['name'][:30]}'")
                pg.focus(f'[data-audit-i="{r["i"]}"]')
        # clicks
        before = len(errs)
        for c in info[:60]:
            if c['tag'] in ('a',):
                continue
            try:
                pg.click(f'[data-audit-i="{c["i"]}"]', timeout=800, force=True)
            except Exception:
                pass
            if len(errs) > before:
                out['clicks'].append(f"{c['tag']}.{c['cls']} '{c['name'][:30]}': {errs[-1][:80]}")
                before = len(errs)
        pg.close()
        # reduced motion: nothing should keep animating
        pg = b.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
        pg.goto(url)
        pg.wait_for_timeout(700)
        snap = "() => [...document.querySelectorAll('figure svg, .hero svg, canvas')].map(s => s.tagName === 'CANVAS' ? s.toDataURL().length : s.innerHTML)"
        a = pg.evaluate(snap)
        pg.wait_for_timeout(900)
        z = pg.evaluate(snap)
        out['motion'] = [f'figure graphic #{i}' for i, (x, y) in enumerate(zip(a, z)) if x != y]
        pg.close()
        # no JavaScript: every figure graphic should still draw something
        ctx = b.new_context(java_script_enabled=False, viewport={'width': width, 'height': 900})
        pg = ctx.new_page()
        pg.goto(url)
        out['no-js'] = pg.evaluate("""() => [...document.querySelectorAll('figure svg')].map((s, i) => [i, s.getAttribute('aria-label') || s.id || '',
            s.querySelectorAll('circle, rect, path, line, polyline, polygon, text').length, s.getBoundingClientRect().width])
            .filter(x => x[2] === 0 && x[3] > 24).map(x => 'figure svg #' + x[0] + ' ' + x[1].slice(0, 40))""")
        ctx.close()
        b.close()
    out['errors_on_load'] = errs[:5]
    return out


if __name__ == '__main__':
    if sys.argv[1:2] in (['-h'], ['--help']):
        print(__doc__); sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    if not pathlib.Path(args[0]).exists():
        sys.exit(f'no such file: {args[0]}')
    width = int(sys.argv[sys.argv.index('--width') + 1]) if '--width' in sys.argv else 400
    src = args[0]
    url = src if '://' in src else pathlib.Path(src).resolve().as_uri()
    res = audit(url, width)
    if '--json' in sys.argv:
        print(json.dumps(res, indent=1))
    else:
        for k, v in res.items():
            print(f'{k}: {len(v)}' + ''.join(f'\n  - {x}' for x in v[:8]) + (f'\n  ... {len(v) - 8} more' if len(v) > 8 else ''))
