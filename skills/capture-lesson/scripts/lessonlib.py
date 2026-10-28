"""Shared helpers for the capture-lesson scripts: where the config lives, which skill is the person's style skill,
what counts as feedback, and how to read the person's own prompts from a transcript.

Import-safe: nothing runs on import (a hook that reads stdin at import time hangs whoever imports it).
"""
import json, os, re

# the Claude config folder this skill is installed in: <config>/skills/capture-lesson/scripts/<this file>
CONFIG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SKILLS = os.path.join(CONFIG, 'skills')


def style_skill(skills_dir=SKILLS):
    """The personal style skill: $CLAUDE_STYLE_SKILL, else the name install.sh saved in <config>/.style-skill, else the
    shortest <name>-style folder when every other *-style folder extends it, else my-style."""
    name = os.environ.get('CLAUDE_STYLE_SKILL')
    if name:
        return name
    try:                        # the name install.sh saved
        name = open(os.path.join(os.path.dirname(skills_dir), '.style-skill')).read().strip()
        if name and os.path.isdir(os.path.join(skills_dir, name)):
            return name
    except OSError:
        pass
    found = sorted((d for d in os.listdir(skills_dir) if d.endswith('-style')), key=len) if os.path.isdir(skills_dir) else []
    # one person's skill can have siblings (jo-style, jo-visual-house-style): the shortest is the style skill
    if found and all(d.startswith(found[0][:-len('style')]) for d in found):
        return found[0]
    return 'my-style'


# text the harness injects as a "user" turn: summaries, skill bodies, notifications, reminders, events
HARNESS = re.compile(
    r'This session is being continued|The user sent a new message while you were working|Base directory for this skill|'
    r'<task-notification>|<system-reminder>|<command-name>|<local-command-|<side-sessions-event>|<ci-monitor-event>|'
    r'^Background \(from the session|<agent-message |<cross-session-message |<scheduled-task |\[Subagent hand-back\]|\[SYSTEM NOTIFICATION|\[Request interrupted')

# feedback: a correction, a preference for next time, a style note, or surprise at a result.
# Measured on real prompts before changing (see SKILL.md §1); bare "don't", "never", "always", "instead" and
# "I want" fire on ordinary instructions, so they count only next to a feedback word.
FEEDBACK = re.compile(
    r"(that'?s (wrong|not (it|right|what))|\bnot (right|quite|what i)|\bincorrect\b|\byou (forgot|missed|ignored|keep)\b|"
    r"\bi meant\b|\bdoesn'?t work|\bisn'?t working|\bstill (wrong|broken|not)|\bshould (have|be|use|show|look)\b|"
    r"\bplease (no|don'?t|stop|always|never|keep|use)\b|\bi (prefer|like it when|hate|don'?t like)\b|\bprefer\b|"
    r"\bfeels? (off|stale|forced|salesy|boring|wrong|cramped|cluttered|heavy|flat|busy)|"
    r"\btoo (much|many|long|slow|small|big|dense|wordy)\b|"
    r"\bwhy (is|are|does|did) (it|this|that|the)\b|\btaking so long|seems? like a lot|"
    r"\b(don'?t|dont|doesn'?t|didn'?t|isn'?t|can'?t) (work|match|line up|make sense|connect|understand|get it|see it|"
    r"know what|look right|read)|\b(don'?t|dont) be\b|"
    r"\b(don'?t|dont|never|always) (do|use|add|put|say|make|show|hide|forget|ask|change|start|write)\b|"
    r"\bno more\b|\bremember (this|that)\b|\bfrom now on\b|\bnext time\b|\bin (each|every) (chat|session)\b|"
    r"^\s*(no|nope|wrong)\b)", re.I)


def read_hook_input(stream):
    """The hook's JSON input, or {} when there is none, it does not parse, or the session is a trigger eval (whose
    test prompts and test skills must not reach the inbox, the usage log or the router)."""
    try:
        raw = stream.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}
    if os.environ.get('SKILL_TRIGGER_EVAL') or 'trigger-evals' in str(data.get('cwd', '')):
        return {}
    return data


def user_prompts(path, tail_bytes=2_000_000):
    """The person's own prompts in a transcript (JSONL), oldest first, read from its last tail_bytes: typed turns and
    messages queued while Claude was working. Skips tool results, injected text (isMeta) and harness messages, which
    also arrive as "user" turns."""
    out = []
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - tail_bytes))
            if size > tail_bytes:
                f.readline()            # drop the partial first line
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                queued = obj.get('attachment') or {}
                if obj.get('type') == 'attachment' and queued.get('type') == 'queued_command':
                    content = queued.get('prompt', '') if queued.get('commandMode') == 'prompt' else ''
                elif obj.get('type') == 'user' and not obj.get('isMeta') and 'toolUseResult' not in obj:
                    content = (obj.get('message') or {}).get('content', '')
                else:
                    continue
                if isinstance(content, list):
                    content = ' '.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
                text = str(content).strip()
                if text and not HARNESS.search(text):
                    out.append(text)
    except OSError:
        pass
    return out


