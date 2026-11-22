"""Nothing public wraps where wrapping breaks the layout.

  python3 tests/formatting.py        exits 1 and prints file:line for each failure

A line inside a fenced block that carries interior alignment (two or more spaces between
visible text, the mark of a column layout) must fit the width GitHub renders, or the
second column folds under the first and the block reads as prose. A plain long command
has no interior alignment and is left alone: breaking it would break the command.
Caught on 2026-11-21, when a file map and a sample report both wrapped on the rendered
README and the explainer page.
"""
import re, subprocess, sys
from pathlib import Path

WIDTH = 78
FENCE = re.compile(r'```[a-z]*\n(.*?)```', re.S)
ALIGNED = re.compile(r'\S {2,}\S')


def failures(text):
    """Line numbers in `text` whose aligned content runs past the rendered width."""
    for m in FENCE.finditer(text):
        start = text[:m.start(1)].count('\n') + 1
        for i, line in enumerate(m.group(1).split('\n')):
            if len(line) > WIDTH and ALIGNED.search(line):
                yield start + i, len(line), line


def main():
    root = Path(__file__).resolve().parent.parent
    files = subprocess.run(['git', '-C', root, 'ls-files', '*.md'],
                           capture_output=True, text=True, check=True).stdout.split()
    hits = []
    for rel in files:
        try:
            text = (root / rel).read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for n, width, line in failures(text):
            hits.append(f'{rel}:{n}: aligned line is {width} chars, over {WIDTH}: {line.strip()[:50]}...')
    print('\n'.join(hits) or f'no aligned line in a fenced block runs past {WIDTH} characters')
    return 1 if hits else 0


def self_test():
    good = '```\na   one\nb   two\nc   three\n```\n'
    wrapped = '```\na   ' + 'x' * 90 + '\n```\n'
    command = '```\ncurl ' + 'y' * 90 + '\n```\n'          # long, but nothing to misalign
    for name, sample, want in (('aligned and short', good, 0), ('aligned and long', wrapped, 1),
                               ('long command', command, 0)):
        got = len(list(failures(sample)))
        if got != want:
            print(f'self-test failed: {name} gave {got} failures, wanted {want}')
            return 1
    print('self-test ok: a wrapped column is caught, a long command is not')
    return 0


if __name__ == '__main__':
    sys.exit(self_test() if '--test' in sys.argv else main())
