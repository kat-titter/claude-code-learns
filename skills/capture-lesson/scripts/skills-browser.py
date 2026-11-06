#!/usr/bin/env python3
"""Draw a skills library as one self-contained page: hover a file to read it.

Every tracked file in the library's git repo: Markdown rendered (frontmatter as a card), scripts with line numbers,
SVGs as images (plain Markdown text if the `markdown` package is missing). Skill names inside a document link to that skill; a search box finds names and full text; each
skill shows its commits per day; files with uncommitted edits are marked. Needs Python 3 and git;
`python3 -m pip install markdown` renders the Markdown.

  python3 skills-browser.py                   # ~/.claude/skills -> ~/.claude/skills-browser/index.html
  python3 skills-browser.py --open            # and open it in the default browser
  python3 skills-browser.py --repo DIR --out FILE
"""
import argparse, base64, collections, html, json, pathlib, re, subprocess, webbrowser

try:
    import markdown
except ImportError:  # still a working page: Markdown shown as wrapped plain text
    markdown = None

HOME = pathlib.Path.home()
REPO = HOME / ".claude/skills"


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    meta, key = {}, None
    for line in text[4:end].splitlines():
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            key = m.group(1); meta[key] = m.group(2).strip()
        elif key and line.strip():
            meta[key] += " " + line.strip()
    return meta, text[end + 4:].lstrip("\n")


def tidy(md):
    """Python-Markdown wants a blank line before a list or table and 4-space nesting."""
    out, fence = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence:
            line = re.sub(r"^ {2}([-*] |\d+\. )", r"    \1", line)
            starts_block = re.match(r"^([-*] |\d+\. |\|)", line)
            prev = out[-1] if out else ""
            if starts_block and prev.strip() and not re.match(r"^\s*([-*] |\d+\. |\|)", prev) and not prev.startswith(" "):
                out.append("")
        out.append(line)
    return "\n".join(out)


def render(path, text):
    ext = path.suffix.lstrip(".") or path.name.lstrip(".")
    if ext == "md":
        meta, body = frontmatter(text)
        card = ""
        if meta:
            rows = "".join(
                f'<div class="fm-row"><span class="fm-key">{html.escape(k)}</span><span>{html.escape(v)}</span></div>'
                for k, v in meta.items() if k != "name")
            card = f'<div class="fm">{rows}</div>'
        if markdown is None:
            return meta, card + f'<pre class="plain">{html.escape(body)}</pre>'
        return meta, card + markdown.markdown(tidy(body), extensions=["tables", "fenced_code", "sane_lists"])
    lines = "".join(f'<span class="l">{html.escape(l) or " "}</span>' for l in text.split("\n"))
    src = f'<pre class="src"><code>{lines}</code></pre>'
    if ext == "svg":
        b64 = base64.b64encode(text.encode()).decode()
        return {}, f'<figure class="svg"><img alt="{html.escape(path.name)}" src="data:image/svg+xml;base64,{b64}"></figure>' + src
    return {}, src


