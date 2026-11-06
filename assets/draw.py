#!/usr/bin/env python3
"""Draw the README's banner and figures as SVG text files, one light and one dark copy of each.

Usage: python3 assets/draw.py          writes assets/*-light.svg and assets/*-dark.svg
Each colour has one meaning, in every figure and on index.html: orange is Claude, blue is code (a check a program can
fail), green is what it keeps, ink is you, grey pages are files. Exits 1 if any text colour falls under WCAG AA (4.5:1)
on the fill it sits on.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "'IBM Plex Mono',ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "Archivo,-apple-system,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

THEMES = {
    'light': dict(bg='#faf9f5', hair='#e8e6dc', ink='#141413', muted='#5e5d59', edge='#8f8d86',
                  claude=('#d97757', '#f8e6dd', '#a8492a'), code=('#6a9bcc', '#e6eef7', '#2f5f8c'),
                  keep=('#788c5d', '#ebeee2', '#4a5c33'), file=('#b0aea5', '#f0eee6', '#141413')),
    'dark': dict(bg='#1f1e1d', hair='#3d3d3a', ink='#faf9f5', muted='#b0aea5', edge='#8f8d86',
                 claude=('#d97757', '#3b2922', '#f0a284'), code=('#6a9bcc', '#212d3a', '#9cc0e6'),
                 keep=('#788c5d', '#282e22', '#b3c59a'), file=('#6b6a65', '#2a2927', '#faf9f5')),
}


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Svg:
    def __init__(self, w, h, t, title):
        self.w, self.h, self.t, self.out = w, h, t, []
        self.head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                     f'role="img" aria-label="{esc(title)}">\n<title>{esc(title)}</title>\n'
                     f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                     f'orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="{t["edge"]}" '
                     f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>\n'
                     f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{t["bg"]}" '
                     f'stroke="{t["hair"]}"/>\n')

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, size=13, fill=None, font=SANS, weight=400, anchor='start', spacing=0):
        ls = f' letter-spacing="{spacing}"' if spacing else ''
        self.add(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{fill or self.t["ink"]}" text-anchor="{anchor}"{ls}>{esc(s)}</text>')

    def node(self, x, y, w, h, kind, title, lines=(), stack=0):
        """A box for code, Claude or what it keeps; a page with a folded corner for a file. lines: (text, is_mono)."""
        stroke, fill, ink = self.t[kind]
        for k in range(stack, 0, -1):   # cards behind: the same step, run once per unit
            self.add(f'<rect x="{x + 6 * k}" y="{y + 6 * k}" width="{w}" height="{h}" rx="10" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="1.2" opacity="{1 - 0.3 * k}"/>')
        if kind == 'file':
            f = 14
            self.add(f'<path d="M{x + 8} {y}H{x + w - f}L{x + w} {y + f}V{y + h - 8}Q{x + w} {y + h} {x + w - 8} '
                     f'{y + h}H{x + 8}Q{x} {y + h} {x} {y + h - 8}V{y + 8}Q{x} {y} {x + 8} {y}Z" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="1.4"/><path d="M{x + w - f} {y}V{y + f}H{x + w}" fill="none" '
                     f'stroke="{stroke}" stroke-width="1.4"/>')
        else:
            self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" '
                     f'stroke-width="1.6"/>')
        cy = y + 23
        if title:
            self.text(x + 14, cy, title, 15, ink, SANS, 600)
            cy += 20
        for s, mono in lines:
            self.text(x + 14, cy, s, 12.5 if mono else 13, self.t['ink'], MONO if mono else SANS)
            cy += 18
        CHECK.append((ink, fill))
        CHECK.append((self.t['ink'], fill))

    def human(self, cx, top, label='you', scale=1.0):
        """You: a person, drawn, not a box."""
        r, s = 11 * scale, scale
        self.add(f'<circle cx="{cx}" cy="{top + r}" r="{r}" fill="{self.t["ink"]}"/>')
        y0 = top + 2 * r + 5 * s
        self.add(f'<path d="M{cx - 22 * s} {y0 + 26 * s}C{cx - 22 * s} {y0 + 4 * s} {cx - 12 * s} {y0} {cx} {y0}'
                 f'C{cx + 12 * s} {y0} {cx + 22 * s} {y0 + 4 * s} {cx + 22 * s} {y0 + 26 * s}Z" fill="{self.t["ink"]}"/>')
        if label:
            self.text(cx, y0 + 26 * s + 20, label, 15, self.t['ink'], SANS, 600, 'middle')

    def edge(self, pts, dashed=False):
        d = 'M' + 'L'.join(f'{x} {y}' for x, y in pts)
        da = ' stroke-dasharray="5 4"' if dashed else ''
        self.add(f'<path d="{d}" fill="none" stroke="{self.t["edge"]}" stroke-width="1.6" stroke-linejoin="round"'
                 f'{da} marker-end="url(#a)"/>')

    def label(self, x, y, lines, anchor='start'):
        for i, s in enumerate(lines):
            self.text(x, y + 15 * i, s, 12.5, self.t['muted'], SANS, 400, anchor)
        CHECK.append((self.t['muted'], self.t['bg']))

    def band(self, x, y, s):
        self.text(x, y, s.upper(), 11.5, self.t['muted'], MONO, 500, spacing=1.2)

    def key(self, y, items):
        """One row: each kind drawn as in the figure, then its meaning."""
        x = 24
        for kind, s in items:
            if kind == 'you':
                self.add(f'<circle cx="{x + 7}" cy="{y - 9}" r="4" fill="{self.t["ink"]}"/><path d="M{x} {y + 2}C{x} {y - 4} '
                         f'{x + 14} {y - 4} {x + 14} {y + 2}Z" fill="{self.t["ink"]}"/>')
            elif kind == 'file':
                st, fi, _ = self.t['file']
                self.add(f'<path d="M{x} {y - 12}H{x + 9}L{x + 14} {y - 7}V{y + 2}H{x}Z" fill="{fi}" stroke="{st}" '
                         f'stroke-width="1.3"/>')
            else:
                st, fi, _ = self.t[kind]
                self.add(f'<rect x="{x}" y="{y - 12}" width="14" height="14" rx="3" fill="{fi}" stroke="{st}" '
                         f'stroke-width="1.5"/>')
            self.text(x + 21, y, s, 12.5, self.t['muted'])
            x += 21 + int(len(s) * 6.6) + 22

    def save(self, name):
        with open(os.path.join(HERE, name), 'w') as f:
            f.write(self.head + '\n'.join(self.out) + '\n</svg>\n')


CHECK = []
KEY = [('you', 'you'), ('code', 'code: a check a program can fail'), ('claude', 'Claude'),
       ('keep', 'what it keeps'), ('file', 'a file')]


def banner(t):
    s = Svg(1280, 320, t, 'claude-code-learns: Correct it once. It remembers.')
    s.text(72, 92, 'claude-code-learns', 26, t['muted'], MONO, 500)
    s.text(72, 178, 'Correct it once.', 62, t['ink'], MONO, 500, spacing=-1)
    s.text(72, 254, 'It remembers.', 62, t['claude'][2], MONO, 500, spacing=-1)
    CHECK.append((t['claude'][2], t['bg']))
    # the mark: one correction from you spirals into a lesson it keeps
    cx, cy, turns, r0, r1 = 1078, 166, 2.6, 16, 112
    pts = []
    for i in range(0, 241):
        f = i / 240
        a = -math.pi / 2 + f * turns * 2 * math.pi
        r = r1 - (r1 - r0) * f
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    s.add(f'<path d="{d}" fill="none" stroke="{t["claude"][0]}" stroke-width="6" stroke-linecap="round" '
          f'stroke-linejoin="round"/>')
    s.add(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="11" fill="{t["keep"][0]}"/>')
    s.human(cx - 70, 22, label=None, scale=0.82)   # you, where the line starts
    s.save(f'banner-{name_of(t)}.svg')


def how_it_works(t):
    s = Svg(740, 776, t, 'How it works: every turn, your correction becomes a one-line lesson; every week, scripts '
            'read the notebook and outside posts, a weekly agent drafts at most five proposals, and the ones that '
            'need you come back to you, one yes per lane.')
    M, R, W = 175, 495, 220
    s.band(M, 40, 'every turn')
    s.human(60, 52)
    s.node(M, 56, W, 72, 'code', 'hooks', [('feedback-nudge.py + 4 more', 1), ('add a line or log, never block', 0)])
    s.node(R, 56, W, 72, 'claude', 'Claude', [('in your session', 0)])
    s.edge([(94, 92), (M - 3, 92)]); s.label(134, 84, ['a correction'], 'middle')
    s.edge([(M + W, 82), (R - 3, 82)]); s.label(445, 74, ['a reminder,'], 'middle'); s.label(445, 101, ['likely skill'], 'middle')
    s.node(M, 196, W, 64, 'file', None, [('lessons-inbox.md', 1), ('skill-usage.log', 1)])
    s.edge([(285, 128), (285, 193)]); s.label(295, 172, ['a quoted line, a skill used'])
    s.node(R, 196, W, 88, 'keep', 'your library', [('skills, e.g. workflow-design', 0), ('your style skill', 0),
                                                    ('project memory', 0)])
    s.edge([(560, 128), (560, 193)]); s.label(552, 156, ['one-line lesson'], 'end')
    s.edge([(650, 196), (650, 131)]); s.label(658, 156, ['skill text,', 'on a match'])
    s.add(f'<path d="M24 318H716" stroke="{t["hair"]}" stroke-width="1"/>')
    s.band(M, 346, 'every week')
    s.edge([(285, 260), (285, 359)]); s.label(295, 296, ["the week's lines"])
    s.node(M, 362, W, 92, 'code', 'weekly scripts', [('skills-watch.py', 1), ('trigger-misses.py', 1),
                                                       ('practice-watch.py', 1)])
    s.node(R, 400, W, 92, 'file', 'outside, read as data', [('new upstream skills', 0), ('X links you pasted', 0),
                                                              ('practice-accounts.txt', 1)])
    s.edge([(R, 446), (M + W + 3, 446)]); s.label(445, 438, ['new skills,'], 'middle'); s.label(445, 464, ['new posts'], 'middle')
    s.edge([(R + 40, 284), (R + 40, 340), (440, 340), (440, 380), (M + W + 3, 380)])
    s.label(R + 48, 340, ["last week's", 'text: landed?'])
    s.node(M, 520, W, 64, 'claude', 'weekly agent', [('weekly-watch.md', 1)])
    s.edge([(285, 454), (285, 517)]); s.label(295, 492, ['one report'])
    s.node(M, 640, W, 92, 'file', 'proposals, by undo cost', [('open: a wording line', 0), ('evidence: after its test', 0),
                                                               ('closed: hooks, installs', 0)])
    s.edge([(285, 584), (285, 637)]); s.label(295, 616, ['at most five drafts'])
    s.edge([(M + W, 681), (726, 681), (726, 240), (R + W + 3, 240)], dashed=True)
    s.label(716, 640, ['open lane applies', 'itself, if you opt in'], 'end')
    s.edge([(M, 704), (60, 704), (60, 133)])
    s.label(70, 560, ['your yes,', 'one per lane'])
    s.key(752, KEY)
    s.save(f'how-it-works-{name_of(t)}.svg')


def check_repair(t):
    s = Svg(740, 330, t, 'check-repair.js: each unit is built by an agent and checked by its exit code; a failing unit '
            'is repaired alone, up to three rounds; a repair that passes becomes a candidate rule, and a unit still '
            'failing comes to you.')
    s.band(24, 40, 'each unit, in parallel')
    s.node(24, 64, 178, 64, 'claude', 'agent builds', [('one unit, its files', 0)], stack=2)
    s.node(304, 64, 172, 64, 'code', 'check', [('the exit code', 0)])
    s.node(556, 64, 160, 64, 'keep', 'candidate rule', [('for the next split', 0)])
    s.edge([(216, 96), (301, 96)]); s.label(259, 88, ['files changed'], 'middle')
    s.edge([(476, 96), (553, 96)]); s.label(515, 88, ['exit 0'], 'middle'); s.label(515, 115, ['after a fix'], 'middle')
    s.node(304, 196, 172, 64, 'claude', 'agent repairs', [('that unit only', 0)])
    s.edge([(350, 128), (350, 193)]); s.label(342, 156, ['exit code,', 'last 40 lines'], 'end')
    s.edge([(430, 196), (430, 131)]); s.label(438, 156, ['a fix, up to', 'three rounds'])
    s.human(640, 182)
    s.edge([(476, 228), (610, 228)]); s.label(543, 220, ['still failing:'], 'middle'); s.label(543, 247, ['what was tried'], 'middle')
    s.key(306, [k for k in KEY if k[0] != 'file'])
    s.save(f'check-repair-{name_of(t)}.svg')


def mind(t):
    """Memory, short and long, and cognition, about you and about itself: which files play each part."""
    s = Svg(740, 476, t, 'Memory and cognition: short-term memory is the session and the inbox; long-term memory is '
            'skills, project memory and CLAUDE.md, sorted in weekly; cognition about you is your style skill and the '
            'feedback hook; cognition about itself is the miss report, the watcher and the audit.')
    cw, gap = 316, 60
    xs = (24, 24 + cw + gap)

    def cell(x, y, h, title, gloss, chips):
        s.add(f'<rect x="{x}" y="{y}" width="{cw}" height="{h}" rx="12" fill="none" stroke="{t["hair"]}" '
              f'stroke-width="1.4"/>')
        s.text(x + 16, y + 26, title, 15, t['ink'], SANS, 600)
        s.text(x + 16, y + 46, gloss, 13, t['muted'])
        for i, (kind, label) in enumerate(chips):
            cy = y + 76 + 24 * i
            st, fi, _ = t[kind]
            if kind == 'file':
                s.add(f'<path d="M{x + 16} {cy - 12}H{x + 25}L{x + 30} {cy - 7}V{cy + 2}H{x + 16}Z" fill="{fi}" '
                      f'stroke="{st}" stroke-width="1.3"/>')
            else:
                s.add(f'<rect x="{x + 16}" y="{cy - 12}" width="14" height="14" rx="3" fill="{fi}" stroke="{st}" '
                      f'stroke-width="1.5"/>')
            s.text(x + 38, cy, label, 13, t['ink'])
        CHECK.append((t['muted'], t['bg']))

    s.band(24, 36, 'memory')
    cell(xs[0], 52, 146, 'short-term', 'this session; fast, small', [
        ('claude', "the session's context"), ('file', 'lessons-inbox.md, a quick notebook'),
        ('file', 'skill-usage.log')])
    cell(xs[1], 52, 146, 'long-term', 'every later session; slow, general', [
        ('keep', 'skills: how to do the work'), ('keep', "project memory: one project's facts"),
        ('keep', 'CLAUDE.md: read every session')])
    s.edge([(xs[0] + cw + 6, 125), (xs[1] - 6, 125)])
    s.label(370, 117, ['sorted'], 'middle'); s.label(370, 144, ['weekly'], 'middle')
    s.band(24, 236, 'cognition')
    cell(xs[0], 252, 170, 'about you', 'relational: who it works with', [
        ('keep', 'your style skill: your taste'), ('code', 'feedback-nudge.py: hears a correction'),
        ('claude', 'routes it: your taste, or for all?'), ('keep', 'memory notes about you')])
    cell(xs[1], 252, 170, 'about itself', 'meta: is its own learning working?', [
        ('code', 'trigger-misses.py: loaded when it fit?'), ('code', "skills-watch.py: did last week's land?"),
        ('code', 'audit-skills.py: too long, repeated'), ('claude', 'asks which family a mistake is in')])
    s.key(456, KEY)
    s.save(f'mind-{name_of(t)}.svg')


def name_of(t):
    return next(k for k, v in THEMES.items() if v is t)


if __name__ == '__main__':
    for t in THEMES.values():
        banner(t)
        how_it_works(t)
        check_repair(t)
        mind(t)
    bad = sorted({(a, b, round(contrast(a, b), 2)) for a, b in CHECK if contrast(a, b) < 4.5})
    for a, b, c in bad:
        print(f'text {a} on {b}: {c}:1, under 4.5')
    print(f'{len(set(CHECK))} text/fill pairs checked, {len(bad)} under AA')
    sys.exit(1 if bad else 0)
