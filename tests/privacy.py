"""No personal details in a tracked file, or in prose written about the repo: no email, home path, private word.
  python3 tests/privacy.py      exits 1 and prints file:line and the kind of each hit, never the line itself, so a
                                public CI log shows no word
  python3 tests/privacy.py --text FILE [FILE ...]   the same gate over prose that is not a tracked file: a pull
                                request body, an issue, a commit message. Reads stdin when given no path.
Private words (names, places, accounts) live outside the repo, one per line or comma-separated: in $PRIVATE_WORDS (in
CI, the repository secret of that name) or in ~/.config/claude-code-learns/private-words. A line starting with # is a
note, not a word, so the list can explain itself. Locally your login name is one too. LICENSE holds the one name the
repo keeps, and the repo's own address holds its owner's, so both are skipped.
  python3 tests/privacy.py --test   checks the list parses as intended, then exits

One parser, one matcher, both modes. A hand-rolled `grep -f` over the word file is not the same check: grep reads a
line as one pattern, so a comma-separated line passes prose that holds one of its words, and it says 0, which reads
as clean (2026-11-22).
"""
import os, re, subprocess, sys
from pathlib import Path

EMAIL = re.compile(r'[\w.%+-]+@([\w-]+\.)+[a-z]{2,}', re.I)
HOME_PATH = re.compile(r'/(Users|home)/[A-Za-z][A-Za-z0-9._-]')   # a one-letter folder (/Users/x/) is a test placeholder
WORDS_FILE = Path.home() / '.config' / 'claude-code-learns' / 'private-words'


def private_words():
    text = os.environ.get('PRIVATE_WORDS', '')
    if WORDS_FILE.exists():
        text += '\n' + WORDS_FILE.read_text()
    lines = [l for l in text.splitlines() if not l.lstrip().startswith('#')]   # a note, not a word
    words = {w.strip().lower() for l in lines for w in l.split(',') if w.strip()}
    if not os.environ.get('CI') and os.environ.get('USER'):
        words.add(os.environ['USER'].lower())
    return words


def matcher(words, own_address=None):
    """The kinds to look for, in one place, so prose and tracked files are judged alike."""
    word = (re.compile(r'(?<![a-z0-9])(' + '|'.join(map(re.escape, sorted(words))) + r')(?![a-z0-9])', re.I)
            if words else None)
    return own_address, (('email', EMAIL), ('home path', HOME_PATH), ('private word', word))


def scan(lines, kinds, own_address=None):
    """Line numbers and the kind of each hit; the line itself is never returned, so a public log shows no word."""
    for n, line in enumerate(lines, 1):
        if own_address:
            line = own_address.sub('OWNER', line)
        for kind, rx in kinds:
            if rx and rx.search(line):
                yield n, kind


def check_text(paths):
    """The gate over prose: the same words, the same matcher, no git and no repo needed."""
    words = private_words()
    _, kinds = matcher(words)
    hits = []
    for path in paths or ['-']:
        text = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
        hits += [f'{path}:{n}: {kind}' for n, kind in scan(text.splitlines(), kinds)]
    print('\n'.join(hits) or 'no emails, home paths or private words')
    if not words:
        print(f'no private words set (PRIVATE_WORDS, or {WORDS_FILE}): names were not checked')
    return 1 if hits else 0


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True, check=True).stdout


def self_test():
    """A comment is dropped whole, commas and all, so a note never becomes something to hunt for."""
    import tempfile
    sample = ('# one per line. Deliberately not here: "widget", which the repo uses\n'
              'Acme, Zarco\n'
              '  # an indented note, with a comma\n'
              'bluesky\n\n')
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'private-words'
        f.write_text(sample)
        global WORDS_FILE
        WORDS_FILE, keep = f, WORDS_FILE
        env = {k: os.environ.pop(k) for k in ('PRIVATE_WORDS', 'USER') if k in os.environ}
        os.environ['CI'] = '1'
        try:
            got = private_words()
        finally:
            WORDS_FILE = keep
            os.environ.update(env)
            os.environ.pop('CI', None)
    want = {'acme', 'zarco', 'bluesky'}
    if got != want:
        print(f'self-test failed: parsed {sorted(got)}, wanted {sorted(want)}')
        return 1
    # the case that sent this check wrong: 'Acme' shares a line with 'Zarco', so `grep -f` reads one pattern,
    # finds nothing in prose holding only 'Acme', and prints 0. The shared matcher splits the line first.
    _, kinds = matcher(want)
    prose = ['This body mentions Acme in passing.', 'and nothing else at all']
    caught = [(n, k) for n, k in scan(prose, kinds)]
    if caught != [(1, 'private word')]:
        print(f'self-test failed: prose scan returned {caught}, wanted [(1, "private word")]')
        return 1
    print(f'self-test ok: {len(want)} words, 2 notes dropped, a word from a shared line caught in prose')
    return 0


def main():
    os.chdir(Path(__file__).resolve().parent.parent)
    origin = git('remote', 'get-url', 'origin').strip()
    owner = re.search(r'[:/]([^/:]+)/[^/]+?(\.git)?$', origin).group(1)
    own_address = re.compile(rf'github\.com/{re.escape(owner)}/|{re.escape(owner)}\.github\.io', re.I)
    words = private_words()
    own_address, kinds = matcher(words, own_address)
    hits = []
    for path in git('ls-files').splitlines():
        if path == 'LICENSE':
            continue
        try:
            lines = Path(path).read_text(encoding='utf-8').splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        hits += [f'{path}:{n}: {kind}' for n, kind in scan(lines, kinds, own_address)]
    print('\n'.join(hits) or 'no emails, home paths or private words')
    if not words:
        print(f'no private words set (PRIVATE_WORDS, or {WORDS_FILE}): names were not checked')
    return 1 if hits else 0


if __name__ == '__main__':
    if '--test' in sys.argv:
        sys.exit(self_test())
    if '--text' in sys.argv:
        sys.exit(check_text(sys.argv[sys.argv.index('--text') + 1:]))
    sys.exit(main())
