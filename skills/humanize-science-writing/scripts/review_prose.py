#!/usr/bin/env python3
"""Review long-form science prose for cohesion, legibility, argument and style signals.

Usage: python3 review_prose.py FILE [--captions] [--main] [--json]
FILE is HTML, Markdown or plain text. Prose comes from <p> and <li> (HTML) or paragraphs (text); scripts,
styles, SVG, code, tables and references are skipped. Add --captions to include figure captions, --main to skip
collapsed <details> sections (supplements), --json for machine-readable output.

Everything reported is a signal for a human or model to look at, not a verdict. A long sentence can be the
right sentence; a "cold" start can be a deliberate turn. The point is to look at the flagged lines.
Stdlib only.
"""
import html
import json
import re
import sys
from collections import Counter

STOP = set("""a about above after again against all also am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers herself him himself his how
i if in into is it its itself just me more most my myself no nor not now of off on once only or other our ours ourselves out over own
same she should so some such than that the their theirs them themselves then there these they this those through to too under until up
very was we were what when where which while who whom why will with would you your yours yourself yourselves one two three may might
must shall can't don't doesn't isn't it's i'm we're they're that's there's here's let's every each many much""".split())
CONNECT = re.compile(r"^(but|so|then|this|that|these|those|it|they|he|she|its|their|here|there|thus|hence|still|yet|now|instead|"
                     r"in turn|as a result|which|both|neither|next|first|second|third|finally|last|for example|for instance|"
                     r"likewise|similarly|however|meanwhile|again|also|and|or|because|if|when|once|after|before|"
                     r"the (?:first|second|third|last|next|other|same|two|three|rest)|even|so)\b", re.I)
HEDGE = re.compile(r"\b(may|might|could|possibly|perhaps|likely|suggests?|appears?|seems?|probably|potentially)\b", re.I)
OVERCLAIM = re.compile(r"\b(prove[sd]?|always|never|clearly|obviously|undeniabl\w*|definitely|certainly|revolutionar\w*|groundbreaking)\b", re.I)
# Signals from Wikipedia: Signs of AI writing (WikiProject AI Cleanup) and common chatbot leftovers. Signals, not bans.
AI_WORDS = re.compile(r"\b(delve\w*|tapestry|testament|pivotal|crucial|landscape|underscor\w*|showcas\w*|foster\w*|intricat\w*|"
                      r"vibrant|realm|navigat\w*|leverag\w*|seamless\w*|multifaceted|nuanced|meticulous\w*|embark\w*|"
                      r"boast\w*|nestled|enduring|interplay|holistic|transformative|game-?changer|unlock\w*|elevat\w*)\b", re.I)
ART = re.compile(r"(the|a|an)\s", re.I)   # an article as the first word
VERDICT = re.compile(r"^(that|this) is\b|^(the result|the answer|the catch|the point)\s*[?:]|^here'?s (the thing|why)|^it'?s worth noting|^in other words\b", re.I)   # verdict openers: once in a piece at most (2026-11-19)
NEG_PARALLEL = re.compile(r"\b(not (just|only|merely) .{1,60}?\bbut\b|it'?s not .{1,40}?, it'?s|isn'?t (just|about) .{1,40}?\bit'?s)", re.I)
# "One cell, nine addresses", "one tripeptide, two forms": a count-pair headline (a peptide explainer, 2026-11-05/06)
COUNT_PAIR = re.compile(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|twelve|a dozen|no) [\w-]+(?: [\w-]+)?, (?:one|two|three|four|five|six|seven|eight|nine|ten|twelve|a dozen|no) [\w-]+", re.I)
VAGUE_ATTR = re.compile(r"\b(experts (say|argue|agree|believe)|studies (show|suggest)|research (shows|suggests)|many (believe|argue)|"
                        r"some (say|argue)|it is (widely|generally) (known|accepted|believed))\b", re.I)
