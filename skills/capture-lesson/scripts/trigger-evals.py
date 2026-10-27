#!/usr/bin/env python3
"""Trigger evals: each skill's description at a baseline revision against the current one, via skill-creator's run_eval.py.

PROMPTS is JSON {skill: [[query, should_trigger], ...]}: three that should trigger and two near-misses from neighbouring
skills (format: ../trigger-prompts.example.json). Each skill runs from a scratch project whose settings turn the real
skill off, so only the test copy is listed and nothing is written to <config>/commands. Needs the skill-creator plugin
and the claude CLI logged in (`claude auth status`). REV is a commit in the skills folder's own git history; without
--baseline only the current description runs.

Usage: trigger-evals.py PROMPTS [--baseline REV] [--runs 1] [--only a,b] [--out results.json]
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import yaml
except ImportError:
    sys.exit("PyYAML missing: pip install pyyaml")
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SK = os.path.join(CONFIG, "skills")
found = sorted(glob.glob(os.path.join(CONFIG, "plugins/cache/*/skill-creator/*/skills/skill-creator/scripts/run_eval.py")), key=os.path.getmtime)
if not found:
    sys.exit("skill-creator's run_eval.py not found: install the skill-creator plugin")
RE = found[-1]
ap = argparse.ArgumentParser(); ap.add_argument("prompts"); ap.add_argument("--baseline", default="")
ap.add_argument("--runs", type=int, default=1); ap.add_argument("--only", default="")
ap.add_argument("--out", default=os.path.join(CONFIG, "skills-watch", "trigger-evals.json"))
a = ap.parse_args()
if not os.path.isfile(a.prompts):
    sys.exit(f"no such file: {a.prompts}")
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
WORK = tempfile.mkdtemp(prefix="trigger-evals-")
if not shutil.which("claude"):
    sys.exit("claude CLI not found on PATH: install Claude Code, then rerun.")
auth = json.loads(subprocess.run(["claude", "auth", "status"], capture_output=True, text=True).stdout or "{}")
if not auth.get("loggedIn"):
    sys.exit("claude CLI is not logged in: run `claude /login` in a terminal, then rerun.")
prompts = json.load(open(a.prompts))
only = set(filter(None, a.only.split(",")))


def desc(text):
    d = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))
    return d["description"] + ((" - " + d["when_to_use"]) if d.get("when_to_use") else "")


results = {}
for sk, items in prompts.items():
    if only and sk not in only:
        continue
    if not os.path.isfile(os.path.join(SK, sk, "SKILL.md")):
        print(f"{sk:26} skipped: no {sk}/SKILL.md in {SK}", flush=True); continue
    proj = os.path.join(WORK, sk); os.makedirs(os.path.join(proj, ".claude"), exist_ok=True)
    json.dump({"skillOverrides": {sk: "off"}}, open(os.path.join(proj, ".claude", "settings.local.json"), "w"))
    evalset = os.path.join(proj, "evalset.json")
    json.dump([{"query": q, "should_trigger": s} for q, s in items], open(evalset, "w"))
    new = desc(open(os.path.join(SK, sk, "SKILL.md")).read())
    variants = {"new": new}
    if a.baseline:
        old_src = subprocess.run(["git", "-C", SK, "show", f"{a.baseline}:{sk}/SKILL.md"], capture_output=True, text=True)
        if old_src.returncode == 0:
            variants["old"] = desc(old_src.stdout)
    results[sk] = {}
    for name, d in variants.items():
        r = subprocess.run([sys.executable, RE, "--eval-set", evalset, "--skill-path", os.path.join(SK, sk),
                            "--description", d, "--runs-per-query", str(a.runs), "--num-workers", "5"],
                           cwd=proj, capture_output=True, text=True)
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"error": (r.stderr or r.stdout)[-400:]}
        results[sk][name] = out
        json.dump(results, open(a.out, "w"), indent=1)
        s = out.get("summary", {})
        print(f"{sk:26} {name:3} passed {s.get('passed', '?')}/{s.get('total', '?')}" + (f"  ERROR {out['error'][:120]}" if "error" in out else ""), flush=True)
