#!/usr/bin/env python3
"""Trigger evals: each skill's description at a baseline revision against the current one, via skill-creator's run_eval.py.

PROMPTS is JSON {skill: [[query, should_trigger], ...]}: three that should trigger and two near-misses from neighbouring
skills (format: ../trigger-prompts.example.json). Each skill runs from a scratch project whose settings turn the real
skill off and every hook off, so only the test copy is listed, nothing is written to <config>/commands, and eval prompts
never reach the lessons inbox or the usage log. The scratch project is removed afterwards (--keep leaves it).
REV is a commit in the skills folder's own git history; without --baseline only the current description runs.

Each query is a yes/no draw that varies from run to run, so one run cannot separate two descriptions: --runs defaults
to 3 (a query passes when it triggers in at least half its runs), and a difference of one query is noise.
Needs the skill-creator plugin, Python 3.10+ for run_eval.py (--python when this one is older), PyYAML, and the claude
CLI logged in (`claude auth status`). Exits 1 when any eval errored or --only names a skill not in PROMPTS.

Usage: trigger-evals.py PROMPTS [--baseline REV] [--runs 3] [--only a,b] [--out results.json] [--python PY3.10+] [--keep]
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG, SKILLS, read_frontmatter

# where skill-creator lives: the plugin cache, and the desktop app's skills plugin
RUN_EVAL = [os.path.join(CONFIG, 'plugins/cache/*/skill-creator/*/skills/skill-creator/scripts/run_eval.py'),
            os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/*/*/skills/skill-creator/scripts/run_eval.py')]


def find_run_eval():
    """The installed skill-creator's run_eval.py (installed_plugins.json first), else the newest copy found."""
    try:
        installed = json.load(open(os.path.join(CONFIG, 'plugins', 'installed_plugins.json'))).get('plugins') or {}
        for key, entries in installed.items():
            for e in entries if key.startswith('skill-creator@') else []:
                p = os.path.join(e.get('installPath', ''), 'skills', 'skill-creator', 'scripts', 'run_eval.py')
                if os.path.isfile(p):
                    return p
    except (OSError, ValueError, AttributeError):
        pass
    found = sorted((p for g in RUN_EVAL for p in glob.glob(g)), key=os.path.getmtime)
    return found[-1] if found else None