LEFTOVER = re.compile(r"(i hope this helps|certainly!|great question|as an ai|in conclusion|it'?s (important|worth) (to note|noting)|"
                      r"let'?s dive in|in today'?s (world|fast-paced)|without further ado)", re.I)
SIGNIFICANCE = re.compile(r"\b(stands? as|serves? as|a key (turning point|moment)|plays? a (vital|key|crucial|pivotal) role|"
                          r"highlighting (its|the) (importance|significance)|marking a)\b", re.I)


def extract(path, captions=False):
    raw = open(path, encoding='utf-8', errors='replace').read()
    if '<' in raw and re.search(r'</(p|li|div|section)>', raw):
        s = re.sub(r'<(script|style|svg|pre|code|table|math|nav|header|footer)\b.*?</\1>', ' ', raw, flags=re.S | re.I)
        s = re.sub(r'<ol class="refs".*?</ol>', ' ', s, flags=re.S | re.I)
        if not captions:
            s = re.sub(r'<figcaption\b.*?</figcaption>', ' ', s, flags=re.S | re.I)
        if SKIP_DETAILS:
            s = re.sub(r'<details\b.*?</details>', ' ', s, flags=re.S | re.I)
        bolds = [html.unescape(re.sub(r'<[^>]+>', '', b)).strip() for b in re.findall(r'<(?:b|strong)>(.*?)</(?:b|strong)>', s, flags=re.S)]
        paras = []
        for m in re.finditer(r'<(p|li)\b[^>]*>(.*?)</\1>', s, flags=re.S | re.I):
            t = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))
            t = re.sub(r'\s+', ' ', t).strip()
            t = re.sub(r'\s+([.,;:!?)\]’])', r'\1', re.sub(r'([(\[‘])\s+', r'\1', t))
            if len(t.split()) >= 4:
                paras.append(t)
        heads = [html.unescape(re.sub(r'<[^>]+>', '', h)).strip() for h in re.findall(r'<h[1-4]\b[^>]*>(.*?)</h[1-4]>', raw, flags=re.S)]
    else:
        s = re.sub(r'```.*?```', ' ', raw, flags=re.S)
        heads = [h.strip('# ').strip() for h in re.findall(r'^#{1,4} .*$', s, flags=re.M)]
        bolds = re.findall(r'\*\*(.+?)\*\*', s)
        paras = [re.sub(r'\s+', ' ', re.sub(r'[*_`>#]', '', p)).strip() for p in re.split(r'\n\s*\n', s)]
        paras = [p for p in paras if len(p.split()) >= 4 and not p.startswith('|')]
    return paras, heads, bolds


SKIP_DETAILS = False
ABBR = r'(?<!\b[A-Z])(?<!\be\.g)(?<!\bi\.e)(?<!\bet al)(?<!\bvs)(?<!\bFig)(?<!\bDr)(?<!\bSt)'


def sentences(p):
    parts = re.split(ABBR + r'(?<=[.?!])\s+(?=[A-Z0-9“"(\[])', p)
    return [x.strip() for x in parts if len(x.split()) >= 2]


def words(t):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", t)


def stem(w):
    w = w.lower().strip("'")
    for suf in ('ing', 'ed', 'es', 's', 'ly'):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def content(t):
    return {stem(w) for w in words(t) if w.lower() not in STOP and len(w) > 2}


def syllables(w):
    w = w.lower()
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups) - (1 if w.endswith('e') and len(groups) > 1 and not w.endswith('le') else 0)
    return max(1, n)


def short(t, n=18):
    ws = t.split()
    return ' '.join(ws[:n]) + (' ...' if len(ws) > n else '')


# Short forms: the convention in science writing is An Acronym (AA) at first use in prose, then AA. A gene,
# protein or receptor symbol (VEGFR2, AMPK, trkB, GLP-1R) is a name rather than an abbreviation and is never
# expanded in the literature, so symbols with a trailing digit or a lower-case run are left out of the count.
SYMBOLISH = re.compile(r'(^[A-Z]{1,4}[a-z]|[a-z]|\d$|R$|ase$)')


