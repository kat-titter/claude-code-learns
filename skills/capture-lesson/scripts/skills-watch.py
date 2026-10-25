#!/usr/bin/env python3
"""Weekly watch over a skill library: new or updated skills upstream, gaps in the library, and how much it costs to carry.

Usage: skills-watch.py [--skills ~/.claude/skills] [--upstream anthropics/skills ...] [--inbox ~/.claude/lessons-inbox.md]
                       [--memory DIR ...] [--out ~/.claude/skills-watch] [--days 7]
Writes one short Markdown report to OUT/<date>.md and remembers what it saw in OUT/state.json, so each run only reports
what changed. Reads public data only (the GitHub contents API, no token needed for a weekly run) and installs nothing:
the report lists candidates for a person to review. Exits 0 even when the network is down, and says so in the report.

  Upstream   skills added to or changed in each upstream repo since the last run, with their descriptions
  Gaps       feedback lines in the inbox from the window that no local skill's description covers, and the words that
             recur among them; an upstream skill whose description shares those words is named as a possible fill
  Health     the audit's flags per skill (audit-skills.py, same folder)
  Footprint  what loads every session (skill descriptions, memory indexes) against what sits on disk until needed
"""
import argparse, datetime as dt, glob, json, os, re, subprocess, sys, urllib.request
from collections import Counter

HOME = os.path.expanduser
# the Claude config folder this skill is installed in: <config>/skills/capture-lesson/scripts/<this file>
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ap = argparse.ArgumentParser()
ap.add_argument('--skills', default=os.path.join(CONFIG, 'skills'))
ap.add_argument('--upstream', nargs='*', default=['anthropics/skills'])
ap.add_argument('--inbox', default=os.path.join(CONFIG, 'lessons-inbox.md'))
ap.add_argument('--memory', nargs='*', default=sorted(glob.glob(os.path.join(CONFIG, 'projects', '*', 'memory'))))
ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch'))
ap.add_argument('--days', type=int, default=7)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
STATE = os.path.join(a.out, 'state.json')
state = json.load(open(STATE)) if os.path.exists(STATE) else {}
today = dt.date.today()
since = today - dt.timedelta(days=a.days)
STOP = set('''a an the and or but of to in on for with at by from as is are was were be been it its this that these those
you your yours i me my we our they them their he she his her not no yes do does did done can could should would will just
than then so very too more most less into over under about after before when where what which who how why also only use
used using make made each per one two new all any some same other via like get got there here up out if else again
please now still lot much many well good bad keep add show see say said need needs want wants way thing things
dont don candidate review pending promoted archived status note'''.split())   # last row: the inbox's own labels

def words(text):
    return [w for w in re.findall(r"[a-z][a-z-]{2,}", text.lower()) if w not in STOP]

def frontmatter(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(':')
        if v: fm[k.strip()] = v.strip()
    return fm, text

def describe(text):
    """The description from a SKILL.md, including YAML block style (description: > or |- with indented lines)."""
    m = re.search(r'^description:[ \t]*(.*)$', text, re.M)
    if not m:
        return ''
    first = m.group(1).strip()
    if first in ('>', '>-', '|', '|-', ''):
        block = re.match(r'((?:[ \t]+.*\n?)+)', text[m.end() + 1:])
        first = ' '.join(l.strip() for l in block.group(1).splitlines()) if block else ''
    return first.strip('"\'')

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'skills-watch', 'Accept': 'application/vnd.github+json'})
    return urllib.request.urlopen(req, timeout=30).read()

# local library: what each skill says it covers
local = {}
for p in sorted(glob.glob(os.path.join(a.skills, '*', 'SKILL.md'))):
    fm, text = frontmatter(p)
    local[os.path.basename(os.path.dirname(p))] = {'desc': fm.get('description', ''), 'when': fm.get('when_to_use', ''),
                                                   'bytes': len(text.encode())}
# skills that arrive through plugins: installed (plugin cache, the desktop app's skills plugin) and on offer (marketplaces)
INSTALLED = [os.path.join(CONFIG, 'plugins/cache/**/skills/*/SKILL.md'),
             HOME('~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/*/*/skills/*/SKILL.md')]
