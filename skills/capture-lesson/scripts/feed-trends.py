#!/usr/bin/env python3
"""What is trending in agent practice this week, measured on posts read from the person's own X feeds and searches.

Usage: feed-trends.py FEED.json [FEED2.json ...] [--labels LABELS.json] [--days 7] [--top 40] [--out ~/.claude/skills-watch]
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


def load(paths):
    seen = {}
    for path in paths:
        for p in json.load(open(path)):
            if p['id'] in seen:
                seen[p['id']]['feeds'] += [f for f in p['feeds'] if f not in seen[p['id']]['feeds']]
            else:
                seen[p['id']] = p
    return list(seen.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('feeds', nargs='+')
    ap.add_argument('--labels', help='JSON map post id -> theme (or "skip"), written by the model from candidates.json')
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--check', help='a second labeller\'s JSON on the same candidates: agreement and every split post')
    ap.add_argument('--min-views', type=int, default=500, help='floor before a post is scored at all (default: %(default)s)')
    ap.add_argument('--prior-views', type=int, default=3000,
                    help='weight of the median save rate in each score, in views (default: %(default)s)')
    ap.add_argument('--top', type=int, default=40, help='candidates, one per author (default: %(default)s)')
    ap.add_argument('--out', default=os.path.join(CONFIG, 'skills-watch'))
    a = ap.parse_args()
    for f in a.feeds:
        if not os.path.exists(f):
            sys.exit(f'no feed file at {f}: save a JSON list of posts first (fields in the docstring)')

    posts = load(a.feeds)
    now = max(when(p) for p in posts)
    recent = [p for p in posts if when(p) >= now - dt.timedelta(days=a.days)]
    topical = [p for p in recent if on_topic(p)]
    for p in topical:
        p['save'] = p['bookmarks'] / p['views'] if p['views'] else 0.0
        p['source'] = bool(SOURCE.search(' '.join([p['text'], p.get('card', '')] + p['links'])) or p.get('article'))
        p['hype'] = bool(HYPE.search(p['text']))
        p['bait'] = bool(BAIT.search(p['text']))
    # score = save rate pulled toward the median by prior_views of evidence: a small account's real signal still ranks,
    # where the old 3,000-view floor dropped it, and a few lucky saves on few views do not top the list
    scored = [p for p in topical if p['views'] >= a.min_views]
    rates = sorted(p['save'] for p in scored) or [0.0]
    prior = rates[len(rates) // 2]
    for p in topical:
        p['score'] = (p['bookmarks'] + prior * a.prior_views) / (p['views'] + a.prior_views) if p in scored else 0.0
    seen, cands = set(), []
    for p in sorted(topical, key=lambda p: -p['score']):
        if p['author'] not in seen and p['score'] > 0 and not p['bait']:
            seen.add(p['author'])
            cands.append(p)
    cands = cands[:a.top]
    bait = sum(p['bait'] for p in scored)

    today = dt.date.today().isoformat()
    os.makedirs(a.out, exist_ok=True)
    keep = ('id', 'author', 'text', 'card', 'views', 'bookmarks', 'save', 'score', 'source', 'hype')
    json.dump([{k: p.get(k) for k in keep} for p in cands], open(os.path.join(a.out, f'trends-{today}.candidates.json'), 'w'), indent=1)

    feeds = collections.Counter(f for p in recent for f in p['feeds'])
    hits = collections.Counter(f for p in topical for f in p['feeds'])
    L = [f'# Feed trends {today}', '',
         f'Funnel: {len(posts)} posts read > {len(recent)} from the last {a.days} days > {len(topical)} on topic > '
         f'{len(cands)} candidates (best smoothed save rate, one per author, {a.min_views:,}+ views; '
         f'{bait} asking to be saved dropped; median save {prior:.1%} weighted as {a.prior_views:,} views)', '',
         'Drift gauge (on-topic share per feed, last 7 days): '
         + ', '.join(f'{f} {hits[f]}/{n} ({hits[f] / n:.0%})' for f, n in feeds.most_common()), '']

    if a.labels:
        labels = json.load(open(a.labels))
        state_path = os.path.join(a.out, 'trends-state.json')
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
            pick = max(ps, key=lambda p: (not p['hype'], p['source'], p['save']))
            prev = last.get(t)
            trend = 'new' if prev is None else 'rising' if len(ps) > prev else 'steady' if len(ps) == prev else 'fading'
            rows.append((len(ps), s[len(s) // 2], t, cover[t], trend, pick))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        state[today] = {r[2]: r[0] for r in rows}
        json.dump(state, open(state_path, 'w'), indent=1)
        L += ['| theme | authors | median save | covered by | trend | read this one |', '|---|---|---|---|---|---|']
        for n, med, t, cov, trend, p in rows:
            flag = ' [source]' * p['source'] + ' [hype]' * p['hype']
            L.append(f'| {t} | {n} | {med:.1%} | {cov} | {trend} | [@{p["author"]}](https://x.com/{p["author"]}/status/{p["id"]}){flag} |')
        L += ['', f'Skipped as off-practice: {sum(1 for p in cands if labels.get(p["id"], "skip") == "skip")} of {len(cands)}', '']
        if a.check:
            same, kappa, covered, both, split = agreement(cands, labels, json.load(open(a.check)))
            L += [f'Second labeller: keep/skip agree {same:.0%} (kappa {kappa:.2f}); same covering skill on '
                  f'{covered} of {both} both kept. A theme whose posts split is a guess: read them before acting.', '',
                  '| post | first | second |', '|---|---|---|']
            second = json.load(open(a.check))
            L += [f'| [@{p["author"]}](https://x.com/{p["author"]}/status/{p["id"]}) | {labels.get(p["id"], "skip")} | '
                  f'{second.get(p["id"], "skip")} |' for p in split]
            L.append('')

    L += ['## Candidates', '']
    for i, p in enumerate(cands, 1):
        txt = re.sub(r'\s+', ' ', p['text'])[:150]
        L.append(f'{i}. score {p["score"]:.1%} (saved {p["save"]:.1%} of {p["views"]:,} views), @{p["author"]}'
                 f'{" [source]" * p["source"]}{" [hype]" * p["hype"]}: '
                 f'{txt} (https://x.com/{p["author"]}/status/{p["id"]})')
    path = os.path.join(a.out, f'trends-{today}.md')
    open(path, 'w').write('\n'.join(L) + '\n')
    print(path)


if __name__ == '__main__':
    main()