def short_forms(paras):
    """Every initialism in the prose, and whether its first use expanded it as 'Full phrase (ACR)'."""
    text = ' '.join(paras)
    seen, out = {}, {}
    for m in re.finditer(r'(?<![\w-])([A-Z][A-Za-z]*[A-Z][A-Za-z]*(?:-\d+|-[IVX]+)?)(?![\w-])', text):
        w = m.group(1)
        if len(w) < 2 or len(w) > 8 or SYMBOLISH.search(w.split('-')[0][1:] or 'x'):
            continue
        seen.setdefault(w, m.start())
    for w, i in seen.items():
        intro = re.search(r'\([^()]{0,4}%s[^()]{0,4}\)' % re.escape(w), text[max(0, i - 90):i + len(w) + 2])
        out[w] = bool(intro)
    return out


def review(path, captions=False):
    paras, heads, bolds = extract(path, captions)
    sents = [(i, s) for i, p in enumerate(paras) for s in sentences(p)]
    allw = [w for _, s in sents for w in words(s)]
    lens = [len(words(s)) for _, s in sents]
    n_s, n_w = len(sents), len(allw)
    if not n_s:
        return {'error': 'no prose found'}
    mean = sum(lens) / n_s
    sd = (sum((l - mean) ** 2 for l in lens) / n_s) ** 0.5
    syl = sum(syllables(w) for w in allw)
    long_words = sum(1 for w in allw if syllables(w) >= 3)
    fk = 0.39 * mean + 11.8 * syl / n_w - 15.59
    nomin = sum(1 for w in allw if re.search(r'(tion|ment|ance|ence|ity|ness)s?$', w.lower()) and len(w) > 6)
    passive = sum(len(re.findall(r'\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?\w+(ed|en)\b', s)) for _, s in sents)

    # cohesion: does each sentence pick up something from the one before (old information first)?
    cold, linked, pairs = [], 0, 0
    for (pi, a), (pj, b) in zip(sents, sents[1:]):
        if pi != pj:
            continue
        pairs += 1
        head = ' '.join(words(b)[:8])
        if content(a) & content(head) or CONNECT.match(b.strip('“"( ')) or content(a) & content(b):
            linked += 1
        else:
            cold.append(short(b))
    cold_paras = []
    for k in range(1, len(paras)):
        prev = ' '.join(sentences(paras[k - 1])[-2:])
        first = (sentences(paras[k]) or [''])[0]
        if not (content(prev) & content(first)) and not CONNECT.match(first.strip('“"( ')):
            cold_paras.append(short(first, 14))

    # legibility: terms bolded as definitions but used earlier
    text_seq = ' '.join(paras).lower()
    early = []
    for b in bolds:
        t = b.lower().strip(' .:')
        if 2 < len(t) < 30 and len(t.split()) <= 3:
            first_use = text_seq.find(t)
            bold_pos = text_seq.find(t, 0)
            if first_use >= 0 and text_seq.count(t) > 1:
                defs = [m.start() for m in re.finditer(re.escape(t), text_seq)]
                if defs and defs[0] < bold_pos:
                    early.append(t)
    longest = sorted(sents, key=lambda x: -len(words(x[1])))[:3]

    # argument: question up front, evidence beside claims, limits, an ending that answers the opening
    first_para = paras[0] if paras else ''
    hook = bool(re.search(r'\b(1[5-9]\d\d|20\d\d)\b|\b\d', first_para)) or bool(re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+', first_para[1:]))
    q_heads = sum(1 for h in heads if h.strip().endswith('?'))
    evid = sum(1 for _, s in sents if re.search(r'\[\d+|\d|https?://|doi', s))
    claims = sum(1 for _, s in sents if re.search(r'\b(is|are|was|were|shows?|finds?|found|means?|predicts?|explains?)\b', s))
    limits = any(re.search(r'\b(limit\w*|caveat\w*|cannot|can\'?t tell|uncertain\w*|weakness\w*|untested)\b', p, re.I) for p in paras)
    first = {}
    for w in words(paras[0]):
        first.setdefault(stem(w), w.lower())
    callback = sorted(first[x] for x in content(paras[0]) & content(' '.join(paras[-3:])))[:8] if len(paras) > 3 else []

    def hits(rx):
        out = []
        for _, s in sents:
            for m in rx.finditer(s):
                out.append(m.group(0).lower()[:40])
        return Counter(out)

    # X, Y and Z lists, skipping lists of names (authors) and clause joins like "table, as Ahnert and ..."
    triads = 0
    for _, s in sents:
        for m in re.finditer(r'\b(\w+(?: \w+)?), (\w+(?: \w+)?),? and (\w+)', s):
            items = m.groups()
            if all(x[:1].isupper() for x in items) or re.match(r'(as|which|so|but|while|when|where|who|because)\b', items[1]):
                continue
            triads += 1

    # rhythm: runs of four or more sentences within three words of each other's length
    flat, run = [], 1
    for a, b in zip(lens, lens[1:]):
        run = run + 1 if abs(a - b) <= 3 else 1
        if run == 4:
            flat.append(len(flat))
    # punctuation as voice: a mix is human; one mark doing all the work is a pattern
    marks = {'em dash': '\u2014', 'parenthesis': '(', 'colon': ':', 'semicolon': ';', 'question': '?'}
    punct = {k: round(100 * sum(s.count(c) for _, s in sents) / n_s, 1) for k, c in marks.items()}
    return {
        'file': path, 'paragraphs': len(paras), 'sentences': n_s, 'words': n_w, 'read_minutes': round(n_w / 230, 1),
        'legibility': {
            'mean_sentence_words': round(mean, 1), 'sentence_length_sd': round(sd, 1),
            'share_over_30_words': round(sum(1 for l in lens if l > 30) / n_s, 2),
            'fk_grade': round(fk, 1), 'share_long_words': round(long_words / n_w, 2),
            'nominalisations_per_100w': round(100 * nomin / n_w, 1), 'passives_per_100_sentences': round(100 * passive / n_s, 1),
            'flat_runs': len(flat), 'punctuation_per_100_sentences': punct,
            'longest': [f'{len(words(s))} words: {short(s, 16)}' for _, s in longest],
            'bold_terms_used_before_defined': early[:10]},
        'cohesion': {'linked_share': round(linked / pairs, 2) if pairs else None, 'cold_sentence_starts': cold[:12],
                     'cold_paragraph_starts': cold_paras[:12]},
        'argument': {'concrete_hook': hook, 'headings': len(heads), 'question_headings': q_heads,
                     'evidence_share': round(evid / n_s, 2), 'claim_share': round(claims / n_s, 2),
                     'hedges_per_100_sentences': round(100 * sum(hits(HEDGE).values()) / n_s, 1),
                     'overclaims': dict(hits(OVERCLAIM).most_common(8)), 'limits_stated': limits,
                     'callback_words_first_to_last': callback},
        'short_forms': short_forms(paras),
        'style_signals': {'ai_vocabulary': dict(hits(AI_WORDS).most_common(10)), 'negative_parallelism': dict(hits(NEG_PARALLEL)),
                          'vague_attribution': dict(hits(VAGUE_ATTR)), 'significance_inflation': dict(hits(SIGNIFICANCE)),
                          'chatbot_leftovers': dict(hits(LEFTOVER)), 'count_pairs': dict(hits(COUNT_PAIR)), 'verdict_openers': dict(Counter(m.group(0).lower() for _, s in sents for m in [VERDICT.match(s.strip())] if m)),
                          'x_y_and_z_lists_per_100_sentences': round(100 * triads / n_s, 1),
                          # sentences that open on an article, and back-to-back runs of them inside one paragraph
                          # (2026-11-20: "pet peeve starting sentences with article. use varied sentence structure")
                          'article_openers_share': round(sum(1 for _, x in sents if ART.match(x.strip())) / n_s, 2),
                          'article_opener_runs': sum(1 for (i, x), (j, y) in zip(sents, sents[1:])
                                                     if i == j and ART.match(x.strip()) and ART.match(y.strip()))},
    }


def report(r):
    if 'error' in r:
        return r['error']
    L, C, A, S = r['legibility'], r['cohesion'], r['argument'], r['style_signals']
    out = [f"# Prose review: {r['file']}", f"{r['words']} words, {r['sentences']} sentences, {r['paragraphs']} paragraphs, about {r['read_minutes']} min to read.", '',
           '## Legibility', f"Sentences average {L['mean_sentence_words']} words (spread {L['sentence_length_sd']}); {int(100 * L['share_over_30_words'])}% run over 30.",
           f"Grade level {L['fk_grade']}; {int(100 * L['share_long_words'])}% of words have three or more syllables; {L['nominalisations_per_100w']} nominalisations per 100 words; {L['passives_per_100_sentences']} passives per 100 sentences.",
           f"Rhythm: {L['flat_runs']} runs of four or more sentences of near-equal length. Punctuation per 100 sentences: "
           + ', '.join(f'{k} {v}' for k, v in L['punctuation_per_100_sentences'].items()) + '.',
           'Longest sentences:'] + [f'- {x}' for x in L['longest']]
    if L['bold_terms_used_before_defined']:
        out += ['Terms used before the sentence that defines them: ' + ', '.join(L['bold_terms_used_before_defined'])]
    out += ['', '## Cohesion', f"{int(100 * (C['linked_share'] or 0))}% of sentences pick up a word or connective from the sentence before.",
            'Cold sentence starts (nothing carried over; check each is a deliberate turn):'] + [f'- {x}' for x in C['cold_sentence_starts']]
    out += ['Cold paragraph starts:'] + [f'- {x}' for x in C['cold_paragraph_starts']]
    out += ['', '## Argument', f"Concrete hook in the first paragraph: {'yes' if A['concrete_hook'] else 'no'}. Headings: {A['headings']}, of which {A['question_headings']} are questions.",
            f"{int(100 * A['evidence_share'])}% of sentences carry evidence (a number, citation or link); hedges {A['hedges_per_100_sentences']} per 100 sentences.",
            f"Overclaim words: {A['overclaims'] or 'none'}. Limits stated: {'yes' if A['limits_stated'] else 'no'}.",
            f"Words shared by the opening and the ending (a callback): {', '.join(A['callback_words_first_to_last']) or 'none'}.",
            '', '## Short forms (An Acronym (AA), then AA)']
    F = r.get('short_forms', {})
    bare = [w for w, ok in F.items() if not ok]
    out += ['Expanded at first use in prose: ' + (', '.join(w for w, ok in F.items() if ok) or 'none'),
            'Never expanded: ' + (', '.join(bare) or 'none') +
            ('' if not bare else '  (a gene or receptor symbol needs none; anything else does)'),
            '', '## Style signals (look, do not ban)']
    for k, v in S.items():
        out.append(f"- {k.replace('_', ' ')}: {v if v else 'none'}")
    return '\n'.join(out)


if __name__ == '__main__':
    if sys.argv[1:2] in (['-h'], ['--help']):
        print(__doc__); sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    if not __import__('os').path.isfile(args[0]):
        sys.exit(f'no such file: {args[0]}')
    SKIP_DETAILS = '--main' in sys.argv
    res = review(args[0], captions='--captions' in sys.argv)
    print(json.dumps(res, indent=1) if '--json' in sys.argv else report(res))
