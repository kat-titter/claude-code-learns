#!/usr/bin/env python3
"""Draw the README's banner and figures as SVG text files, one light and one dark copy of each.

Usage: python3 assets/draw.py          writes assets/*-light.svg and assets/*-dark.svg
Each colour has one meaning, in every figure and on index.html: orange is Claude, blue is code (a check a program can
fail), green is what it keeps, ink is you, grey pages are files. Exits 1 if any text colour falls under WCAG AA (4.5:1)
on the fill it sits on.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "'IBM Plex Mono',ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "Archivo,-apple-system,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

THEMES = {
    'light': dict(bg='#faf9f5', hair='#e8e6dc', mark='#c96442', ink='#141413', muted='#5e5d59', edge='#8f8d86',
                  claude=('#d97757', '#f8e6dd', '#a8492a'), code=('#6a9bcc', '#e6eef7', '#2f5f8c'),
                  keep=('#788c5d', '#ebeee2', '#4a5c33'), file=('#b0aea5', '#f0eee6', '#141413')),
    'dark': dict(bg='#1f1e1d', hair='#3d3d3a', mark='#d97757', ink='#faf9f5', muted='#b0aea5', edge='#8f8d86',
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
        """Each kind drawn as in the figure, then its meaning; wraps to a new row at the figure's edge."""
        x = 24
        for kind, s in items:
            if x > 24 and x + 21 + len(s) * 6.6 > self.w - 16:
                x, y = 24, y + 24
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


# the banner's character: Claude (orange) holding a page with one kept line (green); E is an eye, L the line
CHARACTER = """\
..ooooo......
.ooooooo.ggg.
.oEoooEo.gggg
.ooooooo.gggg
ooooooooogLLg
.ooooooo.gggg
..o...o..gggg
..o...o......"""


def banner(t):
    """The thesis, and Claude keeping one line of it."""
    s = Svg(1280, 300, t, 'claude-code-learns: Learns in one turn. Keeps it for good.')
    s.text(72, 136, 'Learns in one turn.', 76, t['ink'], MONO, 500, spacing=-1.5)
    s.text(72, 230, 'Keeps it for good.', 76, t['claude'][2], MONO, 500, spacing=-1.5)
    CHECK.append((t['claude'][2], t['bg']))
    cell, x0, y0 = 18, 1000, 78
    s.add('<g shape-rendering="crispEdges">')
    paint = {'o': t['mark'], 'E': '#141413', 'g': t['keep'][0], 'L': t['bg']}
    for r, row in enumerate(CHARACTER.splitlines()):
        for c, ch in enumerate(row):
            if ch in paint:
                s.add(f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{cell}" height="{cell}" fill="{paint[ch]}"/>')
    s.add('</g>')
    s.save(f'banner-{name_of(t)}.svg')


def mark_inline(cell=9):
    """The banner's character for index.html, coloured by the page's own tokens so it follows its theme."""
    paint = {'o': 'var(--mark)', 'E': '#141413', 'g': 'var(--keep)', 'L': 'var(--bg)'}
    rows = CHARACTER.splitlines()
    w, h = len(rows[0]) * cell, len(rows) * cell
    cells = ''.join(f'<rect x="{c * cell}" y="{r * cell}" width="{cell}" height="{cell}" fill="{paint[ch]}"/>'
                    for r, row in enumerate(rows) for c, ch in enumerate(row) if ch in paint)
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" shape-rendering="crispEdges" role="img" '
            f'aria-label="Claude keeping one line">{cells}</svg>')

HOOKS = [('feedback-nudge.py', 1), ('skill-router.py', 1), ('prompt-nudge.py', 1), ('scan-corrections.py', 1),
         ('skill-usage-log.py', 1), ('add a line or log, never block', 0)]   # the first three add a line, the last two log


