#!/usr/bin/env python3
"""Weekly watch over a skill library: new or updated skills upstream, gaps in the library, and how much it costs to carry.

Usage: skills-watch.py [--skills ~/.claude/skills] [--upstream anthropics/skills[:path] ...] [--inbox ~/.claude/lessons-inbox.md]
                       [--memory DIR ...] [--out ~/.claude/skills-watch] [--days 7]
Writes one short Markdown report to OUT/<date>.md (OUT/<date>-2.md for a second run that day) and remembers what it saw
in OUT/state.json, so each run only reports what changed. Reads public data only (the GitHub API and raw files, no
token needed for a weekly run) and installs nothing: the report lists candidates for a person to review. Exits 0 even
when the network is down or the audit fails, and says so in the report and the summary line.

  Upstream   skills added to or changed in each upstream repo since the last run, with their descriptions
  Effect     open feedback dated after the skill it belongs to was last updated (git history of the skill's folder
             when the skills folder is in git, else the newest file in it)
  Gaps       feedback lines in the inbox from the window that no skill's description covers (local or installed by a
             plugin), and the words that recur among them; a skill not installed whose description shares those words
             is named as a possible fill
  Health     the audit's flags per skill, trigger collisions, repeats and inbox noise (audit-skills.py, same folder)
  Footprint  what loads every session (skill descriptions, CLAUDE.md, a project's memory index) against what sits on
             disk until needed
"""
import argparse, datetime as dt, glob, json, os, re, shutil, subprocess, sys, urllib.request
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG, HARNESS, SKILLS, read_frontmatter