def main():
    global REPO
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=pathlib.Path, default=REPO, help="the skills library, a git repo (default ~/.claude/skills)")
    ap.add_argument("--out", type=pathlib.Path, default=HOME / ".claude/skills-browser/index.html", help="the page to write")
    ap.add_argument("--open", action="store_true", help="open the page in the default browser")
    args = ap.parse_args()
    REPO = args.repo.expanduser().resolve()
    out = args.out.expanduser()
    paths = git("ls-files").splitlines()
    edited = {l[3:] for l in git("status", "--porcelain").splitlines() if l[:2].strip()}
    # commits per file and per top-level folder per day
    per_file, per_day, per_skill_day = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
    day = None
    for line in git("log", "--relative", "--format=@%cs", "--name-only", "--", ".").splitlines():
        if line.startswith("@"):
            day = line[1:]; per_day[day] += 1; touched = set(); continue
        if line:
            per_file[line] += 1
            top = line.split("/")[0] if "/" in line else "."
            if top not in touched:
                touched.add(top); per_skill_day[top][day] += 1
    days = sorted(per_day)
    last = {}
    for p in paths:
        d, _, s = git("log", "-1", "--format=%cs|%s", "--", p).strip().partition("|")
        last[p] = (d, s)

    files, skills = [], {}
    for p in paths:
        path = REPO / p
        text = path.read_text(errors="replace")
        meta, body = render(path, text)
        skill = p.split("/")[0] if "/" in p else "."
        files.append(dict(path=p, skill=skill, ext=path.suffix.lstrip(".") or path.name.lstrip("."),
                          lines=text.count("\n") + (0 if text.endswith("\n") else 1), bytes=len(text.encode()),
                          date=last[p][0], subject=last[p][1], commits=per_file[p], edited=p in edited, html=body))
        if skill not in skills:
            skills[skill] = dict(name=skill, desc="", when="", commits=sum(per_skill_day[skill].values()),
                                 spark=[per_skill_day[skill][d] for d in days])
        if p.endswith("/SKILL.md"):
            skills[skill].update(desc=meta.get("description", ""), when=meta.get("when_to_use", ""))

    shown = str(REPO).replace(str(HOME), "~", 1)
    data = dict(repo=dict(path=shown, head=git("log", "-1", "--format=%h %cs %s", "--", ".").strip(),
                          commits=int(git("rev-list", "--count", "HEAD", "--", ".")), days=days,
                          spark=[per_day[d] for d in days]),
                skills=sorted(skills.values(), key=lambda s: (s["name"] != ".", s["name"])), files=files)
    blob = json.dumps(data).replace("</", "<\\/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/null", blob))
    print(f"{out}  {len(files)} files  {len(skills) - 1} skills  {out.stat().st_size // 1024} KB")
    if markdown is None:
        print("Markdown shown as plain text; python3 -m pip install markdown renders it")
    if args.open:
        webbrowser.open(out.resolve().as_uri())


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skills Repo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#ffffff; --fg:#14171a; --muted:#56616d; --faint:#9aa4ae; --line:#e3e7ec; --soft:#f3f5f8;
  --rose:#ec3c6e; --rose-soft:rgba(236,60,110,.09); --slate:#8da4bc;
  --sans:"Geist",system-ui,-apple-system,sans-serif; --mono:"Geist Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d1013; --fg:#e7ebef; --muted:#a2acb7; --faint:#5f6a75; --line:#222930; --soft:#151a1f;
  --rose-soft:rgba(236,60,110,.14); --slate:#6f8299;
}}
:root[data-theme="dark"]{
  --bg:#0d1013; --fg:#e7ebef; --muted:#a2acb7; --faint:#5f6a75; --line:#222930; --soft:#151a1f;
  --rose-soft:rgba(236,60,110,.14); --slate:#6f8299;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 var(--sans)}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:21px;padding:13px 21px;flex-wrap:wrap}
.repo{font:600 16px var(--mono)}
.stat{font:13px var(--mono);color:var(--muted);display:flex;align-items:center;gap:8px}
.stat b{color:var(--fg);font-weight:600}
.head{font:13px var(--mono);color:var(--muted);flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.find{font:14px var(--mono);color:var(--fg);background:var(--soft);border:1px solid var(--line);border-radius:8px;
  padding:8px 13px;width:220px;box-shadow:inset 0 1px 2px rgba(0,0,0,.05)}
.find:focus{outline:2px solid var(--rose);outline-offset:1px}
main{display:grid;grid-template-columns:minmax(340px,5fr) 7fr;gap:0}
nav{padding:13px 13px 89px;border-right:1px solid var(--line)}
.group{margin-bottom:8px}
.row{all:unset;box-sizing:border-box;display:grid;width:100%;cursor:pointer;border-radius:8px;padding:8px 13px;
  grid-template-columns:1fr auto;column-gap:13px;align-items:center}
.row:hover{background:var(--soft)}
.row:focus-visible{outline:2px solid var(--rose);outline-offset:-2px}
.row[aria-current="true"]{background:var(--rose-soft);box-shadow:inset 3px 0 0 var(--rose)}
.skill .name{font:600 14px var(--mono)}
.skill .desc{grid-column:1/-1;font-size:13px;color:var(--muted);display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden;margin-top:3px;line-height:1.45}
.skill .meta{display:flex;align-items:center;gap:8px;font:12px var(--mono);color:var(--muted)}
.file{padding:5px 13px 5px 34px}
.file .name{font:13px var(--mono);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.file .name .dir{color:var(--muted)}
.file .meta{font:12px var(--mono);color:var(--muted)}
.ext{display:inline-block;min-width:3.2ch;text-align:center;border:1px solid var(--line);border-radius:5px;
  padding:0 5px;margin-left:8px;color:var(--muted)}
.edit{font:11px var(--mono);color:var(--rose);border:1px solid var(--rose);border-radius:5px;padding:0 4px;margin-left:8px;vertical-align:1px}
.hide{display:none!important}
.dim{opacity:.45}
.spark rect{fill:var(--slate)}
.spark .zero{fill:var(--line)}
#pane{position:sticky;top:var(--hh,58px);height:calc(100vh - var(--hh,58px));overflow:auto;padding:0 34px 89px}
.ph{position:sticky;top:0;background:var(--bg);padding:13px 0 8px;border-bottom:1px solid var(--line);margin-bottom:21px;z-index:2}
.ph .path{font:600 16px var(--mono);display:flex;align-items:center;gap:8px}
.ph .info{font:12px var(--mono);color:var(--muted);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.close{display:none}
.doc{max-width:78ch}
.doc h1{font-size:23px;margin:13px 0 13px;font-weight:600;letter-spacing:-.01em}
.doc h2{font-size:19px;margin:34px 0 8px;font-weight:600;padding-top:8px;border-top:1px solid var(--line)}
.doc h3{font-size:16px;margin:21px 0 5px;font-weight:600}
.doc p{margin:0 0 13px}
.doc ul,.doc ol{padding-left:21px;margin:0 0 13px}
.doc li{margin:0 0 8px}
.doc li>ul,.doc li>ol{margin-top:5px}
.doc code{font:.88em var(--mono);background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px}
.doc pre{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:13px;overflow:auto;font-size:13px}
.doc pre code{border:0;background:none;padding:0}
.doc pre.plain{white-space:pre-wrap;font:13px/1.6 var(--mono)}
.doc blockquote{margin:0 0 13px;padding:3px 0 3px 13px;border-left:3px solid var(--slate);color:var(--muted)}
.doc table{border-collapse:collapse;margin:0 0 13px;font-size:14px;display:block;overflow-x:auto}
.doc th,.doc td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
.doc th{background:var(--soft);font-weight:600}
.doc a{color:inherit;text-decoration:underline;text-decoration-color:var(--slate);text-underline-offset:2px}
.doc a.go{text-decoration-color:var(--rose);text-decoration-style:dotted;text-decoration-thickness:1.5px;cursor:pointer}
.doc a.go:hover{background:var(--rose-soft)}
.doc mark{background:var(--rose-soft);color:inherit;box-shadow:0 0 0 1px var(--rose);border-radius:2px}
.fm{border:1px solid var(--line);border-radius:13px;padding:13px 16px;margin:0 0 21px;background:var(--soft)}
.fm-row{display:grid;grid-template-columns:12.5ch 1fr;gap:13px;font-size:14px;margin:3px 0}
.fm-key{font:12px var(--mono);color:var(--muted);padding-top:2px}
.src{counter-reset:l;font:12.5px/1.6 var(--mono);background:var(--soft);border:1px solid var(--line);border-radius:8px;
  padding:13px 13px 13px 0;overflow:auto;margin:0}
.src .l{display:block;white-space:pre}
.src .l::before{counter-increment:l;content:counter(l);display:inline-block;width:5ch;margin-right:13px;
  text-align:right;color:var(--faint);user-select:none}
figure.svg{margin:0 0 21px;padding:21px;border:1px solid var(--line);border-radius:13px;text-align:center;background:#fff}
figure.svg img{max-width:100%;max-height:420px}
@media (max-width:760px){
  header{padding:8px 16px;gap:8px 13px}
  .head{display:none}
  .find{width:100%}
  main{grid-template-columns:1fr}
  nav{border-right:0;padding:8px 3px 55px}
  #pane{position:fixed;inset:auto 0 0 0;top:auto;height:84vh;z-index:10;background:var(--bg);
    border-top:1px solid var(--line);border-radius:13px 13px 0 0;box-shadow:0 -8px 34px rgba(0,0,0,.18);
    padding:0 16px 55px;transform:translateY(105%);transition:transform .28s ease}
  #pane.open{transform:none}
  .close{display:inline-grid;place-items:center;margin-left:auto;width:44px;height:44px;border-radius:8px;
    border:1px solid var(--line);background:var(--soft);color:var(--fg);font-size:18px;cursor:pointer}
  .ph .path{font-size:14px;word-break:break-all}
  .fm-row{grid-template-columns:1fr;gap:0}
}
@media (prefers-reduced-motion:reduce){#pane{transition:none}}
</style>
</head>
<body>
<header>
  <span class="repo" id="repo"></span>
  <span class="stat" id="stats"></span>
  <span class="head" id="head"></span>
  <input class="find" id="find" type="search" placeholder="find in names and text" aria-label="Find in skills">
</header>
<main>
  <nav id="tree" aria-label="Files"></nav>
  <section id="pane" aria-live="polite">
    <div class="ph"><div class="path"><span id="ppath"></span><button class="close" id="close" aria-label="Close">✕</button></div>
      <div class="info" id="pinfo"></div></div>
    <article class="doc" id="pdoc"></article>
  </section>
</main>
<script id="data" type="application/json">/*DATA*/null</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const byPath = new Map(D.files.map((f, i) => [f.path, i]));
const skillNames = D.skills.map(s => s.name).filter(n => n !== '.').sort((a, b) => b.length - a.length);
const sparkMax = Math.max(...D.skills.map(s => Math.max(...s.spark)));

function spark(vals, max, w = 5, h = 14) {
  const bars = vals.map((v, i) => {
    const bh = v ? Math.max(2, Math.round(v / max * h)) : 1;
    return `<rect class="${v ? '' : 'zero'}" x="${i * (w + 1)}" y="${h - bh}" width="${w}" height="${bh}" rx="1"/>`;
  }).join('');
  return `<svg class="spark" width="${vals.length * (w + 1) - 1}" height="${h}" aria-hidden="true">${bars}</svg>`;
}
const span = `${D.repo.days[0]} to ${D.repo.days.at(-1)}`;
$('stats').innerHTML = `<span><b>${D.skills.length - 1}</b> skills</span><span><b>${D.files.length}</b> files</span>`
  + `<span title="commits per day, ${span}">${spark(D.repo.spark, Math.max(...D.repo.spark), 5, 16)}</span><span><b>${D.repo.commits}</b> commits</span>`;
$('repo').textContent = D.repo.path;
$('head').textContent = 'HEAD ' + D.repo.head;

// tree
const rows = [];
let html = '';
for (const s of D.skills) {
  const fs = D.files.map((f, i) => [f, i]).filter(([f]) => f.skill === s.name);
  const main = fs.find(([f]) => f.path === s.name + '/SKILL.md');
  html += `<div class="group" data-skill="${esc(s.name)}">`;
  if (main) {
    const [f, i] = main;
    html += `<button class="row skill" data-i="${i}" title="">
      <span class="name">${esc(s.name)}${f.edited ? '<span class="edit" title="uncommitted edits in the working tree">edited</span>' : ''}</span>
      <span class="meta" title="${s.commits} commits touch this skill, ${span}">${spark(s.spark, sparkMax)}<span>${f.lines}</span></span>
      <span class="desc">${esc(s.desc)}</span></button>`;
  }
  for (const [f, i] of fs) {
    if (main && i === main[1]) continue;
    const rel = s.name === '.' ? f.path : f.path.slice(s.name.length + 1);
    const cut = rel.lastIndexOf('/');
    const label = cut < 0 ? esc(rel) : `<span class="dir">${esc(rel.slice(0, cut + 1))}</span>${esc(rel.slice(cut + 1))}`;
    html += `<button class="row file" data-i="${i}"><span class="name">${label}${f.edited ? '<span class="edit" title="uncommitted edits in the working tree">edited</span>' : ''}</span>
      <span class="meta">${f.lines}<span class="ext">${esc(f.ext)}</span></span></button>`;
  }
  html += '</div>';
}
$('tree').innerHTML = html;
const rowEls = [...document.querySelectorAll('.row')];
const rowOf = i => rowEls.find(r => +r.dataset.i === i);

// pane
let current = -1, query = '';
function show(i, {scrollRow = false} = {}) {
  const f = D.files[i];
  if (!f) return;
  if (i !== current) {
    current = i;
    $('ppath').textContent = f.path;
    const kb = f.bytes < 1024 ? f.bytes + ' B' : (f.bytes / 1024).toFixed(1) + ' KB';
    $('pinfo').textContent = `${f.lines} lines  ${kb}  ${f.commits} commits  last ${f.date}  ${f.subject}` + (f.edited ? '  (edited, not committed)' : '');
    $('pinfo').title = f.subject;
    $('pdoc').innerHTML = f.html;
    linkify($('pdoc'), f);
    $('pane').scrollTop = 0;
    rowEls.forEach(r => r.setAttribute('aria-current', +r.dataset.i === i));
    history.replaceState(null, '', '#' + encodeURI(f.path));
  }
  highlight();
  if (scrollRow) rowOf(i)?.scrollIntoView({block: 'nearest'});
}

// skill names and relative links inside a document go to that file
function linkify(root, f) {
  const dir = f.path.includes('/') ? f.path.slice(0, f.path.lastIndexOf('/') + 1) : '';
  root.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (/^[a-z]+:/i.test(href) || href.startsWith('#')) { a.target = '_blank'; a.rel = 'noopener'; return; }
    const parts = (dir + href.split('#')[0]).split('/'), out = [];
    for (const p of parts) p === '..' ? out.pop() : p && p !== '.' && out.push(p);
    let target = out.join('/');
    if (!byPath.has(target) && byPath.has(target + '/SKILL.md')) target += '/SKILL.md';
    if (byPath.has(target)) { a.classList.add('go'); a.dataset.go = target; a.removeAttribute('href'); a.tabIndex = 0; }
  });
  const re = new RegExp(`(?<![\\w/-])(${skillNames.map(n => n.replace(/-/g, '\\-')).join('|')})(?![\\w-])`, 'g');
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: n => n.parentElement.closest('a,pre,.fm-key') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT});
  const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    if (!re.test(n.data)) continue;
    re.lastIndex = 0;
    const frag = document.createDocumentFragment();
    let last = 0;
    n.data.replace(re, (m, name, off) => {
      frag.append(n.data.slice(last, off));
      if (name === f.skill) frag.append(m);
      else { const a = document.createElement('a'); a.className = 'go'; a.dataset.go = name + '/SKILL.md'; a.tabIndex = 0; a.textContent = m; frag.append(a); }
      last = off + m.length;
    });
    frag.append(n.data.slice(last));
    const code = n.parentElement.tagName === 'CODE' && n.parentElement.textContent === n.data ? n.parentElement : null;
    if (code && frag.childNodes.length <= 3 && code.textContent.trim() !== f.skill && skillNames.includes(code.textContent.trim())) {
      const a = document.createElement('a'); a.className = 'go'; a.dataset.go = code.textContent.trim() + '/SKILL.md'; a.tabIndex = 0;
      code.replaceWith(a); a.append(code);
    } else n.replaceWith(frag);
  }
}

