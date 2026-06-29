#!/usr/bin/env bash
# Run a long command without letting macOS sleep/idle-throttle it.
# Usage:  caffeinate-render.sh -- python3 long_job.py
#         caffeinate-render.sh -- ffmpeg -i in.mp4 -c:v libx264 out.mp4
set -euo pipefail

if [[ "${1:-}" == "--" ]]; then shift; fi
if [[ $# -eq 0 ]]; then
  echo "usage: caffeinate-render.sh -- <command...>" >&2
  exit 2
fi

echo "[caffeinate-render] preventing sleep for: $*" >&2
exec caffeinate -dimsu "$@"
