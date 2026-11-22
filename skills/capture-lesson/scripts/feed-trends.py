#!/usr/bin/env python3
"""What is trending in agent practice this week, measured on posts read from the person's own X feeds and searches.

Usage: feed-trends.py FEED.json [FEED2.json ...] [--labels LABELS.json] [--context WEEK.json] [--days 7] [--top 40]
       [--top-week 15] [--out ~/.claude/skills-watch]
Each FEED.json is a list of posts you saved yourself, for example from your own browser (id, author, time, text, card, links, replies,
reposts, likes, bookmarks, views, feeds). Run it twice a week-pass:
  1. without --labels: writes OUT/trends-<date>.md with the funnel, a drift gauge and the top posts (one per author),
     and OUT/trends-<date>.candidates.json for a model to label;
  2. with --labels (a JSON map post id -> "theme | covering skill", the skill being the local skill that already
     holds the practice or "none", or "skip" for posts off practice): adds the theme table,
     counted here in code, and remembers it in OUT/trends-state.json so next week can say new, rising or fading.

  Gate     on topic: two or more agent-practice words (practice-watch.TOPIC), or one in a topic feed or search
  Post     save rate = bookmarks / views: people keep what they will use, so it tracks practice better than likes;
           ranked by the rate smoothed toward the median (--prior-views), so small accounts can rank and a few lucky
           saves cannot; posts asking to be saved ("save this", a bookmark emoji) are dropped
  Check    --check SECOND.json: a second labeller's map on the same candidates; the report gives agreement, kappa
           and every post the two split on (2026-11-21: 80% keep/skip, kappa 0.58, covering skill 11 of 20)
  Theme    distinct authors per label: ten people posting the same repo list is one theme with ten authors, and
           the theme gets one post to read, not ten
  Covered  the local skill the labeller says already holds the practice; "none" marks a gap (a word match was
           tried and dropped 2026-11-21: generic words matched 20+ skills for every theme)
  Drift    each feed's on-topic share; a For You share that falls week on week means the algorithm moved, not the field
  Week     --context (week-context.py's JSON, read from skills-watch by default): a second lane for posts about the stack the
           person's repos used this week; a post enters on one stack word plus an agent word, two stack features, or
           one from a search-week feed, and the lane gets its own --top-week places, one per author
"""
import argparse, collections, datetime as dt, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessonlib import CONFIG
pw = __import__('practice-watch')
TOPIC, SOURCE, HYPE = pw.TOPIC, pw.SOURCE, pw.HYPE
TOPIC_FEEDS = {'llms', 'langchain'}
# a post that asks to be saved inflates its own save rate, so it cannot rank by it (2026-11-21: 3 of 40 candidates)
BAIT = re.compile(r"save this|bookmark (this|it)|🔖|save for later|you'?ll thank me|don'?t miss this", re.I)
WORD = re.compile(r"[a-z][a-z0-9+#.\-]{1,30}")
STOP = set('the a an and or of to in on for with is are be it this that you your how what why'.split())


def when(p):
    return dt.datetime.fromisoformat(p['time'].replace('Z', '+00:00'))


def on_topic(p):
    ws = set(WORD.findall((p['text'] + ' ' + p.get('card', '')).lower()))
    hits = len(ws & TOPIC)
    # a search result needs one topic word too, so the drift gauge measures the search instead of passing it whole
    in_topic_feed = bool(TOPIC_FEEDS & set(p['feeds'])) or any(f.startswith('search') for f in p['feeds'])
    return hits >= 2 or (hits >= 1 and in_topic_feed)


def agreement(cands, first, second):
    """Keep/skip agreement and Cohen's kappa between two labellers, and the covering-skill match on posts both kept."""
    keep = lambda L, i: L.get(i, 'skip') != 'skip'
    cover = lambda L, i: L.get(i, 'skip').partition('|')[2].strip()
    ids = [p['id'] for p in cands]
    n = len(ids) or 1
    same = sum(keep(first, i) == keep(second, i) for i in ids) / n
    k1, k2 = sum(keep(first, i) for i in ids) / n, sum(keep(second, i) for i in ids) / n
    chance = k1 * k2 + (1 - k1) * (1 - k2)
    kappa = (same - chance) / (1 - chance) if chance < 1 else 1.0
    both = [i for i in ids if keep(first, i) and keep(second, i)]
    covered = sum(cover(second, i) in cover(first, i) or cover(first, i) in cover(second, i) for i in both)
    split = [p for p in cands if keep(first, p['id']) != keep(second, p['id'])
             or (p['id'] in both and cover(second, p['id']) not in cover(first, p['id']))]
    return same, kappa, covered, len(both), split