def description(path):
    """description (+ when_to_use) to test, and a note: '' when fine, why when the skill must be skipped."""
    try:
        fm, err = read_frontmatter(path)
    except ValueError:
        return '', 'SKILL.md is not UTF-8'
    if err and 'does not parse' in err:
        # older frontmatter with ": " in a plain value fails YAML, yet Claude Code still reads one-line fields
        fm_text = re.match(r'^---\n(.*?)\n---\n', open(path, encoding='utf-8').read(), re.S).group(1)
        fm = {k: (re.search(rf'(?m)^{k}:[ \t]*(.*)$', fm_text) or [None, ''])[1].strip().strip('"\'')
              for k in ('description', 'when_to_use')}
        if fm['description'] in ('', '>', '>-', '|', '|-'):
            return '', 'frontmatter does not parse as YAML and has no one-line description to fall back on'
    elif err:
        return '', err
    d = fm.get('description')
    if not isinstance(d, str) or not d.strip():
        return '', 'frontmatter has no description'
    w = fm.get('when_to_use')
    return d + ((' - ' + str(w)) if w else ''), ''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('prompts', help='JSON {skill: [[query, should_trigger], ...]}')
    ap.add_argument('--baseline', default='', help='a commit in the skills folder to test the old description from')
    ap.add_argument('--runs', type=int, default=3, help='runs per query (default: %(default)s; 1 cannot separate two descriptions)')
    ap.add_argument('--only', default='', help='comma-separated skills from PROMPTS to run')
    ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch', 'trigger-evals.json'), help='results file (default: %(default)s)')
    ap.add_argument('--python', default=sys.executable, help='Python 3.10+ to run run_eval.py with (default: this one)')
    ap.add_argument('--keep', action='store_true', help='keep the scratch project for debugging')
    a = ap.parse_args()

    # inputs first, so a typo is named before anything is checked or spent
    if not os.path.isfile(a.prompts):
        sys.exit(f'no such file: {a.prompts}')
    try:
        prompts = json.load(open(a.prompts, encoding='utf-8'))
        assert isinstance(prompts, dict) and all(isinstance(v, list) and all(
            isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and isinstance(x[1], bool) for x in v)
            for v in prompts.values())
    except (ValueError, AssertionError):
        sys.exit(f'{a.prompts} is not {{skill: [[query, true|false], ...]}}: see trigger-prompts.example.json')
    only = set(filter(None, a.only.split(',')))
    if only - set(prompts):
        sys.exit(f"not in {a.prompts}: {', '.join(sorted(only - set(prompts)))}")
    if a.runs < 1:
        sys.exit('--runs must be 1 or more')
    if a.baseline and not shutil.which('git'):
        sys.exit('--baseline needs git on PATH')
    if a.baseline and subprocess.run(['git', '-C', SKILLS, 'rev-parse', '--verify', '--quiet', f'{a.baseline}^{{commit}}'],
                                     capture_output=True).returncode:
        sys.exit(f'--baseline {a.baseline} is not a commit in {SKILLS} (is the skills folder a git repo?)')

    # then what it depends on
    try:
        import yaml  # noqa: F401  (read_frontmatter reads block-style descriptions only with it)
    except ImportError:
        sys.exit('PyYAML missing: pip install pyyaml')
    run_eval = find_run_eval()
    if not run_eval:
        sys.exit(f"skill-creator's run_eval.py not found under {' or '.join(RUN_EVAL)}: run /plugin install skill-creator")
    if not shutil.which(a.python) and not os.path.isfile(a.python):
        sys.exit(f'no Python at {a.python}: pass --python /path/to/python3.11')
    if subprocess.run([a.python, '-c', 'import sys; sys.exit(sys.version_info < (3, 10))']).returncode:
        sys.exit(f'run_eval.py needs Python 3.10 or newer; {a.python} is older. Pass --python /path/to/python3.11')
    if not shutil.which('claude'):
        sys.exit('claude CLI not found on PATH: install Claude Code, then rerun.')
    try:
        auth = json.loads(subprocess.run(['claude', 'auth', 'status'], capture_output=True, text=True).stdout or '{}')
    except ValueError:
        auth = {}
    if not auth.get('loggedIn'):
        sys.exit('claude CLI is not logged in: run `claude /login` in a terminal, then rerun.')

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join(filter(None, [os.path.dirname(os.path.dirname(run_eval)),
                                                                     os.environ.get('PYTHONPATH')]))}   # run_eval imports scripts.utils
    work = tempfile.mkdtemp(prefix='trigger-evals-')
    results, errors = {}, 0
    try:
        for sk, items in prompts.items():
            if only and sk not in only:
                continue
            path = os.path.join(SKILLS, sk, 'SKILL.md')
            if not os.path.isfile(path):
                print(f'{sk:26} skipped: no {sk}/SKILL.md in {SKILLS}', flush=True); continue
            new, why = description(path)
            if why:
                print(f'{sk:26} skipped: {why}', flush=True); continue
            proj = os.path.join(work, sk); os.makedirs(os.path.join(proj, '.claude'), exist_ok=True)
            with open(os.path.join(proj, '.claude', 'settings.local.json'), 'w') as f:
                json.dump({'skillOverrides': {sk: 'off'}, 'disableAllHooks': True}, f)
            evalset = os.path.join(proj, 'evalset.json')
            with open(evalset, 'w') as f:
                json.dump([{'query': q, 'should_trigger': s} for q, s in items], f)
            variants = {'new': new}
            results[sk] = {}
            if a.baseline:
                old_src = subprocess.run(['git', '-C', SKILLS, 'show', f'{a.baseline}:./{sk}/SKILL.md'], capture_output=True, text=True)
                old_path = os.path.join(proj, 'baseline-SKILL.md')
                if old_src.returncode == 0:
                    with open(old_path, 'w', encoding='utf-8') as f:
                        f.write(old_src.stdout)
                    old, why = description(old_path)
                else:
                    why = (old_src.stderr.strip().splitlines() or ['git show failed'])[0]
                if old_src.returncode or why:
                    print(f'{sk:26} old no baseline ({why})', flush=True)
                    results[sk]['old'] = {'error': f'no baseline: {why}'}
                else:
                    variants['old'] = old
            for name, d in variants.items():
                r = subprocess.run([a.python, run_eval, '--eval-set', evalset, '--skill-path', os.path.join(SKILLS, sk),
                                    '--description', d, '--runs-per-query', str(a.runs), '--num-workers', '5'],
                                   cwd=proj, capture_output=True, text=True, env=env)
                try:
                    out = json.loads(r.stdout)
                except ValueError:
                    out = None
                if not isinstance(out, dict):
                    out = {'error': (r.stderr or r.stdout or f'exit code {r.returncode}')[-400:]}
                errors += 'error' in out
                results[sk][name] = out
                with open(a.out, 'w') as f:
                    json.dump(results, f, indent=1)
                s = out.get('summary', {})
                print(f"{sk:26} {name:3} passed {s.get('passed', '?')}/{s.get('total', '?')}" +
                      (f"  ERROR {out['error'][:120]}" if 'error' in out else ''), flush=True)
    finally:
        if a.keep:
            print(f'scratch project kept at {work}')
        else:
            shutil.rmtree(work, ignore_errors=True)
    if results:
        print(f'results: {a.out}')
    if errors:
        sys.exit(f'{errors} eval(s) errored')


if __name__ == '__main__':
    main()
