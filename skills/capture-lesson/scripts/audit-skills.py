#!/usr/bin/env python3
"""Audit a skill library: what each skill needs to trigger and to be used by anyone, and how the library has drifted.

Usage: audit-skills.py [SKILLS_DIR ...] [--personal NAME-style] [--index ~/.claude/coding-skills.md] [--inbox ~/.claude/lessons-inbox.md]
Per skill: frontmatter (name, description, when_to_use), description length, scripts it names that exist, lines phrased
as prohibitions (rewrite as positive guidelines with an example), and personal-taste markers outside the personal skill
(move them to the personal skill). Library: skills missing from the index, inbox size and harness-noise lines.
Advisory: prints a report and exits 0.
"""
import argparse, os, re, glob

# the Claude config folder this skill is installed in: <config>/skills/capture-lesson/scripts/<this file>
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def style_skill(skills_dir=os.path.join(CONFIG, 'skills')):
    """The personal style skill: $CLAUDE_STYLE_SKILL, else the one skill folder named <name>-style, else my-style."""
    name = os.environ.get('CLAUDE_STYLE_SKILL')
    if name:
        return name
    found = sorted(d for d in os.listdir(skills_dir) if d.endswith('-style')) if os.path.isdir(skills_dir) else []
    return found[0] if len(found) == 1 else 'my-style'

ap = argparse.ArgumentParser()
ap.add_argument('dirs', nargs='*', default=[os.path.join(CONFIG, 'skills')])
ap.add_argument('--personal', default=None, help='the personal style skill (default: detected, see style_skill)')
ap.add_argument('--index', default=os.path.join(CONFIG, 'coding-skills.md'))
ap.add_argument('--inbox', default=os.path.join(CONFIG, 'lessons-inbox.md'))
ap.add_argument('--lines', action='store_true', help='print every flagged line')
a = ap.parse_args()

PROHIBIT = re.compile(r"\b(don'?t|do not|never|must not|mustn'?t|avoid|forbidden|banned)\b|^\s*[-*]\s+\*{0,2}no\b|\bno (more|longer)\b", re.I)
a.personal = a.personal or style_skill(os.path.expanduser(a.dirs[0]))
owner = a.personal[:-len('-style')].capitalize() if a.personal.endswith('-style') and a.personal != 'my-style' else None
PERSONAL = re.compile(r"\b(" + (re.escape(owner) + "|" if owner else "") +
                      r"her taste|her notes|his taste|their taste|the user's (taste|style|preference)s?|my (taste|style))\b")
SCRIPT = re.compile(r"(?:\$\{CLAUDE_SKILL_DIR\}/|~/.claude/skills/([\w-]+)/|`)(scripts/[\w./-]+)")

def frontmatter(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(':')
        if v: out[k.strip()] = v.strip()
    return out, (text[m.end():] if m else text)

skills = sorted(p for d in a.dirs for p in glob.glob(os.path.join(os.path.expanduser(d), '*', 'SKILL.md')))
index = open(a.index).read() if os.path.exists(a.index) else ''
print(f'{len(skills)} skills\n')
for p in skills:
    d = os.path.dirname(p); name = os.path.basename(d); text = open(p).read(); fm, body = frontmatter(text)
    notes = []
    for k in ('name', 'description', 'when_to_use'):
        if k not in fm: notes.append(f'frontmatter has no {k}')
    if 'description' in fm and len(fm['description']) < 120: notes.append('description is short: lead with the use case and the phrases people use')
    for other, s in sorted(set(SCRIPT.findall(body))):
        home = os.path.join(os.path.dirname(d), other) if other else d          # a script of another skill is checked there
        if not os.path.exists(os.path.join(home, s.split()[0].rstrip('`.,)'))): notes.append(f'names {s} but the file is missing')
    prov = body.split('## Provenance')[0]
    neg = [l.strip() for l in prov.splitlines() if PROHIBIT.search(l)]
    if neg: notes.append(f'{len(neg)} line(s) phrased as prohibitions, e.g. "{neg[0][:90]}"' + (''.join(f'\n      > {l[:160]}' for l in neg) if a.lines else ''))
    if name != a.personal:
        pers = [l.strip() for l in prov.splitlines() if PERSONAL.search(l) and a.personal not in l and not l.startswith('Provenance')]   # pointers and provenance are fine
        if pers: notes.append(f'{len(pers)} line(s) of personal taste outside {a.personal}, e.g. "{pers[0][:90]}"' + (''.join(f'\n      > {l[:160]}' for l in pers) if a.lines else ''))
    if index and name not in index: notes.append('missing from the index')
    lines = len(text.splitlines())
    if lines > 220: notes.append(f'{lines} lines: consider splitting by task')
    print(f'{name}: ' + ('ok' if not notes else ''))
    for n in notes: print(f'  - {n}')
# repeats: the same guideline written in two skills (keep it in its owner, link from the other). Lines are compared
# only when they share rare words (an inverted index), so the cost grows with the number of real candidates, not n^2.
from collections import Counter, defaultdict
COMMON = set('when with that this from have your they them what where which while into each only also than then more '
             'over under about after before same other like just make made used using does done keep show their there '
             'should would could every first'.split())
lines_ = []
for p in skills:
    body = frontmatter(open(p).read())[1].split('## Provenance')[0]
    for l in body.splitlines():
        ws = frozenset(w for w in re.findall(r"[a-z]{4,}", l.lower()) if w not in COMMON)
        if len(ws) >= 6:
            lines_.append((os.path.basename(os.path.dirname(p)), l.strip(), ws))
df = Counter(w for _, _, ws in lines_ for w in ws)
postings = defaultdict(list)
for i, (_, _, ws) in enumerate(lines_):
    for w in ws:
        if df[w] <= 8: postings[w].append(i)
shared = Counter()
for ids in postings.values():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if lines_[ids[x]][0] != lines_[ids[y]][0]: shared[(ids[x], ids[y])] += 1
repeats = []
for (i, j), n in shared.items():
    if n >= 3:
        A, B = lines_[i][2], lines_[j][2]
        jac = len(A & B) / len(A | B)
        if jac >= 0.35: repeats.append((jac, i, j))
repeats.sort(reverse=True)
print(f'\nrepeats across skills: {len(repeats)}' + (' (same guideline in two places: keep one owner, link from the other)' if repeats else ''))
for jac, i, j in repeats[:10]:
    print(f'  - {lines_[i][0]} / {lines_[j][0]} ({jac:.0%} shared): "{lines_[i][1][:90]}"' +
          (f'\n      > {lines_[j][1][:150]}' if a.lines else ''))
if os.path.exists(a.inbox):
    inbox = open(a.inbox).read().splitlines()
    noise = [l for l in inbox if re.search(r'This session is being continued|Base directory for this skill|<task-notification>|<system-reminder>', l)]
    print(f'\ninbox: {len(inbox)} lines, {len(noise)} harness-noise lines to archive')