plugin_skills = {os.path.basename(os.path.dirname(p)) for g in INSTALLED for p in glob.glob(g, recursive=True)}
offered = {}
for p in glob.glob(os.path.join(CONFIG, 'plugins/marketplaces/*/**/skills/*/SKILL.md'), recursive=True):
    m = re.search(r'marketplaces/([^/]+)/(?:.*/)?([^/]+)/skills/([^/]+)/SKILL.md$', p)
    if m:
        offered[f'{m.group(1)}: {m.group(2)}/{m.group(3)}'] = p

# upstream: folders added or changed since the last run (a folder's git sha changes whenever any file in it changes)
report, upstream_new = [], []
seen = state.get('upstream', {})
for repo in a.upstream:
    try:
        items = json.loads(get(f'https://api.github.com/repos/{repo}/contents/skills'))
        now = {x['name']: x['sha'] for x in items if x.get('type') == 'dir'}
    except Exception as e:
        report.append(f'- {repo}: could not read ({e}); nothing compared this week')
        continue
    before = seen.get(repo)
    for name, sha in sorted(now.items()):
        status = 'first look' if before is None else 'new' if name not in before else 'updated' if before[name] != sha else None
        if status is None or (status == 'first look' and (name in local or name in plugin_skills)):
            continue
        try:
            raw = get(f'https://raw.githubusercontent.com/{repo}/main/skills/{name}/SKILL.md').decode('utf-8', 'replace')
            desc = describe(raw)
        except Exception:
            desc = ''
        have = 'installed' if (name in local or name in plugin_skills) else 'not installed'
        upstream_new.append({'repo': repo, 'name': name, 'status': status, 'have': have, 'desc': desc})
    gone = sorted(set(before or {}) - set(now))
    for name in gone:
        report.append(f'- {repo}: `{name}` was removed upstream')
    seen[repo] = now
state['upstream'] = seen

# marketplaces: plugin skills on offer locally that were not there last run
before_offer = state.get('offered')
new_offer = [] if before_offer is None else sorted(k for k in offered if k not in before_offer)
offer_desc = {k: describe(open(offered[k], encoding='utf-8', errors='replace').read()) for k in new_offer}
state['offered'] = sorted(offered)

# gaps: recent feedback that no skill's description covers
lines = open(a.inbox, encoding='utf-8', errors='replace').read().splitlines() if os.path.exists(a.inbox) else []
recent = []
for line in lines:
    m = re.search(r'(20\d\d-\d\d-\d\d)', line)
    if m and m.group(1) >= since.isoformat():
        recent.append(line.strip())
vocab = {n: set(words(s['desc'] + ' ' + s['when'] + ' ' + n.replace('-', ' '))) for n, s in local.items()}
unmatched, routed = [], Counter()
for line in recent:
    ws = set(words(line))
    named = [n for n in local if n in line]                     # a line that already names its skill is routed
    best = max(local, key=lambda n: len(ws & vocab[n]), default=None)
    if named:
        routed[named[0]] += 1
    elif best and len(ws & vocab[best]) >= 2:
        routed[best] += 1
    else:
        unmatched.append(line)
recurring = [w for w, c in Counter(w for l in unmatched for w in set(words(l))).most_common(12) if c >= 2]
fills = []
for name, desc, have in [(u['name'], u['desc'], u['have']) for u in upstream_new] + \
                        [(k, describe(open(p, encoding='utf-8', errors='replace').read()), 'offered') for k, p in offered.items()]:
    shared = sorted(set(recurring) & set(words(desc)))
    if len(shared) >= 2 and have != 'installed':
        fills.append((name, shared))

# health: the audit, condensed to one line per flagged skill
audit = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit-skills.py')
try:
    out = subprocess.run([sys.executable, audit, a.skills], capture_output=True, text=True, timeout=60).stdout
    flagged = re.findall(r'^([\w-]+): \n((?:  - .*\n)+)', out, re.M)
except Exception as e:
    flagged, out = [], f'audit failed: {e}'

