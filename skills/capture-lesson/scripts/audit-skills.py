#!/usr/bin/env python3
"""Audit a skill library: what each skill needs to trigger and to be used by anyone, and how the library has drifted.

Usage: audit-skills.py [SKILLS_DIR ...] [--personal NAME-style] [--index ~/.claude/coding-skills.md] [--inbox ~/.claude/lessons-inbox.md]
Per skill, against the rubric in SKILL.md 6b: frontmatter that parses, with a name that matches the folder (lowercase
and hyphens, 64 characters at most, no "claude" or "anthropic"); a description under 1,024 characters and, with
when_to_use, under 1,536 (about 600 is the aim); a body under 500 lines with a `## Gotchas` list in its first 40 lines;
scripts it names that exist; lines phrased as prohibitions (rewrite as positive guidelines with an example); and
personal-taste markers outside the personal skill (move them to the personal skill).
Library: two descriptions that would fire on the same prompt, the same guideline in two skills, skills missing from the
index, inbox size and harness-noise lines.
Advisory: prints a report and exits 0; exits 1 only when there is nothing to audit.
"""
import argparse, glob, importlib.util, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import HARNESS, SKILLS, read_frontmatter, style_skill

# advice phrased as a prohibition: an imperative at the start of a bullet or sentence, or "must not" anywhere
PROHIBIT = re.compile(r"(?:^\s*(?:[-*]|\d+\.)?\s*|[.!?;:]\s+)(?:\*\*)?(?:don'?t|do not|never|avoid)\b|"
                      r"^\s*[-*]\s+(?:\*\*)?no\b|\bmust not\b|\bmustn'?t\b", re.I)
SCRIPT = re.compile(r"(?:\$\{CLAUDE_SKILL_DIR\}/|~/.claude/skills/([\w-]+)/|`)(scripts/[\w./-]+)")
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
FRONT = re.compile(r'^---\n.*?\n---\n', re.S)
COMMON = set('when with that this from have your they them what where which while into each only also than then more '
             'over under about after before same other like just make made used using does done keep show their there '
             'should would could every first'.split())
# words every description uses ("use when someone asks ..."), left out when comparing two descriptions
TRIGGER_WORDS = COMMON | set('asks says someone says user users skill skills whenever anything something before after '
                             'work help need needs want wants request'.split())


def text_of(v):
    """A frontmatter value as text: block and plain strings as they are, nothing for a missing value."""
    return v if isinstance(v, str) else '' if v is None else str(v)


