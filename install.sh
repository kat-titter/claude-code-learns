#!/bin/sh
# Install claude-code-learns into your Claude Code config (~/.claude, or $CLAUDE_CONFIG_DIR).
#   ./install.sh --name yourname --dry-run     show what it would do, change nothing
#   ./install.sh --name yourname               do it
#   ./install.sh --name yourname --examples    also copy the example skills (citations, macos-long-render, html-docs, html-slide-deck)
#   ./install.sh --uninstall                   remove the hooks, the two skills and the CLAUDE.md section; keep your notes
# Safe to re-run: capture-lesson and prompt-practice are refreshed, files you wrote are left alone, settings.json and
# CLAUDE.md are backed up before any change, and a hook that is already there is not added twice.
set -e
NAME=my; DRY=0; EXAMPLES=0; UNINSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --name) case "${2:-}" in ''|-*) echo "--name needs a value, e.g. --name jo"; exit 1 ;; esac; NAME="$2"; shift ;;
    --dry-run) DRY=1 ;;
    --examples) EXAMPLES=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n 2,8p "$0"; exit 0 ;;
    *) echo "unknown option: $1 (try --help)"; exit 1 ;;
  esac
  shift
done
HERE=$(cd "$(dirname "$0")" && pwd)
C="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
STYLE="$(printf '%s' "$NAME" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-')-style"
STAMP=$(date +%Y%m%d-%H%M%S)
say() { printf '%s\n' "$*"; }
# copy a file to <file>.<time>.bak, never over an earlier backup; print the backup's path
backup() { b="$1.$STAMP.bak"; n=1; while [ -e "$b" ]; do b="$1.$STAMP-$n.bak"; n=$((n+1)); done; cp "$1" "$b"; printf '%s' "$b"; }
run() { if [ "$DRY" = 1 ]; then say "  would run: $*"; else "$@"; fi; }
command -v python3 >/dev/null || { say "python3 not found: the hooks need it. Install Python 3, then re-run."; exit 1; }
if [ -e "$C/settings.json" ] && ! python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); assert isinstance(s.get("hooks") or {}, dict)' "$C/settings.json" 2>/dev/null; then
  say "$C/settings.json is not valid JSON (or its hooks are not an object): fix it first; nothing was changed."; exit 1
fi

# settings.json: add (or, with --uninstall, remove) the hooks; back up first; print what changed
hooks() {
python3 - "$C/settings.json" "$C/skills" "$1" "$DRY" "$STAMP" <<'PY'
import json, os, shutil, sys
path, skills, mode, dry, stamp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1', sys.argv[5]
s = json.load(open(path)) if os.path.exists(path) else {}
hooks = s.setdefault('hooks', {})
# (event, matcher, skill, script). The usage log needs two events: PreToolUse sees the model's Skill calls,
# UserPromptExpansion sees a typed /name.
want = [('UserPromptSubmit', None, 'capture-lesson', 'feedback-nudge.py'),
        ('UserPromptSubmit', None, 'capture-lesson', 'skill-router.py'),
        ('UserPromptSubmit', None, 'prompt-practice', 'prompt-nudge.py'),
        ('Stop', None, 'capture-lesson', 'scan-corrections.py'),
        ('PreToolUse', 'Skill', 'capture-lesson', 'skill-usage-log.py'),
        ('UserPromptExpansion', None, 'capture-lesson', 'skill-usage-log.py')]
ours = lambda entry: any(f'{sk}/scripts/{sc}' in json.dumps(entry) for _, _, sk, sc in want)
changed = []
if mode == 'remove':
    for event in list(hooks):
        keep = [e for e in hooks[event] if not ours(e)]
        if len(keep) != len(hooks[event]):
            changed.append(event)
            hooks[event] = keep
        if not hooks[event]:
            del hooks[event]
    if not hooks:
        s.pop('hooks')
else:
    for event, matcher, skill, script in want:
        if f'{skill}/scripts/{script}' in json.dumps(hooks.get(event, [])):
            continue
        hook = {'type': 'command', 'command': f'python3 "{os.path.abspath(skills)}/{skill}/scripts/{script}"', 'timeout': 10}
        if event not in ('UserPromptSubmit',):
            hook['async'] = True        # loggers: nothing to say back, so the reply never waits on them
        entry = {'hooks': [hook]}
        if matcher:
            entry = {'matcher': matcher, **entry}
        hooks.setdefault(event, []).append(entry)
        changed.append(f'{event}{f"({matcher})" if matcher else ""} -> {script}')
verb, done = ('remove', 'removed') if mode == 'remove' else ('add', 'added')
if not changed:
    print('  hooks: nothing to ' + verb)
elif dry:
    print(f'  would {verb} hooks: ' + ', '.join(changed))
else:
    bak, n = f'{path}.{stamp}.bak', 1
    while os.path.exists(bak):
        bak, n = f'{path}.{stamp}-{n}.bak', n + 1
    if os.path.exists(path):
        shutil.copy(path, bak)
    with open(path, 'w') as f:
        json.dump(s, f, indent=2)
        f.write('\n')
    print(f'  {done} hooks: ' + ', '.join(changed) + (f' (backup: {bak})' if os.path.exists(bak) else ''))
PY
}