def how_it_works(t):
    s = Svg(740, 850, t, 'How it works: every turn, your correction becomes a one-line lesson; every week, scripts '
            'read the notebook and outside posts, a weekly agent drafts at most five proposals, and the ones that '
            'need you come back to you, one yes per lane.')
    M, R, W = 175, 495, 220
    s.band(M, 40, 'every turn')
    s.human(60, 52)
    s.node(M, 56, W, 146, 'code', 'hooks', HOOKS)
    s.node(R, 56, W, 72, 'claude', 'Claude', [('in your session', 0)])
    s.edge([(94, 92), (M - 3, 92)]); s.label(134, 84, ['a correction'], 'middle')
    s.edge([(M + W, 82), (R - 3, 82)]); s.label(445, 74, ['a reminder,'], 'middle'); s.label(445, 101, ['likely skill'], 'middle')
    s.node(M, 270, W, 64, 'file', None, [('lessons-inbox.md', 1), ('skill-usage.log', 1)])
    s.edge([(285, 202), (285, 267)]); s.label(295, 240, ['a quoted line, a skill used'])
    s.node(R, 270, W, 88, 'keep', 'your library', [('skills, e.g. workflow-design', 0), ('your style skill', 0),
                                                    ('project memory', 0)])
    s.edge([(560, 128), (560, 267)]); s.label(552, 200, ['one-line lesson'], 'end')
    s.edge([(650, 270), (650, 131)]); s.label(658, 200, ['skill text,', 'on a match'])
    s.add(f'<path d="M24 392H716" stroke="{t["hair"]}" stroke-width="1"/>')
    s.band(M, 420, 'every week')
    s.edge([(285, 334), (285, 433)]); s.label(295, 370, ["the week's lines"])
    s.node(M, 436, W, 92, 'code', 'weekly scripts', [('skills-watch.py', 1), ('trigger-misses.py', 1),
                                                       ('practice-watch.py', 1)])
    s.node(R, 474, W, 92, 'file', 'outside, read as data', [('new upstream skills', 0), ('X links you pasted', 0),
                                                              ('practice-accounts.txt', 1)])
    s.edge([(R, 512), (M + W + 3, 512)]); s.label(445, 504, ['new skills,'], 'middle'); s.label(445, 530, ['new posts'], 'middle')
    s.edge([(R + 40, 358), (R + 40, 414), (440, 414), (440, 454), (M + W + 3, 454)])
    s.label(R + 48, 414, ["last week's", 'text: landed?'])
    s.node(M, 594, W, 64, 'claude', 'weekly agent', [('weekly-watch.md', 1)])
    s.edge([(285, 528), (285, 591)]); s.label(295, 566, ['one report'])
    s.node(M, 714, W, 92, 'file', 'proposals, by undo cost', [('open: a wording line', 0), ('evidence: after its test', 0),
                                                               ('closed: hooks, installs', 0)])
    s.edge([(285, 658), (285, 711)]); s.label(295, 690, ['at most five drafts'])
    s.edge([(M + W, 755), (726, 755), (726, 314), (R + W + 3, 314)], dashed=True)
    s.label(716, 714, ['open lane, and evidence', 'on a pass, if you opt in'], 'end')
    s.edge([(M, 778), (60, 778), (60, 133)])
    s.label(70, 634, ['your yes,', 'one per lane'])
    s.key(826, KEY)
    s.save(f'how-it-works-{name_of(t)}.svg')


