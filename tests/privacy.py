"""No personal details in a tracked file: no email address, no home path, no private word.
  python3 tests/privacy.py      exits 1 and prints file:line and the kind of each hit, never the line itself, so a
                                public CI log shows no word
Private words (names, places, accounts) live outside the repo, one per line or comma-separated: in $PRIVATE_WORDS (in
CI, the repository secret of that name) or in ~/.config/claude-code-learns/private-words. A line starting with # is a
note, not a word, so the list can explain itself. Locally your login name is one too. LICENSE holds the one name the
repo keeps, and the repo's own address holds its owner's, so both are skipped.
  python3 tests/privacy.py --test   checks the list parses as intended, then exits
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


def word_rx(words):
    """One pattern for every private word, matched whole and in any case; None when there are none."""
    return re.compile(r'(?<![a-z0-9])(' + '|'.join(map(re.escape, sorted(words))) + r')(?![a-z0-9])', re.I) if words else None


def own_address_rx(owner):
    """The owner's own GitHub addresses, which a public repo may name."""
    return re.compile(rf'github\.com/{re.escape(owner)}/|{re.escape(owner)}\.github\.io', re.I)


def leaks(line, own_address, word):
    """The kinds of leak on one line: an email, a home path, a private word. review3.py checks reviews with this."""
    line = own_address.sub('OWNER', line)
    return [kind for kind, rx in (('email', EMAIL), ('home path', HOME_PATH), ('private word', word)) if rx and rx.search(line)]


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
    print(f'self-test ok: {len(want)} words, 2 notes dropped')
    return 0


def main():
    os.chdir(Path(__file__).resolve().parent.parent)
    origin = git('remote', 'get-url', 'origin').strip()
    owner = re.search(r'[:/]([^/:]+)/[^/]+?(\.git)?$', origin).group(1)
    own_address = own_address_rx(owner)
    words = private_words()
    word = word_rx(words)
    hits = []
    for path in git('ls-files').splitlines():
        if path == 'LICENSE':
            continue
        try:
            lines = Path(path).read_text(encoding='utf-8').splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for n, line in enumerate(lines, 1):
            hits += [f'{path}:{n}: {kind}' for kind in leaks(line, own_address, word)]
    print('\n'.join(hits) or 'no emails, home paths or private words')
    if not words:
        print(f'no private words set (PRIVATE_WORDS, or {WORDS_FILE}): names were not checked')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(self_test() if '--test' in sys.argv else main())
