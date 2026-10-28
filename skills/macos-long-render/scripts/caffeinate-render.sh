#!/usr/bin/env bash
# Run a long command without letting macOS sleep/idle-throttle it.
# Usage:  caffeinate-render.sh -- python3 long_job.py
#         caffeinate-render.sh -- ffmpeg -i in.mp4 -c:v libx264 out.mp4
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then sed -n '2,4s/^# \{0,1\}//p' "$0"; exit 0; fi
if [[ "${1:-}" == "--" ]]; then shift; fi
if [[ $# -eq 0 ]]; then
  echo "usage: caffeinate-render.sh -- <command...>" >&2
  exit 2
fi

command -v caffeinate >/dev/null || { echo "caffeinate not found: this wrapper is for macOS" >&2; exit 2; }
echo "[caffeinate-render] preventing sleep for: $*" >&2
exec caffeinate -dimsu "$@"
