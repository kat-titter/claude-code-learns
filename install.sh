#!/bin/sh
# Install claude-code-learns into your Claude Code config (~/.claude, or $CLAUDE_CONFIG_DIR).
#   ./install.sh --name yourname --dry-run     show what it would do
#   ./install.sh --name yourname               do it
#   ./install.sh --name yourname --examples    also copy the two example skills (citations, macos-long-render)
# Safe to re-run: capture-lesson and prompt-practice are refreshed, files you wrote are left alone, settings.json is
# backed up before the three hooks are merged in, and a hook that is already there is not added twice.
set -e
NAME=my; DRY=0; EXAMPLES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="$2"; shift ;;
    --dry-run) DRY=1 ;;
    --examples) EXAMPLES=1 ;;
    -h|--help) sed -n 2,7p "$0"; exit 0 ;;
    *) echo "unknown option: $1 (try --help)"; exit 1 ;;
  esac
  shift
done
HERE=$(cd "$(dirname "$0")" && pwd)
C="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
STYLE="$(printf '%s' "$NAME" | tr 'A-Z ' 'a-z-')-style"
say() { printf '%s\n' "$*"; }
run() { if [ "$DRY" = 1 ]; then say "  would run: $*"; else "$@"; fi; }

say "Installing into $C (personal style skill: $STYLE)"

# 1. the skill that writes skills, with its four scripts and the weekly prompt; the skill that turns prompts into briefs
for s in capture-lesson prompt-practice; do run mkdir -p "$C/skills/$s"; run cp -R "$HERE/skills/$s/." "$C/skills/$s/"; done
if [ "$EXAMPLES" = 1 ]; then
  for s in citations macos-long-render; do run mkdir -p "$C/skills/$s"; run cp -R "$HERE/skills/$s/." "$C/skills/$s/"; done
fi

# 2. your personal layer, only if you do not have one yet
if ls -d "$C/skills/"*-style >/dev/null 2>&1; then
  say "  keeping your style skill: $(ls -d "$C/skills/"*-style | xargs -n1 basename | tr '\n' ' ')"
else
  run mkdir -p "$C/skills/$STYLE"
  if [ "$DRY" = 1 ]; then say "  would write $C/skills/$STYLE/SKILL.md"; else
    sed "s/my-style/$STYLE/g" "$HERE/templates/my-style/SKILL.md" > "$C/skills/$STYLE/SKILL.md"; fi
fi

# 3. global instructions that route feedback, only if you have no CLAUDE.md yet
if [ -e "$C/CLAUDE.md" ]; then
  say "  you already have $C/CLAUDE.md: add the three sections from CLAUDE.example.md by hand"
elif [ "$DRY" = 1 ]; then say "  would write $C/CLAUDE.md"; else
  sed "s/my-style/$STYLE/g" "$HERE/CLAUDE.example.md" > "$C/CLAUDE.md"
fi

# 4. an empty fast store
if [ ! -e "$C/lessons-inbox.md" ]; then
  if [ "$DRY" = 1 ]; then say "  would write $C/lessons-inbox.md"; else
    sed -n '1,7p' "$HERE/lessons-inbox.example.md" > "$C/lessons-inbox.md"; fi
fi

# 5. a one-page index of the library, only if you have none yet
if [ ! -e "$C/coding-skills.md" ]; then
  if [ "$DRY" = 1 ]; then say "  would write $C/coding-skills.md"; else
    printf '# Skills index\n\n| Skill | What it is for |\n|---|---|\n| `capture-lesson` | Turn feedback into guidance; tend the library; weekly watch. |\n| `prompt-practice` | Turn every prompt into a brief: terse prompts rewritten, briefs and generator prompts written well. |\n| `%s` | My taste and way of working, kept apart from the general skills. |\n' "$STYLE" > "$C/coding-skills.md"
    [ "$EXAMPLES" = 1 ] && printf '| `citations` | Numbered references checked against the real source. |\n| `macos-long-render` | Keep long Mac jobs awake; tell idle from thermal slowdowns. |\n' >> "$C/coding-skills.md"; fi
fi

# 6. the three hooks, merged into settings.json
python3 - "$C/settings.json" "$C/skills" "$DRY" <<'PY'
import json, os, shutil, sys
path, skills, dry = sys.argv[1], sys.argv[2], sys.argv[3] == '1'
s = json.load(open(path)) if os.path.exists(path) else {}
hooks = s.setdefault('hooks', {})
want = [('UserPromptSubmit', 'capture-lesson', 'feedback-nudge.py'), ('Stop', 'capture-lesson', 'scan-corrections.py'),
        ('UserPromptSubmit', 'prompt-practice', 'prompt-nudge.py')]
added = []
for event, skill, script in want:
    have = json.dumps(hooks.get(event, []))
    if script in have:
        continue
    hooks.setdefault(event, []).append({'hooks': [{'type': 'command', 'command': f'python3 {skills}/{skill}/scripts/{script}'}]})
    added.append(f'{event} -> {script}')
if not added:
    print('  hooks already in place')
elif dry:
    print('  would add hooks: ' + ', '.join(added))
else:
    if os.path.exists(path):
        shutil.copy(path, path + '.bak')
    json.dump(s, open(path, 'w'), indent=2)
    print('  added hooks: ' + ', '.join(added) + (f' (backup: {path}.bak)' if os.path.exists(path + '.bak') else ''))
PY

say ""
say "Done. Two optional steps:"
say "  - Weekly watch: in the Claude desktop app, add a weekly scheduled task with the prompt in"
say "    $C/skills/capture-lesson/weekly-watch.md. Without the app, cron can run the script alone:"
say "    0 9 * * 1  python3 $C/skills/capture-lesson/scripts/skills-watch.py"
say "  - Check the library any time: python3 $C/skills/capture-lesson/scripts/audit-skills.py"