# footprint: what loads every session against what waits on disk
desc_bytes = sum(len((s['desc'] + s['when']).encode()) for s in local.values())
skill_bytes = sum(s['bytes'] for s in local.values())
mem = []
for d in a.memory:
    idx = os.path.join(d, 'MEMORY.md')
    total = sum(os.path.getsize(f) for f in glob.glob(os.path.join(d, '*.md')))
    if os.path.exists(idx):
        mem.append((d, os.path.getsize(idx), total, len(glob.glob(os.path.join(d, '*.md'))) - 1))
foot = {'date': today.isoformat(), 'skills': len(local), 'skill_kb': round(skill_bytes / 1024, 1),
        'descriptions_kb': round(desc_bytes / 1024, 1), 'memory_index_kb': round(sum(m[1] for m in mem) / 1024, 1),
        'memory_kb': round(sum(m[2] for m in mem) / 1024, 1), 'memory_notes': sum(m[3] for m in mem)}
history = state.get('footprint', [])
prev = history[-1] if history else None
history = [h for h in history if h['date'] != foot['date']] + [foot]
state['footprint'] = history[-26:]

# report
md = [f'# Skills watch, {today.isoformat()}', '', f'Window: {since.isoformat()} to {today.isoformat()}.', '']
md += ['## New or updated upstream', '']
first = [u for u in upstream_new if u['status'] == 'first look']
changed = [u for u in upstream_new if u['status'] != 'first look']
if first:
    md.append(f"- first look at {first[0]['repo']}: {len(first)} skills you do not have yet, recorded as the baseline: "
              + ', '.join(u['name'] for u in first))
for u in changed:
    md.append(f"- **{u['name']}** ({u['repo']}, {u['status']}, {u['have']}): {u['desc'][:240]}")
if before_offer is None:
    md.append(f'- first look at local plugin marketplaces: {len(offered)} skills on offer, recorded as the baseline')
for k in new_offer:
    md.append(f'- **{k}** (new in a plugin marketplace): {offer_desc[k][:240]}')
if not changed and not new_offer and not first and before_offer is not None:
    md.append('- nothing new since the last run')
md += report + ['', '## Gaps in the library', '']
md.append(f'{len(recent)} feedback lines in the window; ' + (', '.join(f'{n} {c}' for n, c in routed.most_common()) or 'none routed') + '.')
if unmatched:
    md.append(f'{len(unmatched)} lines match no skill' + (f"; words that recur among them: {', '.join(recurring)}." if recurring else '.'))
    md += [f'  - {l[:200]}' for l in unmatched[:12]]
if fills:
    md += ['', 'Upstream skills that share those words (read before installing):']
    md += [f"  - `{n}`: {', '.join(s)}" for n, s in fills]
md += ['', '## Library health', '']
md += [f"- **{n}**: " + '; '.join(x.strip()[2:] for x in body.strip().splitlines()) for n, body in flagged] or ['- the audit flags nothing']
md += ['', '## Footprint', '',
       f"- every session carries {foot['descriptions_kb']} KB of skill descriptions for {foot['skills']} skills; "
       f"the {foot['skill_kb']} KB of skill bodies load only when a task matches",
       f"- memory: {foot['memory_index_kb']} KB of index lines load each session; {foot['memory_kb']} KB across "
       f"{foot['memory_notes']} notes load only when recalled"]
if prev:
    md.append(f"- since {prev['date']}: skills {prev['skills']} to {foot['skills']}, descriptions {prev['descriptions_kb']} "
              f"to {foot['descriptions_kb']} KB, memory index {prev['memory_index_kb']} to {foot['memory_index_kb']} KB")
path = os.path.join(a.out, f'{today.isoformat()}.md')
open(path, 'w').write('\n'.join(md) + '\n')
state['last_run'] = today.isoformat()
json.dump(state, open(STATE, 'w'), indent=1)
print(path)
print(f"{len(changed)} upstream changes, {len(new_offer)} new in marketplaces, {len(unmatched)} unmatched feedback lines, {len(flagged)} skills flagged by the audit")
