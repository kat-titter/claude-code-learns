#!/usr/bin/env python3
"""Skills that should have loaded and did not: for each recent session, every prompt that strongly matches a skill
(three or more rare trigger words, as skill-router.py uses) is checked against the skills that session loaded (a Skill
call or a read of the SKILL.md). Prints, per skill, how often a strong match loaded it, and a few missed prompts as
cases for that skill's trigger evals. The weekly watch runs it; the report stays on this machine.

Usage: trigger-misses.py [--sessions 60] [--examples 3]
"""
import argparse, json, os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG, match_skills, session_transcripts, skill_index, user_prompts

ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--sessions', type=int, default=60, help='most recent session transcripts to read (default 60)')
ap.add_argument('--examples', type=int, default=3, help='missed prompts shown per skill (default 3)')
a = ap.parse_args()


def loaded(path):
    """Skills a session loaded: Skill tool calls, and reads of a SKILL.md."""
    out = set()
    try:
        for line in open(path, encoding='utf-8'):
            if '"tool_use"' not in line:
                continue
            for b in (json.loads(line).get('message') or {}).get('content') or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    inp = b.get('input') or {}
                    if b.get('name') == 'Skill' and inp.get('skill'):
                        out.add(inp['skill'].split(':')[-1])
                    m = re.search(r'/skills/([\w-]+)/SKILL\.md', str(inp.get('file_path', '')) + str(inp.get('command', '')))
                    if m:
                        out.add(m.group(1))
    except (OSError, ValueError):
        pass
    return out


paths = session_transcripts(a.sessions)
if not paths:
    sys.exit(f'no session transcripts under {CONFIG}/projects yet')
index = skill_index()
matched, hit, missed = defaultdict(int), defaultdict(int), defaultdict(list)
for p in paths:
    have = None
    for prompt in user_prompts(p):
        for _, skill, ws in match_skills(prompt, index)[:1]:
            if skill.endswith('-style'):
                continue
            have = loaded(p) if have is None else have
            matched[skill] += 1
            if skill in have:
                hit[skill] += 1
            else:
                missed[skill].append((ws, re.sub(r'\s+', ' ', prompt)[:90]))

print(f'# Trigger misses: {len(paths)} sessions, prompts that strongly match a skill\n')
if not matched:
    print('No strong matches: nothing to report.')
for skill in sorted(matched, key=lambda s: (-(matched[s] - hit[s]), s)):
    print(f'- `{skill}`: loaded for {hit[skill]} of {matched[skill]} strong matches')
    for ws, text in missed[skill][:a.examples]:
        print(f'    - missed ({", ".join(ws[:4])}): "{text}"')