$('pdoc').addEventListener('click', e => {
  const a = e.target.closest('a.go');
  if (a) { e.preventDefault(); show(byPath.get(a.dataset.go), {scrollRow: true}); }
});
$('pdoc').addEventListener('keydown', e => {
  const a = e.target.closest('a.go');
  if (a && e.key === 'Enter') show(byPath.get(a.dataset.go), {scrollRow: true});
});

// hover with a short intent delay, so a diagonal move to the pane keeps the file you meant
let timer = 0;
const phone = matchMedia('(max-width:760px)');
$('tree').addEventListener('pointerover', e => {
  const r = e.target.closest('.row');
  if (!r || e.pointerType !== 'mouse') return;
  clearTimeout(timer);
  timer = setTimeout(() => show(+r.dataset.i), current < 0 ? 0 : 90);
});
$('tree').addEventListener('pointerout', () => clearTimeout(timer));
$('tree').addEventListener('click', e => {
  const r = e.target.closest('.row');
  if (!r) return;
  clearTimeout(timer);
  show(+r.dataset.i);
  if (phone.matches) $('pane').classList.add('open');
});
$('tree').addEventListener('focusin', e => { const r = e.target.closest('.row'); if (r && !phone.matches) show(+r.dataset.i); });
$('tree').addEventListener('keydown', e => {
  if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
  e.preventDefault();
  const vis = rowEls.filter(r => r.offsetParent);
  const k = vis.indexOf(document.activeElement);
  vis[Math.max(0, Math.min(vis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1)))]?.focus();
});
$('close').addEventListener('click', () => $('pane').classList.remove('open'));

