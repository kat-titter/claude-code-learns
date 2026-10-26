#!/bin/bash
# After a push to a static host (GitHub Pages and the like): wait until every listed file is served byte-identical to the
# local build, then check that private paths are NOT served. Cache-busting query strings keep a CDN copy from fooling it.
# Usage: verify-live.sh BASE_URL [--private PATH]... [--timeout SECONDS] LOCAL_FILE[=REMOTE_PATH]...
# Example: verify-live.sh https://user.github.io/deck index.html datum-line-deck.pdf --private private/judge-qa.html
set -u
BASE="${1%/}"; shift; PRIVATE=(); FILES=(); TIMEOUT=600
while [ $# -gt 0 ]; do case "$1" in
  --private) PRIVATE+=("$2"); shift 2;; --timeout) TIMEOUT="$2"; shift 2;; *) FILES+=("$1"); shift;; esac; done
hash() { shasum -a 256 | cut -c1-16; }
status=0; start=$(date +%s)
for spec in "${FILES[@]}"; do
  local_f="${spec%%=*}"; remote="${spec#*=}"; [ "$remote" = "$spec" ] && remote="$local_f"
  want=$(hash < "$local_f"); got=""; n=0
  while :; do
    n=$((n + 1)); got=$(curl -sL -H 'Cache-Control: no-cache' "$BASE/$remote?v=$(date +%s)$n" | hash)
    [ "$got" = "$want" ] && { echo "MATCH $remote after $(( $(date +%s) - start )) s"; break; }
    [ $(( $(date +%s) - start )) -ge "$TIMEOUT" ] && { echo "NO MATCH $remote (live $got, local $want)"; status=1; break; }
    sleep 15
  done
done
for p in "${PRIVATE[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$p")
  [ "$code" = "404" ] && echo "private $p: 404" || { echo "PRIVATE $p IS SERVED (HTTP $code)"; status=1; }
done
exit $status
