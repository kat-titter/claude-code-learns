#!/usr/bin/env python3
"""How light is this page? A static, no-browser check of an HTML doc or deck's weight and interactivity.

Usage: python3 light-audit.py PAGE.html [PAGE2.html ...] [--deck] [--json]

Reports per page:
  weight     file size, inline script and style, embedded data URIs, external requests by host
  libraries  frameworks and big libraries the page loads (React, Vue, jQuery, D3, three.js, Plotly ...)
  asks       what the page asks the reader to do: folds, buttons, inputs, hover notes, keys, per 1,000 words
  care       print rules, reduced-motion rules beside any motion, dark-mode tokens, ids on section headings,
             hover rules with a focus twin, notes reachable without a mouse
Flags are places to look, not verdicts. --deck relaxes the doc-only checks (heading ids, word-count density).
Stdlib only. Pair with interactive-figures/scripts/audit_interactions.py (browser: targets, focus, no-JS frames).
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

JS_BUDGET_KB = {'doc': 40, 'deck': 80}   # inline script a light doc or deck rarely needs more than
DATA_URI_KB = 500                        # embedded images past this weigh down every load and every diff
# by the file a page loads, or the banner a bundled copy carries (a page's own `new Chart(` is not Chart.js)
LIBS = {
    'React': (r'react(-dom)?[\w.@/-]*\.js', r'@license React|React v\d'),
    'Vue': (r'vue[\w.@/-]*\.js', r'Vue\.js v\d'),
    'jQuery': (r'jquery[\w.@/-]*\.js', r'jQuery v\d|jquery\.org/license'),
    'D3': (r'\bd3[\w.@/-]*\.js', r'd3js\.org v\d'),
    'three.js': (r'three[\w.@/-]*\.js', r'REVISION\s*=\s*["\']1\d\d|threejs\.org/license'),
    'Plotly': (r'plotly[\w.@/-]*\.js', r'plotly\.js v\d'),
    'Chart.js': (r'chart(\.umd)?[\w.@/-]*\.js', r'Chart\.js v\d|chartjs\.org'),
    'Mermaid': (r'mermaid[\w.@/-]*\.js', r'mermaid\.initialize'),
    'Tailwind (CDN)': (r'cdn\.tailwindcss\.com', r'tailwindcss v\d'),
    'p5.js': (r'\bp5[\w.@/-]*\.js', r'p5\.js v\d'),
}
FONT_HOSTS = {'fonts.googleapis.com', 'fonts.gstatic.com'}
NOTE_CLASS = re.compile(r'\b(term|tooltip|gloss|has-tip)\b')   # 'note' is usually a side note, not a hover note
NOTE_ATTRS = ('data-gloss', 'data-tip', 'data-tooltip', 'data-note', 'data-card', 'data-def', 'data-term', 'aria-describedby')


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.text, self.scripts, self.styles = [], [], [], []
        self.ext, self.counts, self.headings = [], {}, []
        self.style_attr, self.data_uri_bytes, self._buf = [], 0, None

    def bump(self, k, n=1):
        self.counts[k] = self.counts.get(k, 0) + n

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.stack.append((tag, a.get('id')))
        for v in a.values():
            if v and v.startswith('data:'):
                self.data_uri_bytes += len(v)
        if a.get('style'):
            self.style_attr.append(a['style'])
        src = a.get('src') or (a.get('href') if tag == 'link' else None)
        if src and urlparse(src).scheme in ('http', 'https') and (tag != 'link' or 'stylesheet' in (a.get('rel') or '') or a.get('rel') == 'preload'):
            self.ext.append((tag, src))
        if tag == 'script':
            self._buf = [] if not a.get('src') else None
            if a.get('src'):
                self.scripts.append(('src', a['src']))
        elif tag == 'style':
            self._buf = []
        if tag == 'details':
            self.bump('folds')
        elif tag == 'button':
            self.bump('buttons')
        elif tag in ('input', 'select', 'textarea'):
            self.bump('inputs')
        elif tag in ('video', 'audio') and 'autoplay' in a:
            self.bump('autoplay')
        if tag == 'abbr' and a.get('title'):
            self.bump('notes')
            self.bump('notes_title_only')
        elif a.get('title') and tag not in ('a', 'abbr', 'iframe', 'link', 'svg', 'title', 'button', 'input', 'select', 'textarea') and 'role' not in a:
            self.bump('notes_title_only')
        if NOTE_CLASS.search(a.get('class') or '') or any(k in a for k in NOTE_ATTRS):
            self.bump('notes')
            if 'tabindex' not in a and tag not in ('a', 'button'):
                self.bump('notes_no_focus')
        if any(k.startswith('on') for k in a):
            self.bump('inline_handlers')
        if re.fullmatch(r'h[1-3]', tag):
            # a heading links if it or its section/article carries an id
            sec = next((i for t, i in reversed(self.stack[:-1]) if t in ('section', 'article') and i), None)
            self.headings.append([tag, a.get('id') or sec, ''])

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self._buf is not None:
            (self.scripts if tag == 'script' else self.styles).append(('inline', ''.join(self._buf)))
            self._buf = None
        while self.stack:
            if self.stack.pop()[0] == tag:
                break

    def handle_data(self, d):
        if self._buf is not None:
            self._buf.append(d)
            return
        tags = [t for t, _ in self.stack]
        if self.headings and self.headings[-1][2] == '' and tags and re.fullmatch(r'h[1-3]', tags[-1]):
            self.headings[-1][2] = d.strip()[:50]
        if not any(t in ('script', 'style', 'svg') for t in tags[-6:]):
            self.text.append(d)


def audit(path, deck=False):
    raw = Path(path).read_text(errors='replace')
    p = Page()
    p.feed(raw)
    js = '\n'.join(s for kind, s in p.scripts if kind == 'inline')
    css = '\n'.join(s for _, s in p.styles) + '\n' + '\n'.join(p.style_attr)
    words = len(re.findall(r"[A-Za-z0-9][\w'’-]*", ' '.join(p.text)))
    hosts = {}
    for _, u in p.ext:
        h = urlparse(u).netloc
        hosts[h] = hosts.get(h, 0) + 1
    srcs = ' '.join(u for _, u in p.scripts if _ == 'src') + ' ' + ' '.join(u for t, u in p.ext if t == 'script')
    libs = sorted({n for n, (src_rx, banner_rx) in LIBS.items() if re.search(src_rx, srcs, re.I) or re.search(banner_rx, js)})
    events = {}
    for ev in re.findall(r"addEventListener\(\s*['\"](\w+)", js):
        events[ev] = events.get(ev, 0) + 1
    keys = len(re.findall(r"\.key\s*===?\s*['\"]|keydown|keyup", js))
    hover_js = sum(events.get(e, 0) for e in ('mouseover', 'mouseenter', 'pointerenter', 'pointerover'))
    focus_js = sum(events.get(e, 0) for e in ('focus', 'focusin', 'click', 'pointerdown', 'keydown'))
    hover_css = len(re.findall(r':hover\b', css))
    focus_css = len(re.findall(r':focus(-visible|-within)?\b', css))
    motion = len(re.findall(r'@keyframes\b', css)) + len(re.findall(r'requestAnimationFrame', js)) + len(re.findall(r'animation-timeline', css))
    asks = p.counts.get('folds', 0) + p.counts.get('buttons', 0) + p.counts.get('inputs', 0) + p.counts.get('notes', 0)
    m = {
        'file_kb': round(len(raw.encode()) / 1024, 1),
        'script_kb': round(len(js.encode()) / 1024, 1),
        'style_kb': round(len(css.encode()) / 1024, 1),
        'data_uri_kb': round(p.data_uri_bytes / 1024, 1),
        'words': words,
        'external': hosts,
        'libraries': libs,
        'folds': p.counts.get('folds', 0), 'buttons': p.counts.get('buttons', 0), 'inputs': p.counts.get('inputs', 0),
        'notes': p.counts.get('notes', 0), 'keys': keys, 'listeners': events,
        'asks_per_1k_words': round(1000 * asks / words, 1) if words else None,
        'motion': motion,
        'print_rules': bool(re.search(r'@media\s+print|@page\b', css)),
        'reduced_motion_rules': 'prefers-reduced-motion' in css + js,
        'dark_mode': 'prefers-color-scheme' in css + js or 'data-theme' in raw,
        'headings_without_id': [h[2] or h[0] for h in p.headings if not h[1] and h[0] != 'h1'],
    }
    flags = []
    if libs:
        flags.append(f"loads {', '.join(libs)}: a document rarely needs a framework; hand-write the few lines it uses, or keep it for a figure that truly needs it")
    budget = JS_BUDGET_KB['deck' if deck else 'doc']
    if m['script_kb'] > budget:
        flags.append(f"{m['script_kb']} KB of inline script (light {'decks' if deck else 'docs'} stay under {budget} KB): look for a mini-app hiding in the page")
    if m['data_uri_kb'] > DATA_URI_KB:
        flags.append(f"{m['data_uri_kb']} KB of images embedded as data URIs: draw them as inline SVG, or serve compressed files beside the page")
    other = {h: n for h, n in hosts.items() if h not in FONT_HOSTS}
    if other:
        flags.append('fetches from ' + ', '.join(f'{h} ({n})' for h, n in other.items()) + ': inline it or pin exact versions so the file stands alone')
    if p.counts.get('notes_title_only'):
        flags.append(f"{p.counts['notes_title_only']} note(s) live only in a title attribute: phones and keyboards never see them; use a focusable term with a card")
    focus_by_script = bool(re.search(r"tabIndex\s*=|setAttribute\(\s*['\"]tabindex", js))
    if p.counts.get('notes_no_focus') and not focus_by_script:
        flags.append(f"{p.counts['notes_no_focus']} hover note(s) without tabindex: give each term tabindex=0 so focus opens its card")
    if hover_css and not focus_css:
        flags.append(f'{hover_css} :hover rule(s) and no :focus twin: mirror each hover state on :focus-visible')
    if hover_js and not focus_js:
        flags.append('hover listeners with no click or focus counterpart: a tap must do what a hover does')
    if events.get('wheel') and 'preventDefault' in js:
        flags.append('a wheel listener calls preventDefault: let the page scroll as the reader expects')
    if re.search(r'scroll-snap-type:\s*y\s+mandatory', css) and not deck:
        flags.append('mandatory scroll snapping on a document: readers lose their place; use proximity or none')
    if p.counts.get('autoplay'):
        flags.append(f"{p.counts['autoplay']} media element(s) autoplay: start on the reader's action")
    if motion and not m['reduced_motion_rules']:
        flags.append(f'{motion} motion source(s) and no prefers-reduced-motion rule: settle every animation at its end state when asked')
    if not m['print_rules']:
        flags.append('no print rules: add @media print (open folds, hide controls, settle motion) so the PDF reads whole')
    if not deck and m['headings_without_id']:
        flags.append(f"{len(m['headings_without_id'])} section heading(s) without an id (" + ', '.join(m['headings_without_id'][:3]) + '): ids give deep links and stable edit targets')
    if not deck and m['asks_per_1k_words'] is not None and m['asks_per_1k_words'] > 40:
        flags.append(f"{m['asks_per_1k_words']} asks per 1,000 words: more controls than reading; fold the rest or let one control drive a figure")
    if p.counts.get('inline_handlers'):
        flags.append(f"{p.counts['inline_handlers']} inline on* handler(s): fine for a few; one delegated listener is easier to keep")
    return m, flags


def main():
    if sys.argv[1:2] in (['-h'], ['--help']):
        print(__doc__); sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit('usage: light-audit.py PAGE.html [PAGE2.html ...] [--deck] [--json] (no page given; --help for more)')
    if not Path(args[0]).exists():
        sys.exit(f'no such file: {args[0]}')
    deck, as_json = '--deck' in sys.argv, '--json' in sys.argv
    out = {}
    for a in args:
        m, flags = audit(a, deck)
        out[a] = {'measures': m, 'flags': flags}
        if as_json:
            continue
        ext = ', '.join(f'{h} {n}' for h, n in m['external'].items()) or 'none'
        print(f"\n{a}")
        print(f"  weight   {m['file_kb']} KB file, {m['script_kb']} KB script, {m['style_kb']} KB style, {m['data_uri_kb']} KB data URIs; external: {ext}")
        print(f"  libs     {', '.join(m['libraries']) or 'none'}")
        print(f"  asks     {m['folds']} folds, {m['buttons']} buttons, {m['inputs']} inputs, {m['notes']} notes, {m['keys']} key refs; {m['asks_per_1k_words']} per 1k of {m['words']} words")
        print(f"  care     print {'yes' if m['print_rules'] else 'no'}, reduced motion {'yes' if m['reduced_motion_rules'] else 'no'} ({m['motion']} motion), dark {'yes' if m['dark_mode'] else 'no'}, headings without id {len(m['headings_without_id'])}")
        for f in flags:
            print(f'  look     {f}')
        if not flags:
            print('  look     nothing flagged')
    if as_json:
        print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