// find: names, descriptions and full text; matches marked in the open document
const texts = D.files.map(f => (f.path + ' ' + f.html.replace(/<[^>]+>/g, ' ')).toLowerCase()
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;/g, "'"));
$('find').addEventListener('input', e => {
  query = e.target.value.trim().toLowerCase();
  let n = 0;
  for (const r of rowEls) {
    const hit = !query || texts[+r.dataset.i].includes(query) || (r.classList.contains('skill') && D.skills.find(s => s.name === D.files[+r.dataset.i].skill).desc.toLowerCase().includes(query));
    r.classList.toggle('hide', !hit && !r.classList.contains('skill'));
    r.classList.toggle('dim', !hit && r.classList.contains('skill'));
    if (hit) n++;
  }
  document.querySelectorAll('.group').forEach(g => g.classList.toggle('hide', !!query && !g.querySelector('.row:not(.hide):not(.dim)')));
  $('find').title = query ? `${n} files match` : '';
  const first = rowEls.find(r => !r.classList.contains('hide') && !r.classList.contains('dim'));
  if (query && first && !texts[current]?.includes(query)) show(+first.dataset.i); else highlight();
});
function highlight() {
  const doc = $('pdoc');
  doc.querySelectorAll('mark').forEach(m => m.replaceWith(...m.childNodes));
  doc.normalize();
  if (query.length < 2) return;
  const walker = document.createTreeWalker(doc, NodeFilter.SHOW_TEXT), nodes = [];
  while (walker.nextNode()) if (walker.currentNode.data.toLowerCase().includes(query)) nodes.push(walker.currentNode);
  for (const n of nodes) {
    const frag = document.createDocumentFragment(), low = n.data.toLowerCase();
    let last = 0, k;
    while ((k = low.indexOf(query, last)) >= 0) {
      frag.append(n.data.slice(last, k));
      const m = document.createElement('mark'); m.textContent = n.data.slice(k, k + query.length); frag.append(m);
      last = k + query.length;
    }
    frag.append(n.data.slice(last)); n.replaceWith(frag);
  }
  doc.querySelector('mark')?.scrollIntoView({block: 'center'});
}

// header height feeds the sticky pane
const setHH = () => document.documentElement.style.setProperty('--hh', document.querySelector('header').offsetHeight + 'px');
addEventListener('resize', setHH); setHH();

// open the file in the URL, else the SKILL.md changed most recently
const fromHash = byPath.get(decodeURI(location.hash.slice(1)));
const latest = D.files.map((f, i) => [f, i]).filter(([f]) => f.path.endsWith('SKILL.md'))
  .sort((a, b) => b[0].date.localeCompare(a[0].date))[0][1];
show(fromHash ?? latest, {scrollRow: fromHash != null});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
