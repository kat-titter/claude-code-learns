#!/bin/bash
# Print an HTML page (a deck, a doc) to PDF with headless Chrome, and wait until Chrome has really finished.
# Usage: print-pdf.sh IN.html|URL OUT.pdf [profile-dir] [virtual-time-ms]
# Give each print that runs in parallel its own profile dir: Chrome locks a profile, and a second print on the same one
# silently produces nothing. --virtual-time-budget lets fonts, images and CSS animations settle before printing.
set -u
IN="$1"; OUT="$2"; PROFILE="${3:-$(mktemp -d -t chromeprint)}"; VT="${4:-15000}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
case "$IN" in http*|file://*) URL="$IN";; /*) URL="file://$IN";; *) URL="file://$PWD/$IN";; esac
rm -f "$OUT.tmp"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --user-data-dir="$PROFILE" \
  --virtual-time-budget="$VT" --print-to-pdf="$OUT.tmp" "$URL" 2>/dev/null &
C=$!
for i in $(seq 1 180); do if [ -s "$OUT.tmp" ] && ! kill -0 $C 2>/dev/null; then break; fi; sleep 1; done
kill $C 2>/dev/null; sleep 1
if [ -s "$OUT.tmp" ]; then mv "$OUT.tmp" "$OUT"; echo "ok $OUT"; else echo "FAILED $OUT (no output in 180 s)" >&2; exit 1; fi