BEGIN='<!-- claude-code-learns: begin -->'; END='<!-- claude-code-learns: end -->'

if [ "$UNINSTALL" = 1 ]; then
  say "Uninstalling from $C"
  hooks remove
  for s in capture-lesson prompt-practice; do [ -d "$C/skills/$s" ] && run rm -r "$C/skills/$s"; done
  if [ -e "$C/CLAUDE.md" ] && grep -qF "$BEGIN" "$C/CLAUDE.md"; then
    if [ "$DRY" = 1 ]; then say "  would remove the claude-code-learns section from $C/CLAUDE.md (after a backup)"; else
      b=$(backup "$C/CLAUDE.md"); sed "/$BEGIN/,/$END/d" "$b" > "$C/CLAUDE.md"; say "  removed the claude-code-learns section from CLAUDE.md (backup: $b)"; fi
  fi
  say "Kept (yours): your *-style skill, lessons-inbox.md, skill-usage.log, coding-skills.md, memory, and any example skills."
  exit 0
fi

say "Installing into $C (personal style skill: $STYLE)"

# 1. the skill that writes skills, with its scripts and the weekly prompt; the skill that turns prompts into briefs.
# The loop may have written lessons into an installed copy, so a copy that differs is backed up (outside skills/,
# where it would load as a second skill) before the refresh.
SKILLS="capture-lesson prompt-practice"; [ "$EXAMPLES" = 1 ] && SKILLS="$SKILLS citations macos-long-render html-docs html-slide-deck"
for s in $SKILLS; do
  if [ -d "$C/skills/$s" ] && ! diff -rq "$HERE/skills/$s" "$C/skills/$s" >/dev/null 2>&1; then
    run mkdir -p "$C/backups/claude-code-learns-$STAMP"; run cp -R "$C/skills/$s" "$C/backups/claude-code-learns-$STAMP/"
    say "  $s: your copy differed; saved it to backups/claude-code-learns-$STAMP/$s (merge any lessons back by hand)"
  fi
  run mkdir -p "$C/skills/$s"; run cp -R "$HERE/skills/$s/." "$C/skills/$s/"
done
# the weekly prompt names the config folder; point it at this one
if [ "$DRY" = 0 ] && [ "$C" != "$HOME/.claude" ]; then
  sed "s|~/.claude|$C|g" "$HERE/skills/capture-lesson/weekly-watch.md" > "$C/skills/capture-lesson/weekly-watch.md"
fi

# 2. your personal layer, only if you do not have one yet
if ls -d "$C/skills/"*-style >/dev/null 2>&1; then
  for d in "$C/skills/"*-style; do say "  keeping your style skill: ${d##*/}"; done