def how_it_works_phone(t):
    """The same graph in one column for a phone: the spine top to bottom, one rail each side."""
    s = Svg(320, 1386, t, 'How it works, phone layout: every turn, your correction reaches a hook, Claude writes a '
            'one-line lesson into your library; every week, scripts read the logs and outside posts, a weekly agent '
            'drafts at most five proposals, and they come back to you, one yes per lane.')
    X, W, A = 44, 246, 80
    s.band(X, 30, 'every turn')
    s.human(A, 44)
    s.edge([(A, 124), (A, 149)]); s.label(92, 141, ['a correction'])
    s.node(X, 152, W, 146, 'code', 'hooks', HOOKS)
    s.edge([(A, 298), (A, 335)]); s.label(92, 321, ['a reminder, the likely skill'])
    s.node(X, 338, W, 52, 'claude', 'Claude', [('in your session', 0)])
    s.edge([(A, 390), (A, 435)]); s.label(92, 418, ['a one-line lesson'])
    s.edge([(210, 438), (210, 393)]); s.label(218, 410, ['skill text,', 'on a match'])
    s.node(X, 438, W, 88, 'keep', 'your library', [('skills, e.g. workflow-design', 0), ('your style skill', 0),
                                                   ('project memory', 0)])
    s.add(f'<path d="M16 550H304" stroke="{t["hair"]}" stroke-width="1"/>')
    s.band(X, 574, 'every week')
    s.node(X, 586, W, 92, 'file', 'outside, read as data', [('new upstream skills', 0), ('X links you pasted', 0),
                                                            ('practice-accounts.txt', 1)])
    s.label(X, 704, ['new skills, new posts'])
    s.edge([(X + W, 188), (304, 188), (304, 766), (X + W + 3, 766)]); s.label(296, 724, ['a quoted line, a skill used'], 'end')
    s.node(X, 734, W, 64, 'file', None, [('lessons-inbox.md', 1), ('skill-usage.log', 1)])
    s.edge([(A, 798), (A, 843)]); s.label(92, 826, ["the week's lines"])
    s.node(X, 846, W, 118, 'code', 'weekly scripts', [('skills-watch.py', 1), ('trigger-misses.py', 1),
                                                       ('practice-watch.py', 1), ("did last week's text land?", 0)])
    s.edge([(X, 632), (30, 632), (30, 874), (X - 3, 874)])
    s.edge([(A, 964), (A, 1009)]); s.label(92, 992, ['one report'])
    s.node(X, 1012, W, 64, 'claude', 'weekly agent', [('weekly-watch.md', 1)])
    s.edge([(A, 1076), (A, 1121)]); s.label(92, 1104, ['at most five drafts'])
    s.node(X, 1124, W, 104, 'file', 'proposals, by undo cost', [('open: applies itself, opt-in', 0),
                                                                 ('evidence: on a pass, opt-in', 0), ('closed: hooks, installs', 0)])
    s.edge([(100, 1228), (100, 1250), (14, 1250), (14, 84), (55, 84)])
    s.label(X, 1272, ['back to you: one yes per lane'])
    s.key(1310, KEY)
    s.save(f'how-it-works-phone-{name_of(t)}.svg')


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


def check_repair_phone(t):
    """The same loop in one column for a phone; the pass branch takes the right rail."""
    s = Svg(320, 672, t, 'check-repair.js, phone layout: an agent builds each unit, a check reads its exit code, a '
            'failing unit is repaired alone up to three rounds, a unit still failing comes to you, and a repair that '
            'passes becomes a candidate rule.')
    X, W, A = 40, 240, 80
    s.band(X, 34, 'each unit, in parallel')
    s.node(X, 52, W, 64, 'claude', 'agent builds', [('one unit, its files', 0)], stack=2)
    s.edge([(A, 128), (A, 167)]); s.label(92, 152, ['files changed'])
    s.node(X, 170, W, 64, 'code', 'check', [('the exit code', 0)])
    s.edge([(A, 234), (A, 287)]); s.label(92, 256, ['exit code,', 'last 40 lines'])
    s.edge([(200, 290), (200, 237)]); s.label(208, 256, ['a fix, up to', 'three rounds'])
    s.node(X, 290, W, 64, 'claude', 'agent repairs', [('that unit only', 0)])
    s.edge([(A, 354), (A, 393)]); s.label(92, 378, ['still failing: what was tried'])
    s.human(A, 396)
    s.edge([(X + W, 202), (300, 202), (300, 532), (X + W + 3, 532)])
    s.label(292, 492, ['exit 0, after a fix'], 'end')
    s.node(X, 500, W, 64, 'keep', 'candidate rule', [('for the next split', 0)])
    s.key(600, [k for k in KEY if k[0] != 'file'])
    s.save(f'check-repair-phone-{name_of(t)}.svg')


MIND_TITLE = ('Memory and cognition: short-term memory is the session and the inbox; long-term memory is skills, '
              'project memory and CLAUDE.md, sorted in weekly; cognition about you is your style skill and the feedback '
              'hook; cognition about itself is the miss report, the watcher and the audit.')