def read_frontmatter(path):
    """A SKILL.md's frontmatter as a dict, and an error line when it does not parse ({} and the reason).
    Uses PyYAML when installed, else a simple reader for one-line `key: value` fields."""
    try:
        text = open(path, encoding='utf-8').read()
    except OSError as e:
        return {}, f'unreadable: {e.strerror}'
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return {}, 'no frontmatter: the skill loads with no description'
    try:
        import yaml
    except ImportError:
        yaml = None
    if yaml:
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            return {}, f'frontmatter does not parse ({str(e).splitlines()[0]}): the skill loads with no description'
        return (fm, '') if isinstance(fm, dict) else ({}, 'frontmatter is not a mapping')
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(':')
        if sep and k.strip() and not k.startswith((' ', '\t')):
            fm[k.strip()] = v.strip().strip('"\'')
    return fm, ''


# --- skill matching: a rare-word index over each skill's description and when_to_use ---------------------------------
# A prompt that shares three or more rare words with one skill's trigger text names that skill (measured on one
# library of 29 skills and 1,657 prompts: such matches were the right skill about 9 times in 10, while the matched skill
# loaded on its own only about 1 time in 5).
STOP = set("""a an the and or but if then else of to in on for with by from at as is are was were be been being it its this
that these those there here what which who whom whose when where why how all any each every some no not only own same so
than too very can will just should now do does did done doing have has had having i me my we our you your he she they them
their his her us use used using before after one two first into out up down over under again more most other such about
via per vs like make makes made get gets go goes going want need needs also still even way ways thing things something
someone says say said asks ask asked whenever while within without onto don dont let lets work works working page pages run
runs never user users claude line lines section sections open main table apply list point people current week moment
local pass edit edits touch right version view path step steps built already next complete far longer file files data
real system different level row rows name names set web state confirm job expect wrap order good new show look see time
add call keep start end anything anyone person reader readers whoever others part parts kind form true short long small big
check checks fix fixes plain clear once later back across around place hold holds come comes give gives take takes find
finds read reads write writes skill skills""".split())
MIN_WORDS = 3               # rare words a prompt must share with a skill before it is named
INDEX = os.path.join(CONFIG, '.skill-index.json')


def stem(w):
    for suf in ('ings', 'ing', 'ies', 'ied', 'es', 'ed', 'ly', 's'):
        if suf == 'es' and not w.endswith(('ses', 'xes', 'zes', 'ches', 'shes')):
            continue
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)] + ('y' if suf in ('ies', 'ied') else '')
    return w


def words(text):
    out = set()
    for w in re.findall(r"[a-z][a-z0-9+#.-]*[a-z0-9]|[a-z]", text.lower().replace("'", '')):
        if len(w) > 2 and w not in STOP and stem(w) not in STOP:
            out.add(stem(w))
    return out


def session_transcripts(n):
    """The n most recent session transcripts, leaving out sessions run from a temp folder (trigger evals, where the
    skill under test is switched off on purpose)."""
    import glob
    real = [p for p in glob.glob(os.path.join(CONFIG, 'projects', '*', '*.jsonl'))
            if not re.match(r'-(private-)?(var-folders|tmp)', os.path.basename(os.path.dirname(p)))]
    return sorted(real, key=os.path.getmtime)[-n:]


def skill_index(skills_dir=SKILLS, transcripts=None):
    """{skill: {word: weight}} for words that name at most two skills. Cached in <config>/.skill-index.json and
    rebuilt when a SKILL.md changes; words in more than 15% of recent prompts are dropped (words typed everywhere)."""
    import glob, math
    paths = sorted(glob.glob(os.path.join(skills_dir, '*', 'SKILL.md')))
    stamp = max((os.path.getmtime(p) for p in paths), default=0)
    try:
        cached = json.load(open(INDEX))
        if cached.get('stamp') == stamp and cached.get('n') == len(paths):
            return cached['skills']
    except (OSError, ValueError):
        pass
    text = {}
    for p in paths:
        fm, err = read_frontmatter(p)
        if not err:
            text[os.path.basename(os.path.dirname(p))] = words(f"{fm.get('description', '')} {fm.get('when_to_use', '')}")
    df = {}
    for ws in text.values():
        for w in ws:
            df[w] = df.get(w, 0) + 1
    if transcripts is None:
        transcripts = session_transcripts(60)
    prompts = [words(p[:1500]) for t in transcripts for p in user_prompts(t, 500_000)]
    common = set()
    if len(prompts) >= 50:
        pdf = {}
        for ws in prompts:
            for w in ws:
                pdf[w] = pdf.get(w, 0) + 1
        common = {w for w, c in pdf.items() if c > 0.15 * len(prompts)}
    n = max(len(text), 1)
    index = {s: {w: round(math.log(n / df[w]), 3) for w in ws if df[w] <= 2 and w not in common} for s, ws in text.items()}
    try:
        tmp = INDEX + '.tmp'
        json.dump({'stamp': stamp, 'n': len(paths), 'skills': index}, open(tmp, 'w'))
        os.replace(tmp, INDEX)
    except OSError:
        pass
    return index


def match_skills(prompt, index, min_words=MIN_WORDS):
    """Skills whose rare trigger words the prompt shares, best first: [(score, skill, [words])], strong matches only."""
    ws = words(prompt[:1500])
    hits = []
    for skill, weights in index.items():
        shared = sorted(ws & set(weights), key=lambda w: -weights[w])
        if len(shared) >= min_words:
            hits.append((round(sum(weights[w] for w in shared), 1), skill, shared))
    return sorted(hits, reverse=True)