else
  run mkdir -p "$C/skills/$STYLE"
  if [ "$DRY" = 1 ]; then say "  would write $C/skills/$STYLE/SKILL.md"; else
    sed "s/my-style/$STYLE/g" "$HERE/templates/my-style/SKILL.md" > "$C/skills/$STYLE/SKILL.md"
    printf '%s\n' "$STYLE" > "$C/.style-skill"; fi   # the scripts read this name, so an unrelated *-style skill is never mistaken for yours
fi

# 3. the routing habit in CLAUDE.md (loaded every session): a new file, or one marked section added to yours
if [ ! -e "$C/CLAUDE.md" ]; then
  if [ "$DRY" = 1 ]; then say "  would write $C/CLAUDE.md"; else
    sed "s/my-style/$STYLE/g" "$HERE/CLAUDE.example.md" > "$C/CLAUDE.md"; fi
elif grep -qF "$BEGIN" "$C/CLAUDE.md" || grep -q 'capture-lesson' "$C/CLAUDE.md"; then
  say "  CLAUDE.md already routes feedback: left as is"
elif [ "$DRY" = 1 ]; then say "  would add the 'Feedback becomes guidance' section to $C/CLAUDE.md (after a backup)"
else
  b=$(backup "$C/CLAUDE.md")
  { printf '\n%s\n' "$BEGIN"; sed -n '/^## Feedback becomes guidance/,$p' "$HERE/CLAUDE.example.md" | sed "s/my-style/$STYLE/g"; printf '%s\n' "$END"; } >> "$C/CLAUDE.md"
  say "  added the 'Feedback becomes guidance' section to CLAUDE.md (backup: $b)"
fi

# 4. an empty fast store: the example's header, without the example lines
if [ ! -e "$C/lessons-inbox.md" ]; then
  if [ "$DRY" = 1 ]; then say "  would write $C/lessons-inbox.md"; else
    sed '/^Format:/q' "$HERE/lessons-inbox.example.md" > "$C/lessons-inbox.md"; fi
fi

# 5. a one-page index of the library, only if you have none yet
if [ ! -e "$C/coding-skills.md" ]; then
  if [ "$DRY" = 1 ]; then say "  would write $C/coding-skills.md"; else
    printf '# Skills index\n\n| Skill | What it is for |\n|---|---|\n| `capture-lesson` | Turn feedback into guidance; tend the library; weekly watch. |\n| `prompt-practice` | Turn every prompt into a brief: terse prompts rewritten, briefs and generator prompts written well. |\n| `%s` | My taste and way of working, kept apart from the general skills. |\n' "$STYLE" > "$C/coding-skills.md"
  fi
fi
if [ "$EXAMPLES" = 1 ] && [ "$DRY" = 0 ]; then
  while IFS='|' read -r name what; do
    grep -qF "\`$name\`" "$C/coding-skills.md" || printf '| `%s` | %s |\n' "$name" "$what" >> "$C/coding-skills.md"
  done <<'ROWS'
citations|Numbered references checked against the real source.
macos-long-render|Keep long Mac jobs awake; tell idle from thermal slowdowns.
html-docs|One-file HTML docs with light interactivity; light-audit.py.
html-slide-deck|One-file HTML decks: views, layers, print, publish.
ROWS
fi

# 6. the hooks: feedback nudge, skill router and prompt nudge (each prompt), correction scan (after each reply),
#    usage log (each skill use)
hooks add

say ""
say "Done. Start a new session so the hooks and skills load. Then, optionally:"
say "  - Weekly watch: in the Claude desktop app, add a weekly scheduled task with the prompt in"
say "    $C/skills/capture-lesson/weekly-watch.md. Without the app, cron can run the script alone:"
say "    0 9 * * 1  python3 \"$C/skills/capture-lesson/scripts/skills-watch.py\""
say "  - Check the library any time: python3 \"$C/skills/capture-lesson/scripts/audit-skills.py\""
say "  - See which skills get used:  python3 \"$C/skills/capture-lesson/scripts/skill-usage-log.py\" --report"
say "  - See which skills missed:     python3 \"$C/skills/capture-lesson/scripts/trigger-misses.py\""
say "  - Undo everything: ./install.sh --uninstall"