def is_index_entry(name, index):
    """The skill is named in the index as a whole token or in backticks, not inside another word."""
    return bool(re.search(rf'`{re.escape(name)}`|(?<![\w-]){re.escape(name)}(?![\w-])', index))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dirs', nargs='*', default=[SKILLS], help='skills folders to audit (default: %(default)s)')
    ap.add_argument('--personal', default=None, help='the personal style skill, e.g. jo-style (default: detected)')
    ap.add_argument('--index', default=os.path.join(os.path.dirname(SKILLS), 'coding-skills.md'),
                    help='a file that lists every skill (default: %(default)s)')
    ap.add_argument('--inbox', default=os.path.join(os.path.dirname(SKILLS), 'lessons-inbox.md'),
                    help='the lessons inbox (default: %(default)s)')
    ap.add_argument('--lines', action='store_true', help='print every flagged line')
    a = ap.parse_args()

    dirs = [os.path.expanduser(d) for d in a.dirs]
    for d in dirs:
        if not os.path.isdir(d):
            sys.exit(f'no skills folder at {d}')
    skills = sorted(p for d in dirs for p in glob.glob(os.path.join(d, '*', 'SKILL.md')))
    if not skills:
        sys.exit(f"no <skill>/SKILL.md found in {', '.join(dirs)}")

    personal = a.personal or style_skill(dirs[0])
    # siblings share the prefix (jo-style, jo-visual-house-style); a name without -style is its own prefix
    prefix = personal[:-len('style')] if personal.endswith('-style') else personal + '-'
    owner = prefix.strip('-').capitalize() if prefix != 'my-' else None
    PERSONAL = re.compile(r"\b(" + (re.escape(owner) + "|" if owner else "") +
                          r"her taste|her notes|his taste|their taste|the user's (taste|style|preference)s?|my (taste|style))\b")

    print(f'{len(skills)} skills; style skill {personal}')
    if not importlib.util.find_spec('yaml'):
        print('PyYAML is not installed, so frontmatter is read line by line: block-style values and parse errors are '
              'missed (pip install pyyaml)')
    index = open(a.index, encoding='utf-8', errors='replace').read() if os.path.exists(a.index) else ''
    if not index:
        print(f'no index at {a.index}: index check skipped')
    print()

    bodies, triggers = {}, {}
    for p in skills:
        d = os.path.dirname(p); name = os.path.basename(d)
        text = open(p, encoding='utf-8', errors='replace').read()
        m = FRONT.match(text)
        body = text[m.end():] if m else text
        try:
            fm, err = read_frontmatter(p)
        except ValueError as e:                     # a file that is not UTF-8
            fm, err = {}, f'unreadable as UTF-8 ({e.reason}): the skill loads with no description'
        notes = [err] if err else []
        if not err:
            for k in ('name', 'description', 'when_to_use'):
                if k not in fm: notes.append(f'frontmatter has no {k}')
        fname, desc, when = text_of(fm.get('name')), text_of(fm.get('description')), text_of(fm.get('when_to_use'))
        if fname and fname != name: notes.append(f'name "{fname}" does not match the folder {name}')
        if fname and (not NAME.match(fname) or len(fname) > 64):
            notes.append(f'name "{fname}" is not lowercase-hyphen, 64 characters at most')
        if re.search(r'claude|anthropic', fname, re.I): notes.append(f'name "{fname}" contains a reserved word (claude, anthropic)')
        if desc and len(desc) < 120: notes.append('description is short: lead with the use case and the phrases people use')
        if len(desc) > 1024: notes.append(f'description is {len(desc)} characters: the limit is 1,024')
        both = len(desc) + len(when)
        if both > 1536: notes.append(f'description + when_to_use is {both} characters: the shared limit is 1,536')
        elif both > 600: notes.append(f'description + when_to_use is {both} characters: aim for about 600')
        for other, s in sorted(set(SCRIPT.findall(body))):
            home = os.path.join(os.path.dirname(d), other) if other else d          # a script of another skill is checked there
            if not os.path.exists(os.path.join(home, s.split()[0].rstrip('`.,)'))): notes.append(f'names {s} but the file is missing')
        prov = body.split('## Provenance')[0]
        neg = [l.strip() for l in prov.splitlines() if PROHIBIT.search(re.sub(r'"[^"]*"|“[^”]*”|`[^`]*`', '', l))]  # quotes and code are provenance, not advice
        if neg: notes.append(f'{len(neg)} line(s) phrased as prohibitions, e.g. "{neg[0][:90]}"' + (''.join(f'\n      > {l[:160]}' for l in neg) if a.lines else ''))
        if name != personal and not name.startswith(prefix):   # the person's sibling skills are personal too
            pers = [l.strip() for l in prov.splitlines() if PERSONAL.search(l) and personal not in l and not l.startswith('Provenance')]   # pointers and provenance are fine
            if pers: notes.append(f'{len(pers)} line(s) of personal taste outside {personal}, e.g. "{pers[0][:90]}"' + (''.join(f'\n      > {l[:160]}' for l in pers) if a.lines else ''))
        if index and not is_index_entry(name, index): notes.append('missing from the index')
        lines = body.splitlines()
        if len(lines) > 500: notes.append(f'body is {len(lines)} lines: the limit is 500, split by task into references/')
        personal_layer = name == personal or name.startswith(prefix)    # a taste file, not a how-to: no Gotchas needed
        if not personal_layer and not any(re.match(r'##\s+Gotchas\b', l) for l in lines[:40]): notes.append('no "## Gotchas" in the first 40 lines of the body')
        print(f'{name}: ' + ('ok' if not notes else ''))
        for n in notes: print(f'  - {n}')
        bodies[name] = prov
        triggers[name] = {w for w in re.findall(r"[a-z]{4,}", (desc + ' ' + when).lower()) if w not in TRIGGER_WORDS}

    # collisions: two descriptions that share most of their words fire on the same prompts (merge, or give each its own use)
    names = sorted(triggers)
    collide = []
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            A, B = triggers[x], triggers[y]
            if len(A) >= 5 and len(B) >= 5 and len(A & B) / len(A | B) > 0.5:
                collide.append((len(A & B) / len(A | B), x, y))
    collide.sort(key=lambda t: (-t[0], t[1], t[2]))
    print(f'\ntrigger collisions: {len(collide)}' + (' (descriptions share most words: merge, or give each its own use)' if collide else ''))
    for jac, x, y in collide[:10]:
        print(f'  - {x} / {y} ({jac:.0%} of description words shared)')

    # repeats: the same guideline written in two skills (keep it in its owner, link from the other). Lines are compared
    # only when they share rare words (an inverted index), so the cost grows with the number of real candidates, not n^2.
    lines_ = []
    for name, prov in bodies.items():
        for l in prov.splitlines():
            ws = frozenset(w for w in re.findall(r"[a-z]{4,}", l.lower()) if w not in COMMON)
            if len(ws) >= 6:
                lines_.append((name, l.strip(), ws))
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
    repeats.sort(key=lambda t: (-t[0], t[1], t[2]))
    print(f'\nrepeats across skills: {len(repeats)}' + (' (same guideline in two places: keep one owner, link from the other)' if repeats else ''))
    for jac, i, j in repeats[:10]:
        print(f'  - {lines_[i][0]} / {lines_[j][0]} ({jac:.0%} shared): "{lines_[i][1][:90]}"' +
              (f'\n      > {lines_[j][1][:150]}' if a.lines else ''))
    if os.path.exists(a.inbox):
        inbox = open(a.inbox, encoding='utf-8', errors='replace').read().splitlines()
        noise = [l for l in inbox if HARNESS.search(l)]
        print(f'\ninbox: {len(inbox)} lines, {len(noise)} harness-noise lines to archive')
    else:
        print(f'\ninbox: none at {a.inbox}')


if __name__ == '__main__':
    main()