STOP = set('''a an the and or but of to in on for with at by from as is are was were be been it its this that these those
you your yours i me my we our they them their he she his her not no yes do does did done can could should would will just
than then so very too more most less into over under about after before when where what which who how why also only use
used using make made each per one two new all any some same other via like get got there here up out if else again
please now still lot much many well good bad keep add show see say said need needs want wants way thing things
dont don candidate review pending promoted archived status note'''.split())   # last row: the inbox's own labels
DATE = re.compile(r'(20\d\d-\d\d-\d\d)')
OPEN = re.compile(r'·\s*(candidate|pending)\s*·', re.I)                 # an inbox line still waiting for review
CLOSED = re.compile(r'→\s*\**\s*(promoted|done|archived)', re.I)        # ... unless it records its own resolution
# skills that arrive through plugins: the plugin cache, and the desktop app's skills plugin
INSTALLED = [os.path.join(CONFIG, 'plugins/cache/**/skills/*/SKILL.md'),
             os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/*/*/skills/*/SKILL.md')]


def words(text):
    return [w for w in re.findall(r"[a-z][a-z-]{2,}", text.lower()) if w not in STOP]


def text_of(v):
    return v if isinstance(v, str) else '' if v is None else str(v)


def fields(path):
    """The description and when_to_use of a local SKILL.md (block style included); '' when unreadable."""
    try:
        fm, _ = read_frontmatter(path)
    except ValueError:
        fm = {}
    return text_of(fm.get('description')), text_of(fm.get('when_to_use'))


def describe(text):
    """The description from fetched SKILL.md text, including YAML block style (description: > or |- with indented lines)."""
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


def unbullet(line):
    """An inbox line without its own '- ', so the report bullets it once."""
    return re.sub(r'^[-*]\s+', '', line)


def names_skill(name, line):
    """The line names the skill as a whole token (or in backticks), not inside another word."""
    return bool(re.search(rf'(?<![\w-]){re.escape(name)}(?![\w-])', line))


def last_updated(skills_dir, name, in_git):
    """The date a skill was last changed: its folder's last commit (today when it has uncommitted edits), else the
    newest file in it. A touch, a checkout or a reinstall does not move the git date."""
    folder = os.path.join(skills_dir, name)
    if in_git:
        dirty = subprocess.run(['git', '-C', skills_dir, 'status', '--porcelain', '--', f'{name}/'],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            return dt.date.today().isoformat()
        d = subprocess.run(['git', '-C', skills_dir, 'log', '-1', '--format=%cs', '--', f'{name}/'],
                           capture_output=True, text=True).stdout.strip()
        if d:
            return d
    mtimes = [os.path.getmtime(f) for f in glob.glob(os.path.join(folder, '**', '*'), recursive=True) if os.path.isfile(f)]
    return dt.date.fromtimestamp(max(mtimes)).isoformat() if mtimes else ''


def load_state(path, today):
    """state.json as a dict; a corrupt or wrong-shaped file is moved aside (with a note) and the run starts fresh."""
    if not os.path.exists(path):
        return {}, ''
    try:
        state = json.load(open(path, encoding='utf-8'))
        if isinstance(state, dict):
            return state, ''
        problem = 'is not a JSON object'
    except (ValueError, OSError) as e:
        problem = f'does not parse ({e})'
    bad, n = f'{path}.bad-{today}', 1
    while os.path.exists(bad):                    # keep every bad copy for a look
        n += 1
        bad = f'{path}.bad-{today}-{n}'
    os.replace(path, bad)
    return {}, f'- state.json {problem}: moved to {bad}; this run starts fresh, so everything upstream is a first look'


def report_path(out, today):
    """OUT/<date>.md, or <date>-2.md, -3 ... so a second run the same day keeps the first report (and its Proposed)."""
    path, n = os.path.join(out, f'{today}.md'), 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(out, f'{today}-{n}.md')
    return path


def enabled_plugin_skills():
    """SKILL.md files of the plugins enabled in <config>/settings.json, from their install paths."""
    try:
        enabled = json.load(open(os.path.join(CONFIG, 'settings.json'), encoding='utf-8')).get('enabledPlugins') or {}
        installed = json.load(open(os.path.join(CONFIG, 'plugins', 'installed_plugins.json'), encoding='utf-8')).get('plugins') or {}
    except (OSError, ValueError, AttributeError):
        return []
    return sorted(p for key, on in enabled.items() if on for e in installed.get(key, []) if isinstance(e, dict)
                  for p in glob.glob(os.path.join(e.get('installPath', ''), 'skills', '*', 'SKILL.md')))


def write_atomic(path, text):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skills', default=SKILLS, help='the local skills folder (default: %(default)s)')
    ap.add_argument('--upstream', nargs='*', default=['anthropics/skills'],
                    help='GitHub repos to watch, as owner/repo or owner/repo:path when skills are not in skills/')
    ap.add_argument('--inbox', default=os.path.join(CONFIG, 'lessons-inbox.md'), help='the lessons inbox (default: %(default)s)')
    ap.add_argument('--memory', nargs='*', default=sorted(glob.glob(os.path.join(CONFIG, 'projects', '*', 'memory'))),
                    help='project memory folders (default: every <config>/projects/*/memory)')
    ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch'), help='where reports and state go (default: %(default)s)')
    ap.add_argument('--days', type=int, default=7, help='the feedback window in days (default: %(default)s)')
    a = ap.parse_args()

    local_paths = sorted(glob.glob(os.path.join(a.skills, '*', 'SKILL.md')))
    if not local_paths:
        sys.exit(f'no skills found in {a.skills}: pass --skills <folder with <name>/SKILL.md>')
    os.makedirs(a.out, exist_ok=True)
    today = dt.date.today()
    since = today - dt.timedelta(days=a.days)
    STATE = os.path.join(a.out, 'state.json')
    state, state_note = load_state(STATE, today.isoformat())

    # local library: what each skill says it covers
    local = {}
    for p in local_paths:
        desc, when = fields(p)
        local[os.path.basename(os.path.dirname(p))] = {'desc': desc, 'when': when, 'bytes': os.path.getsize(p)}
    plugin_paths = {}
    for g in INSTALLED:
        for p in glob.glob(g, recursive=True):
            n = os.path.basename(os.path.dirname(p))
            if n not in plugin_paths or os.path.getmtime(p) > os.path.getmtime(plugin_paths[n]):
                plugin_paths[n] = p                                       # newest copy of each plugin skill
    plugin_skills = set(plugin_paths)
    offered = {}
    for p in glob.glob(os.path.join(CONFIG, 'plugins/marketplaces/*/**/skills/*/SKILL.md'), recursive=True):
        m = re.search(r'marketplaces/([^/]+)/(?:.*/)?([^/]+)/skills/([^/]+)/SKILL.md$', p)
        if m:
            offered[f'{m.group(1)}: {m.group(2)}/{m.group(3)}'] = (m.group(3), p)

    # upstream: folders added or changed since the last run (a folder's git sha changes whenever any file in it changes)
    upstream_notes, upstream_seen, unreadable = [], [], 0
    seen = state.get('upstream') if isinstance(state.get('upstream'), dict) else {}
    for spec in a.upstream:
        repo, _, sub = spec.partition(':')
        sub = sub.strip('/') or 'skills'
        try:
            branch = json.loads(get(f'https://api.github.com/repos/{repo}')).get('default_branch', 'main')
            items = json.loads(get(f'https://api.github.com/repos/{repo}/contents/{sub}?ref={branch}'))
            now = {x['name']: x['sha'] for x in items if x.get('type') == 'dir'}
        except Exception as e:
            upstream_notes.append(f'- {spec}: could not read ({e}); nothing compared this week')
            unreadable += 1
            continue
        before = seen.get(spec) if isinstance(seen.get(spec), dict) else None
        for name, sha in sorted(now.items()):
            status = 'first look' if before is None else 'new' if name not in before else 'updated' if before[name] != sha else None
            if status is None or (status == 'first look' and (name in local or name in plugin_skills)):
                continue
            url = f'https://raw.githubusercontent.com/{repo}/{branch}/{sub}/{name}/SKILL.md'
            try:
                desc = describe(get(url).decode('utf-8', 'replace'))
            except Exception:
                desc = ''
            have = 'installed' if (name in local or name in plugin_skills) else 'not installed'
            upstream_seen.append({'repo': spec, 'name': name, 'status': status, 'have': have, 'desc': desc, 'url': url})
        for name in sorted(set(before or {}) - set(now)):
            upstream_notes.append(f'- {spec}: `{name}` was removed upstream')
        seen[spec] = now
    state['upstream'] = seen

    # marketplaces: plugin skills on offer locally that were not there last run
    before_offer = state.get('offered') if isinstance(state.get('offered'), list) else None
    new_offer = [] if before_offer is None else sorted(k for k in offered if k not in before_offer)
    offer_desc = {k: fields(offered[k][1])[0] for k in offered}
    state['offered'] = sorted(offered)

    # gaps: recent feedback that no skill's description covers (harness text is noise, not feedback)
    have_inbox = os.path.exists(a.inbox)
    lines = open(a.inbox, encoding='utf-8', errors='replace').read().splitlines() if have_inbox else []
    recent = []
    for line in lines:
        m = DATE.search(line)
        if m and m.group(1) >= since.isoformat() and not HARNESS.search(line):
            recent.append(line.strip())
    vocab = {n: set(words(s['desc'] + ' ' + s['when'] + ' ' + n.replace('-', ' '))) for n, s in local.items()}
    for n, p in plugin_paths.items():
        if n not in vocab:                                                # an installed plugin skill covers its words too
            d, w = fields(p)
            vocab[n] = set(words(d + ' ' + w + ' ' + n.replace('-', ' ')))
    claude_md = os.path.join(CONFIG, 'CLAUDE.md')
    if os.path.exists(claude_md):                                         # habits live here too
        vocab['CLAUDE.md'] = set(words(open(claude_md, encoding='utf-8', errors='replace').read()))
    in_git = bool(shutil.which('git')) and subprocess.run(['git', '-C', a.skills, 'rev-parse', '--is-inside-work-tree'],
                                                          capture_output=True, text=True).stdout.strip() == 'true'
    updated = {}
    unmatched, routed = [], Counter()
    after = {}   # effect: open feedback that arrived after the skill's last update
    for line in recent:
        ws = set(words(line))
        named = sorted((n for n in local if names_skill(n, line)), key=lambda n: (-len(n), n))   # the line names its skill
        best = max(sorted(vocab), key=lambda n: len(ws & vocab[n]), default=None)
        if named:
            hit = named[0]
        elif best and len(ws & vocab[best]) >= 2:
            hit = best
        else:
            unmatched.append(line)
            continue
        routed[hit] += 1
        if hit in local and OPEN.search(line) and not CLOSED.search(line):
            if hit not in updated:
                updated[hit] = last_updated(a.skills, hit, in_git)
            if DATE.search(line).group(1) > updated[hit]:
                after.setdefault(hit, []).append(line)
    counts = Counter(w for l in unmatched for w in set(words(l)))
    recurring = [w for w, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12] if c >= 2]
    fills = []
    candidates = [(u['name'], u['name'], u['desc'], u['have']) for u in upstream_seen] + \
                 [(k, n, offer_desc[k], 'installed' if n in local or n in plugin_skills else 'offered')
                  for k, (n, _) in sorted(offered.items())]
    for label, name, desc, have in candidates:
        shared = sorted(set(recurring) & set(words(desc)))
        if len(shared) >= 2 and have != 'installed':
            fills.append((label, shared))

    # health: the audit, condensed to one line per flagged skill, plus its library-wide sections
    audit = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit-skills.py')
    try:
        r = subprocess.run([sys.executable, audit, a.skills], capture_output=True, text=True, timeout=120)
        out = r.stdout
        audit_error = '' if r.returncode == 0 else \
            (r.stderr.strip().splitlines() or [f'exit code {r.returncode}'])[-1]
    except Exception as e:
        out, audit_error = '', str(e)
    flagged = re.findall(r'^([^\s:]+): *\n((?:  - .*\n)+)', out, re.M)
    library = re.findall(r'^((?:trigger collisions|repeats across skills): [1-9].*\n(?:  - .*\n)*)', out, re.M)
    inbox_line = re.search(r'^inbox: .*$', out, re.M)

    # footprint: what loads every session against what waits on disk. A session loads its own project's MEMORY.md
    # only, so the largest index is the realistic per-session cost; summing every project's index overstates it.
    desc_bytes = sum(len((s['desc'] + s['when']).encode()) for s in local.values())
    skill_bytes = sum(s['bytes'] for s in local.values())
    extra_bytes = sum(os.path.getsize(f) for n in local for f in glob.glob(os.path.join(a.skills, n, '**', '*'), recursive=True)
                      if os.path.isfile(f) and os.path.basename(f) != 'SKILL.md')
    claude_bytes = os.path.getsize(claude_md) if os.path.exists(claude_md) else 0
    enabled = enabled_plugin_skills()
    plugin_bytes = sum(len(' '.join(fields(p)).encode()) for p in enabled)
    mem = []
    for d in a.memory:
        idx = os.path.join(d, 'MEMORY.md')
        notes = [f for f in glob.glob(os.path.join(d, '*.md')) if os.path.basename(f) != 'MEMORY.md']
        if os.path.exists(idx):
            mem.append((os.path.getsize(idx), sum(os.path.getsize(f) for f in notes), len(notes), os.path.basename(os.path.dirname(d))))
    biggest = max(mem, default=(0, 0, 0, ''))
    kb = lambda b: round(b / 1024, 1)
    foot = {'date': today.isoformat(), 'skills': len(local), 'skill_file_kb': kb(skill_bytes), 'skill_extra_kb': kb(extra_bytes),
            'descriptions_kb': kb(desc_bytes), 'plugin_descriptions_kb': kb(plugin_bytes), 'claude_md_kb': kb(claude_bytes), 'memory_index_max_kb': kb(biggest[0]),
            'memory_projects': len(mem), 'memory_kb': kb(sum(m[1] for m in mem)), 'memory_notes': sum(m[2] for m in mem)}
    foot['every_session_kb'] = kb(desc_bytes + plugin_bytes + claude_bytes + biggest[0])
    history = [h for h in state.get('footprint', []) if isinstance(h, dict)] if isinstance(state.get('footprint'), list) else []
    prev = next((h for h in reversed(history) if h.get('date') != foot['date']), None)
    state['footprint'] = ([h for h in history if h.get('date') != foot['date']] + [foot])[-26:]

    # report
    md = [f'# Skills watch, {today.isoformat()}', '', f'Window: {since.isoformat()} to {today.isoformat()}.', '']
    if state_note:
        md += [state_note, '']
    md += ['## New or updated upstream', '']
    first = [u for u in upstream_seen if u['status'] == 'first look']
    changed = [u for u in upstream_seen if u['status'] != 'first look']
    for repo in sorted({u['repo'] for u in first}):
        names = [u['name'] for u in first if u['repo'] == repo]
        md.append(f"- first look at {repo}: {len(names)} skills you do not have yet, recorded as the baseline: " + ', '.join(names))
    for u in changed:
        md.append(f"- **{u['name']}** ({u['repo']}, {u['status']}, {u['have']}): {u['desc'][:240]} ({u['url']})")
    if before_offer is None:
        md.append(f'- first look at local plugin marketplaces: {len(offered)} skills on offer, recorded as the baseline')
    for k in new_offer:
        md.append(f'- **{k}** (new in a plugin marketplace): {offer_desc[k][:240]}')
    if not changed and not new_offer and not first and before_offer is not None and not unreadable:
        md.append('- nothing new since the last run')
    md += upstream_notes + ['', '## Effect', '']
    md.append('Open feedback dated after the skill it belongs to was last updated: the update has not settled it yet.'
              if after else 'No open feedback arrived after the last update of the skill it belongs to.')
    for n, ls in sorted(after.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        md.append(f'- **{n}** (updated {updated[n]}): {len(ls)} line(s), e.g. {unbullet(ls[0])[:140]}')
    md += ['', '## Gaps in the library', '']
    if not have_inbox:
        md.append(f'No inbox at {a.inbox}: nothing to compare.')
    else:
        md.append(f'{len(recent)} feedback lines in the window; ' +
                  (', '.join(f'{n} {c}' for n, c in sorted(routed.items(), key=lambda kv: (-kv[1], kv[0]))) or 'none routed') + '.')
    if unmatched:
        md.append(f'{len(unmatched)} lines match no skill' + (f"; words that recur among them: {', '.join(recurring)}." if recurring else '.'))
        md += [f'  - {unbullet(l)[:200]}' for l in unmatched[:12]]
    if fills:
        md += ['', 'Skills that share those words (upstream or marketplace, not installed; read before installing):']
        md += [f"  - `{n}`: {', '.join(s)}" for n, s in fills]
    md += ['', '## Library health', '']
    if audit_error:
        md.append(f'- audit FAILED ({audit_error}): the library was not checked this run')
    md += [f"- **{n}**: " + '; '.join(x.strip()[2:] for x in body.strip().splitlines()) for n, body in flagged]
    for block in library:
        head, *rest = block.strip().splitlines()
        md += [f'- {head}'] + [f'  {x.strip()}' for x in rest]
    if inbox_line:
        md.append(f'- {inbox_line.group(0)}')
    if not audit_error and not flagged and not library:
        md.append('- the audit flags nothing')
    md += ['', '## Footprint', '',
           f"- every session carries about {foot['every_session_kb']} KB: {foot['descriptions_kb']} KB of descriptions for "
           f"{foot['skills']} local skills, {foot['plugin_descriptions_kb']} KB for {len(enabled)} skills of enabled "
           f"plugins, {foot['claude_md_kb']} KB of CLAUDE.md, and one project's memory index (largest "
           f"{foot['memory_index_max_kb']} KB" + (f", {biggest[3]})" if biggest[3] else ')'),
           f"- on disk until a task needs them: {foot['skill_file_kb']} KB of SKILL.md files and {foot['skill_extra_kb']} KB "
           f"of references and scripts; {foot['memory_kb']} KB across {foot['memory_notes']} memory notes in "
           f"{foot['memory_projects']} projects, read when recalled"]
    if prev and 'every_session_kb' in prev:
        md.append(f"- since {prev['date']}: skills {prev['skills']} to {foot['skills']}, every session {prev['every_session_kb']} "
                  f"to {foot['every_session_kb']} KB, descriptions {prev['descriptions_kb']} to {foot['descriptions_kb']} KB")
    path = report_path(a.out, today.isoformat())
    write_atomic(path, '\n'.join(md) + '\n')
    state['last_run'] = today.isoformat()
    write_atomic(STATE, json.dumps(state, indent=1))
    print(path)
    print(f"{len(changed)} upstream changes" + (f", {unreadable} upstream repos unreadable" if unreadable else '') +
          f", {len(new_offer)} new in marketplaces, {len(unmatched)} unmatched feedback lines, " +
          ('audit FAILED' if audit_error else f'{len(flagged)} skills flagged by the audit') +
          (', state.json was corrupt and moved aside' if state_note else ''))


if __name__ == '__main__':
    main()
