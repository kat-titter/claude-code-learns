"""What your own library and this repo's published copy of a skill no longer share.

The two copies differ by design: the installed skill is where lessons land, this repo is a scrubbed snapshot
published as an example, so prose drifts on purpose. Code is the part that must not: a fix in one copy and not the
other is a silent bug, and nothing else here would tell you.
  python3 tests/drift.py            per-file report, exit 0
  python3 tests/drift.py --strict   exit 1 if any script's code lines differ
  python3 tests/drift.py --test     self-test on a built fixture, then exit
  python3 tests/drift.py --live DIR compare against another skills/ folder (default $CLAUDE_CONFIG_DIR, else ~/.claude)
Only skills/*/scripts/ is compared, and only lines that are not blank and not a whole-line comment; SKILL.md and the
other prose is left alone. A trailing comment on a line of code still counts as part of that line, so an edit to one
shows up as drift. The report names files, never their lines, but the names are your library's: keep it off a public
page. Without an installed library (CI) it prints one line and passes.
"""
import difflib, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MARK = {'.py': '#', '.sh': '#', '.js': '//', '.cjs': '//', '.mjs': '//', '.html': '<!--', '.css': '/*'}


def live_root():
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or Path.home() / '.claude') / 'skills'


def code(path):
    """A file's lines with the blank ones and the whole-line comments dropped. None if it is not text."""
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        return None
    mark = MARK.get(path.suffix)
    return [s for s in (l.strip() for l in text.splitlines())
            if s and not (mark and s.startswith(mark))]


def compare(repo, live):
    """Per skill: [(file, lines only in repo, lines only in live)], repo-only files, live-only files."""
    rows, only_repo, only_live = [], [], []
    for d in sorted(repo.glob('*/scripts')):
        name = d.parent.name
        there = live / name / 'scripts'
        if not there.is_dir():
            continue                      # a skill you have not installed is not drift
        here_files = {f.relative_to(d) for f in d.rglob('*') if f.is_file()}
        there_files = {f.relative_to(there) for f in there.rglob('*') if f.is_file()}
        only_repo += [f'{name}/{f}' for f in sorted(here_files - there_files)]
        only_live += [f'{name}/{f}' for f in sorted(there_files - here_files)]
        for f in sorted(here_files & there_files):
            a, b = code(d / f), code(there / f)
            if a is None or b is None or a == b:
                continue
            diff = list(difflib.unified_diff(a, b, n=0))
            r = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
            v = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
            rows.append((f'{name}/{f}', r, v))
    return rows, only_repo, only_live


def report(rows, only_repo, only_live):
    if rows:
        print(f'{"file":52s} {"here only":>10s} {"yours only":>11s}')
        for f, r, v in rows:
            print(f'{f:52s} {r:>10d} {v:>11d}')
        print(f'\n{sum(r for _, r, _ in rows)} lines here your library lacks: published and never pulled back.')
        print(f'{sum(v for _, _, v in rows)} lines yours this repo lacks: your work, not yet published.')
    else:
        print('every installed skill\'s scripts match this repo, line for line.')
    for label, names in (('only here', only_repo), ('only in yours', only_live)):
        if names:
            print(f'\n{label} ({len(names)}): ' + ', '.join(names))


def self_test():
    """A comment-only change is not drift; a code change is, and the count says which side the line is on."""
    import tempfile
    files = {
        'a/scripts/same.py': ('# published note\nx = 1\n', '# a different note\nx = 1\n'),
        'a/scripts/moved.py': ('import os\nimport sys\ny = 2\n', 'y = 2\n'),
        'a/scripts/gone.py': ('z = 3\n', None),
        'a/scripts/new.py': (None, 'w = 4\n'),
        'b/scripts/untouched.sh': ('echo hi\n', 'echo hi\n'),
        'c/scripts/uninstalled.py': ('v = 5\n', None),          # skill c is not installed at all: never drift
    }
    with tempfile.TemporaryDirectory() as d:
        repo, live = Path(d) / 'repo', Path(d) / 'live'
        for rel, (a, b) in files.items():
            for root, text in ((repo, a), (live, b)):
                if text is None:
                    continue
                if rel.startswith('c/') and root is live:
                    continue
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
        rows, only_repo, only_live = compare(repo, live)
    want_rows = [('a/moved.py', 2, 0)]
    bad = []
    if rows != want_rows:
        bad.append(f'rows: got {rows}, wanted {want_rows}')
    if only_repo != ['a/gone.py']:
        bad.append(f'only here: got {only_repo}')
    if only_live != ['a/new.py']:
        bad.append(f'only in yours: got {only_live}')
    for line in bad:
        print('self-test failed: ' + line)
    if bad:
        return 1
    print('self-test ok: a comment-only change is not drift, a dropped import is, and an uninstalled skill is skipped')
    return 0


def main(argv):
    if '--test' in argv:
        return self_test()
    live = Path(argv[argv.index('--live') + 1]) if '--live' in argv else live_root()
    if not live.is_dir():
        print(f'no installed library at {live}: nothing to compare')
        return 0
    rows, only_repo, only_live = compare(HERE / 'skills', live)
    report(rows, only_repo, only_live)
    return 1 if (rows and '--strict' in argv) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