MIND = [  # (band, title, gloss, chips): one cell each
    ('memory', 'short-term', 'this session; fast, small', [
        ('claude', "the session's context"), ('file', 'lessons-inbox.md, a quick notebook'), ('file', 'skill-usage.log')]),
    ('memory', 'long-term', 'every later session; slow, general', [
        ('keep', 'skills: how to do the work'), ('keep', "project memory: one project's facts"),
        ('keep', 'CLAUDE.md: read every session')]),
    ('cognition', 'about you', 'relational: who it works with', [
        ('keep', 'your style skill: your taste'), ('code', 'feedback-nudge.py: hears a correction'),
        ('claude', 'routes it: your taste, or for all?'), ('keep', 'memory notes about you')]),
    ('cognition', 'about itself', 'meta: is its own learning working?', [
        ('code', 'trigger-misses.py: loaded when it fit?'), ('code', "skills-watch.py: did last week's land?"),
        ('code', 'audit-skills.py: too long, repeated'), ('claude', 'asks which family a mistake is in')]),
]


def mind_cell(s, x, y, w, cell):
    _, title, gloss, chips = cell
    t = s.t
    h = 66 + 24 * len(chips)
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{t["hair"]}" stroke-width="1.4"/>')
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
    return h


def mind(t):
    """Memory, short and long, and cognition, about you and about itself: which files play each part."""
    s = Svg(740, 476, t, MIND_TITLE)
    cw, gap = 316, 60
    xs = (24, 24 + cw + gap)
    s.band(24, 36, 'memory')
    mind_cell(s, xs[0], 52, cw, MIND[0]); mind_cell(s, xs[1], 52, cw, MIND[1])
    s.edge([(xs[0] + cw + 6, 125), (xs[1] - 6, 125)])
    s.label(370, 117, ['sorted'], 'middle'); s.label(370, 144, ['weekly'], 'middle')
    s.band(24, 236, 'cognition')
    mind_cell(s, xs[0], 252, cw, MIND[2]); mind_cell(s, xs[1], 252, cw, MIND[3])
    s.key(456, KEY)
    s.save(f'mind-{name_of(t)}.svg')


def mind_phone(t):
    """The same four cells in one column for a phone."""
    s = Svg(320, 880, t, MIND_TITLE)
    x, w, y = 16, 288, 52
    s.band(x, 36, 'memory')
    y += mind_cell(s, x, y, w, MIND[0])
    s.edge([(80, y + 4), (80, y + 41)]); s.label(92, y + 28, ['sorted weekly'])
    y += 44
    y += mind_cell(s, x, y, w, MIND[1]) + 40
    s.band(x, y, 'cognition')
    y += 16
    y += mind_cell(s, x, y, w, MIND[2]) + 16
    y += mind_cell(s, x, y, w, MIND[3]) + 36
    s.key(y, KEY)
    s.save(f'mind-phone-{name_of(t)}.svg')
    return y


def name_of(t):
    return next(k for k, v in THEMES.items() if v is t)


if __name__ == '__main__':
    for t in THEMES.values():
        banner(t)
        how_it_works(t)
        how_it_works_phone(t)
        check_repair(t)
        check_repair_phone(t)
        mind(t)
        mind_phone(t)
    page = os.path.join(HERE, '..', 'index.html')
    if os.path.exists(page):   # the page's copy of the character, between its <!--mark--> markers
        html = open(page).read()
        a, b = html.find('<!--mark-->'), html.find('<!--/mark-->')
        if a >= 0 and b > a:
            open(page, 'w').write(html[:a + 11] + mark_inline() + html[b:])
    bad = sorted({(a, b, round(contrast(a, b), 2)) for a, b in CHECK if contrast(a, b) < 4.5})
    for a, b, c in bad:
        print(f'text {a} on {b}: {c}:1, under 4.5')
    print(f'{len(set(CHECK))} text/fill pairs checked, {len(bad)} under AA')
    sys.exit(1 if bad else 0)
