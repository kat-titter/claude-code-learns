#!/bin/sh
# The program checks every pull request runs (.github/workflows/checks.yml runs each as its own job).
#   sh tests/checks.sh                  run them all, print ok or FAIL per check, exit 1 if any failed
#   sh tests/checks.sh audit install    run some: python audit install watch check-repair mermaid
# Each check is a command that exits non-zero when something broke; nothing here asks a model. The mermaid check
# fetches @mermaid-js/mermaid-cli and a headless Chrome through npx the first time (about 200 MB).
ALL="python audit install watch check-repair mermaid"
S=skills/capture-lesson/scripts
MMDC=@mermaid-js/mermaid-cli@11.17.1
say() { printf '%s\n' "$*"; }
SELF=$(cd "$(dirname "$0")" && pwd)/checks.sh   # before the cd, so a relative $0 still finds it
cd "$(dirname "$0")/.." || exit 1

# count settings.json hook entries that run one of our scripts
our_hooks() { python3 -c 'import json,sys; h=json.load(open(sys.argv[1])).get("hooks",{}); print(sum("/scripts/" in json.dumps(e) for v in h.values() for e in v))' "$1"; }

one() {
  case "$1" in
  python)   # every script parses (Python compiles, shell passes bash -n), and the router's skill pick fires only
            # where no skill has loaded: tool definitions and a quoted mention do not count as a load
    python3 -m py_compile skills/*/scripts/*.py
    for f in skills/*/scripts/*.sh; do bash -n "$f"; done
    t=$(mktemp -d)
    printf '%s\n' '{"tools":[{"name":"Skill","description":"Invoke a skill"}]}' > "$t/defs.jsonl"
    printf '%s\n' '{"type":"user","message":{"content":[{"type":"text","text":"a regex: \"Base directory for this skill\""}]}}' > "$t/quoted.jsonl"
    printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"t1","name":"Skill","input":{"skill":"x"}}]}}' > "$t/called.jsonl"
    printf '%s\n' '{"type":"user","message":{"content":[{"type":"text","text":"Base directory for this skill: /x"}]}}' > "$t/typed.jsonl"
    got=
    for c in defs quoted called typed; do
      for q in 'make the readme better and check it all still holds up' continue; do
        o=$(printf '{"prompt": "%s", "transcript_path": "%s"}' "$q" "$t/$c.jsonl" | python3 "$S/skill-router.py")
        case "$o" in *'Skill pick'*) got="$got $c:${q%% *}" ;; esac
      done
    done
    [ "$got" = " defs:make quoted:make" ] || { say "skill pick fired for:$got (want: defs:make quoted:make)"; return 1; } ;;
  audit)    # the skill library passes its own audit with no flag at all
    python3 "$S/audit-skills.py" --strict skills ;;
  install)  # the installer parses, a dry run writes nothing, a real run installs, re-runs and undoes in a temp HOME
    sh -n install.sh
    h=$(mktemp -d)
    env -u CLAUDE_CONFIG_DIR HOME="$h" ./install.sh --name ci --dry-run
    [ -z "$(ls -A "$h")" ] || { say "the dry run wrote files:"; ls -A "$h"; return 1; }
    env -u CLAUDE_CONFIG_DIR HOME="$h" ./install.sh --name ci >/dev/null
    n=$(our_hooks "$h/.claude/settings.json"); [ "$n" = 6 ] || { say "install added $n hooks, want 6"; return 1; }
    o=$(env -u CLAUDE_CONFIG_DIR HOME="$h" ./install.sh --name ci)   # in $(), so a failing re-run stops the check
    case "$o" in *'hooks: nothing to add'*) ;; *) say "a re-run added hooks again"; return 1 ;; esac
    env -u CLAUDE_CONFIG_DIR HOME="$h" ./install.sh --uninstall >/dev/null
    n=$(our_hooks "$h/.claude/settings.json"); [ "$n" = 0 ] || { say "uninstall left $n hooks"; return 1; }
    for s in capture-lesson prompt-practice; do [ ! -e "$h/.claude/skills/$s" ] || { say "uninstall left $s"; return 1; }; done ;;
  watch)    # the weekly scripts run: skills-watch writes its report offline, practice-watch answers --help
    h=$(mktemp -d)
    env -u CLAUDE_CONFIG_DIR HOME="$h" python3 "$S/skills-watch.py" --skills skills --out "$h/out" --upstream
    [ -s "$h/out/$(date +%Y-%m-%d).md" ] || { say "skills-watch wrote no report"; return 1; }
    env -u CLAUDE_CONFIG_DIR HOME="$h" python3 "$S/practice-watch.py" --help >/dev/null ;;
  check-repair)   # the Workflow template, run against stub agents
    node --version
    node tests/check-repair.test.mjs ;;
  mermaid)  # every Mermaid block in README.md and AGENTS.md renders; a block that fails to parse fails here
    out=$(mktemp -d)
    for f in README.md AGENTS.md; do
      want=$(grep -c '^```mermaid' "$f" || true)   # grep -c exits 1 on a count of 0
      [ "$want" -gt 0 ] || { say "$f: no Mermaid blocks"; continue; }
      npx -y "$MMDC" -p tests/puppeteer.json -q -i "$f" -o "$out/$f"
      got=$(ls "$out" | grep -c "^${f%.md}-[0-9]*\.svg$" || true)
      [ "$got" = "$want" ] || { say "$f: $want Mermaid blocks, $got rendered"; return 1; }
      say "$f: $got Mermaid block(s) rendered"
    done ;;
  *) say "unknown check: $1 (checks: $ALL)"; return 2 ;;
  esac
}

# each check runs in its own process so set -e holds inside it (an `if` or `||` around a function turns it off)
if [ "${1:-}" = --one ]; then
  set -e
  [ -z "${CI:-}" ] || set -x   # in CI, trace each command, so a check that stops silently names its last command
  one "$2"; exit
fi
[ $# -gt 0 ] || set -- $ALL
failed=
for c; do
  if sh "$SELF" --one "$c"; then say "ok    $c"; else say "FAIL  $c"; failed="$failed $c"; fi
done
[ -z "$failed" ] || { say "failed:$failed"; exit 1; }