def fit(p, ctx):
    """Features of this week's stack the post names (word boundaries, so 'ui' does not match 'build')."""
    text = (p['text'] + ' ' + p.get('card', '')).lower()
    return [f for f, v in ctx.get('features', {}).items()
            if any(re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', text) for w in v['words'])]


def in_week(p):
    hits = len(set(WORD.findall((p['text'] + ' ' + p.get('card', '')).lower())) & TOPIC)
    return bool(p['fit']) and (hits >= 1 or len(p['fit']) >= 2 or any(f.startswith('search-week') for f in p['feeds']))


def load(paths):
    seen = {}
    for path in paths:
        for p in json.load(open(path)):
            if p['id'] in seen:
                seen[p['id']]['feeds'] += [f for f in p['feeds'] if f not in seen[p['id']]['feeds']]
            else:
                seen[p['id']] = p
    return list(seen.values())


def score(pool, a):
    """Save rate pulled toward the median by prior_views of evidence: a small account's real signal still ranks, where
    the old 3,000-view floor dropped it, and a few lucky saves on few views do not top the list. Returns the median."""
    for p in pool:
        p['save'] = p['bookmarks'] / p['views'] if p['views'] else 0.0
        p['source'] = bool(SOURCE.search(' '.join([p['text'], p.get('card', '')] + p['links'])) or p.get('article'))
        p['hype'] = bool(HYPE.search(p['text']))
        p['bait'] = bool(BAIT.search(p['text']))
    scored = [p for p in pool if p['views'] >= a.min_views]
    rates = sorted(p['save'] for p in scored) or [0.0]
    prior = rates[len(rates) // 2]
    for p in pool:
        p['score'] = (p['bookmarks'] + prior * a.prior_views) / (p['views'] + a.prior_views) if p in scored else 0.0
    return prior


def pick(pool, top, seen, lane):
    """The best-scored posts, one per author not already in seen, bait left out."""
    out = []
    for p in sorted(pool, key=lambda p: -p['score']):
        if len(out) < top and p['author'] not in seen and p['score'] > 0 and not p['bait']:
            seen.add(p['author'])
            p['lane'] = lane
            out.append(p)
    return out


def link(p):
    return f'[@{p["author"]}](https://x.com/{p["author"]}/status/{p["id"]})'


def theme_table(cands, labels, out, today):
    """Theme rows counted in code, trend against the last saved week; the state file remembers this week."""
    state_path = os.path.join(out, 'trends-state.json')
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    last = state[max(k for k in state if k != today)] if any(k != today for k in state) else {}
    by, cover = collections.defaultdict(list), {}
    for p in cands:
        lab = labels.get(p['id'], 'skip')
        if lab != 'skip':
            t, _, c = (x.strip() for x in lab.partition('|'))
            by[t].append(p)
            cover[t] = c or '?'
    rows = []
    for t, ps in by.items():
        s = sorted(p['save'] for p in ps)
        pick_ = max(ps, key=lambda p: (not p['hype'], p['source'], p['save']))
        prev = last.get(t)
        trend = 'new' if prev is None else 'rising' if len(ps) > prev else 'steady' if len(ps) == prev else 'fading'
        rows.append((len(ps), s[len(s) // 2], t, cover[t], trend, pick_))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    state[today] = {r[2]: r[0] for r in rows}
    json.dump(state, open(state_path, 'w'), indent=1)
    L = ['| theme | authors | median save | covered by | trend | read this one |', '|---|---|---|---|---|---|']
    for n, med, t, cov, trend, p in rows:
        L.append(f'| {t} | {n} | {med:.1%} | {cov} | {trend} | {link(p)}{" [source]" * p["source"]}{" [hype]" * p["hype"]} |')
    skipped = sum(1 for p in cands if labels.get(p['id'], 'skip') == 'skip')
    return L + ['', f'Skipped as off-practice: {skipped} of {len(cands)}', '']


def check_table(cands, labels, second):
    same, kappa, covered, both, split = agreement(cands, labels, second)
    return ([f'Second labeller: keep/skip agree {same:.0%} (kappa {kappa:.2f}); same covering skill on '
             f'{covered} of {both} both kept. A theme whose posts split is a guess: read them before acting.', '',
             '| post | first | second |', '|---|---|---|']
            + [f'| {link(p)} | {labels.get(p["id"], "skip")} | {second.get(p["id"], "skip")} |' for p in split] + [''])


def candidate_lines(cands, start=1):
    L = []
    for i, p in enumerate(cands, start):
        txt = re.sub(r'\s+', ' ', p['text'])[:150]
        fits = f' [week: {", ".join(p["fit"])}]' if p.get('fit') else ''
        L.append(f'{i}. score {p["score"]:.1%} (saved {p["save"]:.1%} of {p["views"]:,} views), @{p["author"]}'
                 f'{" [source]" * p["source"]}{" [hype]" * p["hype"]}{fits}: '
                 f'{txt} (https://x.com/{p["author"]}/status/{p["id"]})')
    return L


def header(today, posts, recent, topical, week, cands, bait, prior, a, ctx, ctx_path):
    """Funnel, drift gauge per feed (on topic / on the week's stack) and the week context in one line each."""
    feeds = collections.Counter(f for p in recent for f in p['feeds'])
    hits = collections.Counter(f for p in topical for f in p['feeds'])
    whits = collections.Counter(f for p in week for f in p['feeds'])
    n_week = sum(p['lane'] == 'week' for p in cands)
    L = [f'# Feed trends {today}', '',
         f'Funnel: {len(posts)} posts read > {len(recent)} from the last {a.days} days > {len(topical)} on topic, '
         f'{len(week)} on this week\'s stack > {len(cands) - n_week} + {n_week} candidates (best smoothed save rate, '
         f'one per author, {a.min_views:,}+ views; {bait} asking to be saved dropped; median save {prior:.1%} weighted '
         f'as {a.prior_views:,} views)', '',
         'Drift gauge (share of each feed, last 7 days, on topic / on the week\'s stack): '
         + ', '.join(f'{f} {hits[f] / n:.0%} / {whits[f] / n:.0%} of {n}' for f, n in feeds.most_common()), '']
    if ctx:
        L += [f'Week context ({os.path.basename(ctx_path)}, made {ctx.get("made")}, last {ctx.get("days")} days of commits): '
              + ', '.join(f'{f} {len(v["repos"])}' for f, v in ctx['features'].items()), '']
    return L


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('feeds', nargs='+')
    ap.add_argument('--labels', help='JSON map post id -> theme (or "skip"), written by the model from candidates.json')
    ap.add_argument('--context', default=os.path.join(CONFIG, 'skills-watch', 'week-context.json'),
                    help="week-context.py's JSON, used when it exists (default: %(default)s)")
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--check', help='a second labeller\'s JSON on the same candidates: agreement and every split post')
    ap.add_argument('--min-views', type=int, default=500, help='floor before a post is scored at all (default: %(default)s)')
    ap.add_argument('--prior-views', type=int, default=3000,
                    help='weight of the median save rate in each score, in views (default: %(default)s)')
    ap.add_argument('--top', type=int, default=40, help='agent-practice candidates, one per author (default: %(default)s)')
    ap.add_argument('--top-week', type=int, default=15, help='week-lane candidates (default: %(default)s)')
    ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch'))
    a = ap.parse_args()
    for f in a.feeds:
        if not os.path.exists(f):
            sys.exit(f'no feed file at {f}: save a JSON list of posts first (fields in the docstring)')
    ctx_path = a.context
    ctx = json.load(open(ctx_path)) if os.path.exists(ctx_path) else {}

    posts = load(a.feeds)
    now = max(when(p) for p in posts)
    recent = [p for p in posts if when(p) >= now - dt.timedelta(days=a.days)]
    for p in recent:
        p['fit'] = fit(p, ctx)
    topical = [p for p in recent if on_topic(p)]
    week = [p for p in recent if in_week(p)]
    prior = score(list({p['id']: p for p in topical + week}.values()), a)
    seen = set()
    cands = pick(topical, a.top, seen, 'agents')
    cands += pick(week, a.top_week, seen, 'week')
    bait = sum(p['bait'] for p in topical + week if p['views'] >= a.min_views)

    today = dt.date.today().isoformat()
    os.makedirs(a.out, exist_ok=True)
    keep = ('id', 'author', 'text', 'card', 'views', 'bookmarks', 'save', 'score', 'source', 'hype', 'lane', 'fit')
    json.dump([{k: p.get(k) for k in keep} for p in cands], open(os.path.join(a.out, f'trends-{today}.candidates.json'), 'w'), indent=1)

    L = header(today, posts, recent, topical, week, cands, bait, prior, a, ctx, ctx_path)
    if a.labels:
        labels = json.load(open(a.labels))
        L += theme_table(cands, labels, a.out, today)
        if a.check:
            L += check_table(cands, labels, json.load(open(a.check)))
    agents = [p for p in cands if p['lane'] == 'agents']
    L += ['## Candidates: agent practice', ''] + candidate_lines(agents)
    L += ['', "## Candidates: this week's stack", ''] + candidate_lines([p for p in cands if p['lane'] == 'week'], len(agents) + 1)
    path = os.path.join(a.out, f'trends-{today}.md')
    open(path, 'w').write('\n'.join(L) + '\n')
    print(path)


if __name__ == '__main__':
    main()
