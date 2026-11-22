#!/usr/bin/env python3
"""What the person built this week, read from the files their git repos changed in the last N days.

Usage: week-context.py [--days 7] [--roots ~] [--out <config>/skills-watch/week-context.json]
Finds every git repo under the roots with a commit in the window, scans only the files those commits touched, and
records which front-end and tooling features they use (FEATURES: a code pattern and the words people post with).
feed-trends.py --context reads the JSON to open a second lane, posts about the stack in use this week; the two X
searches it prints carry that stack into the next collection.
"""
import argparse, datetime as dt, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG   # the install root, so --out and feed-trends.py --context name one file

# name: (pattern in the changed code, words a post about it would use; specific, since a bare 'canvas' matched the
# company and a bare 'interactive' matched anything, 2026-11-21)
FEATURES = {
    'web pages': (r'<html\b|<!doctype html', ['frontend', 'front-end', 'css', 'html', 'web design', 'ui']),
    'svg': (r'<svg\b', ['svg']),
    'canvas': (r"getContext\(\s*['\"]2d", ['html canvas', 'canvas api', '<canvas>']),
    'webgl': (r"getContext\(\s*['\"]webgl|gl_FragColor|precision (high|medium)p", ['webgl', 'shader', 'shaders', 'glsl']),
    'three.js': (r"three(\.module)?(\.min)?\.js|from ['\"]three['\"]", ['three.js', 'threejs']),
    'p5.js': (r'p5(\.min)?\.js', ['p5.js', 'p5js']),
    'd3': (r"d3(\.v\d)?(\.min)?\.js|from ['\"]d3['\"]", ['d3.js', 'd3']),
    'generative art': (r'noise\(|Math\.random\(\)[^;]*\*', ['generative art', 'creative coding', 'genart']),
    'interactive figures': (r'type="range"|pointermove|addEventListener\(\s*[\'"](pointer|mouse)', ['interactive html', 'interactive page', 'interactive figure', 'explorable', 'data viz', 'dataviz']),
    'animation': (r'requestAnimationFrame|@keyframes|prefers-reduced-motion', ['web animation', 'css animation', 'motion design', 'animating', 'animation']),
    'web audio': (r'AudioContext', ['web audio']),
    'dark mode': (r'prefers-color-scheme', ['dark mode']),
    'mobile layout': (r'@media[^{]*max-width|name="viewport"', ['responsive design', 'responsive', 'mobile layout']),
    'print and pdf': (r'@media print|@page\b', ['print css', 'pdf export']),
    'slides': (r'class="[^"]*\bslide\b', ['html slides', 'slide deck', 'slides']),
    'typography': (r'fonts\.googleapis|@font-face|font-feature-settings', ['typography', 'web fonts']),
    'web images': (r'\.webp\b|srcset=', ['webp', 'image optimization']),
    'diagrams': (r'mermaid', ['mermaid', 'diagrams']),
    'math': (r'katex|mathjax', ['katex', 'mathjax']),
    'github pages': (r'gh-pages|github\.io', ['github pages', 'static site']),
    'github actions': (r'^\s*runs-on:', ['github actions']),
}
# prose (.md) left out: a skill or README that names a feature does not use it (2026-11-21: docs matched all 18)
CODE = ('.html', '.htm', '.css', '.js', '.mjs', '.ts', '.svg', '.py', '.yml', '.yaml')
SKIP = ('/Library/', '/node_modules/', '/.worktrees/', '/.Trash/')


def repos(roots, depth=4):
    """Git repos under the roots, at most depth folders down, skipping caches and worktrees."""
    for root in roots:
        root = os.path.expanduser(root)
        for d, subs, _ in os.walk(root):
            if any(s in d + '/' for s in SKIP) or d[len(root):].count(os.sep) >= depth:
                subs[:] = []
                continue
            if '.git' in subs:
                yield d
            subs[:] = [s for s in subs if not s.startswith('.')]


def touched(repo, days):
    """Files changed by commits in the window that still exist, code types only."""
    out = subprocess.run(['git', '-C', repo, 'log', f'--since={days} days ago', '--name-only', '--format='],
                         capture_output=True, text=True).stdout
    names = {n for n in out.splitlines() if n.endswith(CODE)}
    return [os.path.join(repo, n) for n in sorted(names) if os.path.isfile(os.path.join(repo, n))]


def scan(files):
    """Feature names whose pattern appears in any of the files."""
    found = set()
    for f in files:
        try:
            text = open(f, errors='replace').read(2_000_000)
        except OSError:
            continue
        found |= {name for name, (pat, _) in FEATURES.items() if name not in found and re.search(pat, text, re.I | re.M)}
    return found


def searches(features, since):
    """Two X searches: the stack built with agents (a lower bar), and the stack on its own (a higher one)."""
    words = [w for f in features for w in FEATURES[f][1][:2]]
    stack = '(' + ' OR '.join(f'"{w}"' if ' ' in w or '.' in w else w for w in words) + ')'
    agents = '("claude code" OR codex OR cursor OR agent OR agents)'
    tail = f'since:{since} -filter:replies'
    return {'search-week-agents': f'{stack} {agents} min_faves:100 {tail}', 'search-week-craft': f'{stack} min_faves:500 {tail}'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--roots', nargs='+', default=['~'])
    ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch', 'week-context.json'))
    a = ap.parse_args()
    by = {}
    for repo in repos(a.roots):
        files = touched(repo, a.days)
        for f in scan(files):
            by.setdefault(f, []).append(os.path.basename(repo))
    if not by:
        sys.exit(f'no feature found in files changed over the last {a.days} days under {a.roots}')
    ranked = sorted(by, key=lambda f: (-len(by[f]), f))
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    ctx = {'days': a.days, 'made': dt.date.today().isoformat(),
           'features': {f: {'repos': sorted(by[f]), 'words': FEATURES[f][1]} for f in ranked},
           'searches': searches(ranked[:8], since)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(ctx, open(a.out, 'w'), indent=1)
    for f in ranked:
        print(f'{f:15} {len(by[f]):2} repos  {", ".join(sorted(by[f]))}')
    for k, v in ctx['searches'].items():
        print(f'{k}: {v}')
    print(a.out)


if __name__ == '__main__':
    main()
