"""No personal details in a tracked file: no email address, no home path, no private word.
  python3 tests/privacy.py      exits 1 and prints file:line and the kind of each hit, never the line itself, so a
                                public CI log shows no word
Private words (names, places, accounts) live outside the repo, one per line or comma-separated: in $PRIVATE_WORDS (in
CI, the repository secret of that name) or in ~/.config/claude-code-learns/private-words. Locally your login name is
one too. LICENSE holds the one name the repo keeps, and the repo's own address holds its owner's, so both are skipped.
"""
import os, re, subprocess, sys
from pathlib import Path

EMAIL = re.compile(r'[\w.%+-]+@([\w-]+\.)+[a-z]{2,}', re.I)
HOME_PATH = re.compile(r'/(Users|home)/[A-Za-z]')
WORDS_FILE = Path.home() / '.config' / 'claude-code-learns' / 'private-words'


def private_words():
    text = os.environ.get('PRIVATE_WORDS', '')
    if WORDS_FILE.exists():
        text += '\n' + WORDS_FILE.read_text()
    words = {w.strip().lower() for w in re.split(r'[,\n]', text) if w.strip()}
    if not os.environ.get('CI') and os.environ.get('USER'):
        words.add(os.environ['USER'].lower())
    return words


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True, check=True).stdout


def main():
    os.chdir(Path(__file__).resolve().parent.parent)
    origin = git('remote', 'get-url', 'origin').strip()
    owner = re.search(r'[:/]([^/:]+)/[^/]+?(\.git)?$', origin).group(1)
    own_address = re.compile(rf'github\.com/{re.escape(owner)}/|{re.escape(owner)}\.github\.io', re.I)
    words = private_words()
    word = re.compile(r'(?<![a-z0-9])(' + '|'.join(map(re.escape, sorted(words))) + r')(?![a-z0-9])', re.I) if words else None
    hits = []
    for path in git('ls-files').splitlines():
        if path == 'LICENSE':
            continue
        try:
            lines = Path(path).read_text(encoding='utf-8').splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for n, line in enumerate(lines, 1):
            line = own_address.sub('OWNER', line)
            for kind, rx in (('email', EMAIL), ('home path', HOME_PATH), ('private word', word)):
                if rx and rx.search(line):
                    hits.append(f'{path}:{n}: {kind}')
    print('\n'.join(hits) or 'no emails, home paths or private words')
    if not words:
        print(f'no private words set (PRIVATE_WORDS, or {WORDS_FILE}): names were not checked')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
