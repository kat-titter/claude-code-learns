#!/bin/bash
# Run a build twice and require byte-identical output. A build that edits its own source (passes that rewrite a stored
# HTML file, pattern-keyed fixes, generated boards) drifts silently; the second build is where that shows.
# Usage: stable-build.sh OUTPUT_FILE -- build command and args...
set -u
case "${1:-}" in -h|--help) sed -n '2,4s/^# \{0,1\}//p' "$0"; exit 0;; esac
[ $# -ge 2 ] || { echo "usage: stable-build.sh OUTPUT_FILE -- build command and args... (no build command given)" >&2; exit 2; }
OUT="$1"; shift; [ "$1" = "--" ] && shift
[ $# -ge 1 ] || { echo "stable-build.sh: no build command after --" >&2; exit 2; }
TMP=$(mktemp -t stable)
"$@" > /dev/null || { echo "build 1 failed" >&2; exit 2; }
cp "$OUT" "$TMP"
"$@" > /dev/null || { echo "build 2 failed" >&2; exit 2; }
if cmp -s "$OUT" "$TMP"; then echo "stable: two builds byte-identical ($(wc -c < "$OUT" | tr -d ' ') bytes)"; rm -f "$TMP"; exit 0; fi
python3 - "$TMP" "$OUT" <<'PY'
import sys, re
a, b = (open(p, encoding='utf-8', errors='replace').read() for p in sys.argv[1:3])
i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
clean = lambda s: re.sub(r'base64,[A-Za-z0-9+/=]{40,}', 'base64,...', s)
print(f'NOT stable: builds differ at character {i} (sizes {len(a)} and {len(b)})')
print('build 1:', clean(a[max(0, i - 200):i + 200]))
print('build 2:', clean(b[max(0, i - 200):i + 200]))
PY
exit 1
