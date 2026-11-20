#!/usr/bin/env python3
"""Where Claude Code tokens go, measured from session transcripts (~/.claude/projects/*/*.jsonl).

  usage.py                      sessions of the last 30 days: calls, output, cache write, cache read, hours, list cost
  usage.py --calls              plus the context re-read per call (median, quartiles) and the share above --cap
  usage.py --session ID         one session split by user turn (the cost of each task in it)
  usage.py --match WORD         only sessions whose first message or folder contains WORD
  usage.py --since 2026-10-01   only sessions that started on or after this date
  usage.py --cap 150000         the context size a handoff would hold calls under (default 150000)
  usage.py --prices FILE.json   {"model-prefix": {"input": 4, "output": 20, "cache_read": 0.2}, ...} per million tokens

Default prices are the list prices of 2026-10-06 (the claude-api skill's table); check that table before quoting a cost.
Cache writes are priced at 1.25x input (5-minute TTL)."""
import argparse, datetime as dt, glob, json, os, sys

PRICES = {"claude-opus-5": {"input": 4, "output": 20, "cache_read": 0.2},
          "claude-sonnet-5": {"input": 2, "output": 10, "cache_read": 0.2},
          "claude-haiku-5": {"input": 0.1, "output": 0.5, "cache_read": 0.01},
          "claude-fable-5": {"input": 10, "output": 50, "cache_read": 0.25}}


def price(model, prices):
    return next((v for k, v in prices.items() if str(model).startswith(k)), None)


def cost(u, p):
    if not p:
        return 0.0
    return (u.get("output_tokens", 0) * p["output"] + u.get("input_tokens", 0) * p["input"]
            + u.get("cache_creation_input_tokens", 0) * p["input"] * 1.25 + u.get("cache_read_input_tokens", 0) * p["cache_read"]) / 1e6


def read(path):
    for line in open(path, errors="ignore"):
        try:
            yield json.loads(line)
        except ValueError:
            continue


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--since", default=(dt.date.today() - dt.timedelta(days=30)).isoformat())
    ap.add_argument("--match")
    ap.add_argument("--session")
    ap.add_argument("--calls", action="store_true")
    ap.add_argument("--cap", type=int, default=150000)
    ap.add_argument("--prices")
    a = ap.parse_args()
    prices = json.load(open(a.prices)) if a.prices else PRICES
    since = dt.datetime.fromisoformat(a.since).replace(tzinfo=dt.timezone.utc)
    paths = glob.glob(f"{a.projects}/*/*.jsonl")
    if not paths:
        sys.exit(f"no transcripts under {a.projects}")
    if a.session:
        paths = [p for p in paths if os.path.basename(p).startswith(a.session)]
    rows, ctxs, turns = [], [], []
    for p in paths:
        s = {"id": os.path.basename(p)[:8], "calls": 0, "out": 0, "cw": 0, "cr": 0, "usd": 0.0, "t0": None, "t1": None, "first": "", "models": {}, "ctx": []}
        cur = None
        for r in read(p):
            ts = r.get("timestamp")
            t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
            if t:
                s["t0"], s["t1"] = s["t0"] or t, t
            m = r.get("message") if isinstance(r.get("message"), dict) else {}
            if r.get("type") == "user" and isinstance(m.get("content"), str):
                if not s["first"]:
                    s["first"] = m["content"][:80].replace("\n", " ")
                if a.session and "<task-notification" not in m["content"][:40]:
                    cur = {"q": m["content"][-70:].replace("\n", " "), "t0": t, "t1": t, "calls": 0, "out": 0, "cr": 0, "usd": 0.0}
                    turns.append(cur)
            u = m.get("usage")
            if r.get("type") != "assistant" or not u or not str(m.get("model", "")).startswith("claude"):
                continue
            pr = price(m.get("model"), prices)
            c = cost(u, pr)
            s["calls"] += 1; s["out"] += u.get("output_tokens", 0); s["cw"] += u.get("cache_creation_input_tokens", 0)
            s["cr"] += u.get("cache_read_input_tokens", 0); s["usd"] += c
            s["models"][m["model"]] = s["models"].get(m["model"], 0) + 1
            s["ctx"].append((u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
                         u.get("cache_read_input_tokens", 0), (pr or {}).get("cache_read", 0)))
            if cur:
                cur["calls"] += 1; cur["out"] += u.get("output_tokens", 0); cur["cr"] += u.get("cache_read_input_tokens", 0)
                cur["usd"] += c; cur["t1"] = t
        if s["calls"] and s["t0"] and s["t0"] >= since and (not a.match or a.match.lower() in (s["first"] + p).lower()):
            rows.append(s)
            ctxs += s["ctx"]
    if a.session:
        for c in turns:
            mins = (c["t1"] - c["t0"]).total_seconds() / 60 if c["t0"] and c["t1"] else 0
            print(f"{mins:6.0f} min {c['calls']:5} calls {c['out'] / 1e3:7.0f}k out {c['cr'] / 1e6:7.1f}M read ${c['usd']:7.2f} | {c['q']}")
        return
    rows.sort(key=lambda s: s["t0"])
    print(f"{'start':11} {'id':8} {'model':16} {'calls':>6} {'out_k':>7} {'cw_M':>6} {'cr_M':>7} {'hours':>6} {'list $':>8}  first message")
    for s in rows:
        model = max(s["models"], key=s["models"].get)
        print(f"{s['t0']:%m-%d %H:%M} {s['id']} {model[:16]:16} {s['calls']:6} {s['out'] / 1e3:7.0f} {s['cw'] / 1e6:6.1f} {s['cr'] / 1e6:7.0f} "
              f"{(s['t1'] - s['t0']).total_seconds() / 3600:6.1f} {s['usd']:8.0f}  {s['first'][:48]}")
    T = {k: sum(s[k] for s in rows) for k in ("calls", "out", "cw", "cr", "usd")}
    print(f"TOTAL {len(rows)} sessions: {T['calls']} calls, {T['out'] / 1e6:.1f}M output, {T['cw'] / 1e6:.0f}M cache write, "
          f"{T['cr'] / 1e9:.2f}B cache read, ${T['usd']:,.0f} at list prices")
    if a.calls and ctxs:
        ctxs.sort()
        n, cr = len(ctxs), sum(c[1] for c in ctxs) or 1
        q = lambda f: ctxs[int(f * (n - 1))][0] / 1e3
        over = sum(max(c[1] - a.cap, 0) for c in ctxs)
        print(f"context re-read per call: median {q(.5):.0f}k, quartiles {q(.25):.0f}k to {q(.75):.0f}k, p90 {q(.9):.0f}k "
              f"({n} calls)")
        print(f"tokens re-read beyond {a.cap / 1e3:.0f}k: {over / cr:.0%} of all cache reads, "
              f"${sum(max(c[1] - a.cap, 0) * c[2] for c in ctxs) / 1e6:,.0f} at list prices: the most a handoff at that size saves")
        print(f"cache-read tokens per output token: {cr / max(T['out'], 1):.0f} ")


if __name__ == "__main__":
    main()
