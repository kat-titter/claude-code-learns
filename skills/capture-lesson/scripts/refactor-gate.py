#!/usr/bin/env python3
"""Refactor gate: keep an evidence-lane skill change only when a program says it cleared its flag and broke nothing.

The change sits uncommitted in the skills folder (or in commits after REV). Two checks, the free one first:
1. audit: audit-skills.py --strict --only SKILL on the library at REV and as it is now. Passes when no flag is new or
   larger (numbers are compared, quoted examples ignored) and, with --clears, no flag still contains FLAG, matched with
   numbers ignored ("aim for about 600" matches whatever the length was).
2. triggers: trigger-evals.py PROMPTS --baseline REV --runs N --only SKILL. Passes when the new description passes at
   least as many queries as the old one. It costs 2 descriptions x 5 queries x N runs `claude -p` calls (30 at
   --runs 3), so it runs only when the audit passed.
Exits 0 when both pass and 1 when either fails or cannot run, with the failing output above the last line.
SKILL is a skill that exists at REV: for a merge or split, the one that keeps its name. PROMPTS has the trigger-evals
format (../trigger-prompts.example.json); for a merge, give SKILL the merged skill's should-trigger queries too.

Usage: refactor-gate.py SKILL PROMPTS [--baseline REV] [--clears FLAG] [--runs 3] [--python PY3.10+]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lessonlib import SKILLS, style_skill


def flag_key(note):
    """A flag without its numbers and example, so it keeps its identity when only its count changes."""
    return re.sub(r'\d[\d,.]*%?', 'N', note.split(', e.g. ')[0].split(': "')[0])


def first_number(note):
    m = re.search(r'\d[\d,]*', note.split(', e.g. ')[0])
    return int(m.group().replace(',', '')) if m else 0


def audit(skills_dir, skill, personal):
    """{flag key: its number} for skill in that folder, and the audit's output."""
    r = subprocess.run([sys.executable, os.path.join(HERE, 'audit-skills.py'), skills_dir, '--strict', '--only', skill,
                        '--personal', personal], capture_output=True, text=True)
    if r.returncode and 'strict:' not in r.stderr:
        sys.exit(f'gate: FAIL, the audit could not run on {skills_dir}: {r.stderr.strip()}')
    notes = [l[4:] for l in r.stdout.splitlines() if l.startswith('  - ')]
    return {flag_key(n): first_number(n) for n in notes}, r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('skill', help='the skill the change touches')
    ap.add_argument('prompts', help='JSON {skill: [[query, should_trigger], ...]} with an entry for SKILL')
    ap.add_argument('--baseline', default='HEAD', help='the commit before the change (default: %(default)s)')
    ap.add_argument('--clears', default='', metavar='FLAG', help='a flag the change must clear, as the audit prints it')
    ap.add_argument('--runs', type=int, default=3, help='trigger-eval runs per query (default: %(default)s)')
    ap.add_argument('--python', default='', help='Python 3.10+ for run_eval.py, passed to trigger-evals.py')
    a = ap.parse_args()

    # inputs first, so a typo is named before anything is spent
    try:
        prompts = json.load(open(a.prompts, encoding='utf-8'))
    except (OSError, ValueError) as e:
        sys.exit(f'gate: FAIL, cannot read {a.prompts}: {e}')
    if a.skill not in prompts:
        sys.exit(f'gate: FAIL, {a.prompts} has no queries for {a.skill}')
    if subprocess.run(['git', '-C', SKILLS, 'rev-parse', '--verify', '--quiet', f'{a.baseline}^{{commit}}'],
                      capture_output=True).returncode:
        sys.exit(f'gate: FAIL, {a.baseline} is not a commit in {SKILLS} (is the skills folder a git repo?)')

    # 1. audit: the library at the baseline against the library now
    personal = style_skill(SKILLS)
    old_tree = tempfile.mkdtemp(prefix='refactor-gate-')
    try:
        tar = subprocess.run(['git', '-C', SKILLS, 'archive', a.baseline], capture_output=True, check=True).stdout
        subprocess.run(['tar', '-x', '-C', old_tree], input=tar, check=True)
        if not os.path.isfile(os.path.join(old_tree, a.skill, 'SKILL.md')):
            sys.exit(f'gate: FAIL, {a.skill} does not exist at {a.baseline}: gate the skill that keeps its name')
        before, _ = audit(old_tree, a.skill, personal)
    finally:
        shutil.rmtree(old_tree, ignore_errors=True)
    after, report = audit(SKILLS, a.skill, personal)
    cleared = sorted(set(before) - set(after))
    worse = sorted(k for k in after if k not in before or after[k] > before[k])
    still = sorted(k for k in after if a.clears and flag_key(a.clears) in k)
    print(f'audit {a.skill}: {len(before)} flag(s) at {a.baseline}, {len(after)} now')
    for k in cleared: print(f'  cleared  {k}')
    for k in worse: print(f'  new      {k}' if k not in before else f'  larger   {k} ({before[k]} -> {after[k]})')
    for k in still: print(f'  still    {k} (--clears)')
    if worse or still:
        print(report.rstrip())
        sys.exit('gate: FAIL at the audit: ' + ('a new or larger flag' if worse else f'"{a.clears}" did not clear') +
                 '; trigger evals not run')

    # 2. triggers: the old description against the new one on the same queries
    calls = 2 * len(prompts[a.skill]) * a.runs
    print(f'\ntriggers {a.skill}: old against new, {len(prompts[a.skill])} queries x {a.runs} runs = {calls} claude -p calls', flush=True)
    out = os.path.join(tempfile.mkdtemp(prefix='refactor-gate-'), 'trigger-evals.json')
    subprocess.run([sys.executable, os.path.join(HERE, 'trigger-evals.py'), a.prompts, '--baseline', a.baseline,
                    '--runs', str(a.runs), '--only', a.skill, '--out', out] + (['--python', a.python] if a.python else []))
    try:
        res = json.load(open(out))[a.skill]
    except (OSError, ValueError, KeyError):
        sys.exit('gate: FAIL, trigger evals wrote no result (output above)')
    old, new = (res.get(v) or {'error': 'no result'} for v in ('old', 'new'))
    errs = [f"{v}: {r['error'][:200]}" for v, r in (('old', old), ('new', new)) if 'error' in r]
    if errs:
        sys.exit('gate: FAIL, trigger evals errored: ' + '; '.join(errs))
    old, new = old['summary'], new['summary']
    print(f"triggers: old {old['passed']}/{old['total']}, new {new['passed']}/{new['total']}")
    if new['passed'] < old['passed']:
        sys.exit('gate: FAIL at the triggers: the new description passes fewer queries')
    print('gate: pass')


if __name__ == '__main__':
    main()
