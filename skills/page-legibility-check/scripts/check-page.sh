#!/bin/zsh
# usage: check-page.sh <page.html> [query] [delay-ms] [screenshot-dir]
# Checks a local HTML page at 1280 px and at a true 400 px (inside an iframe: headless Chrome will not size a window
# below 500 px) in light and dark (sets <html data-theme>), and prints one JSON line per run plus PASS/FAIL.
# The page is copied to a temp dir with <base href> pointing at its own folder, so relative assets and fetch()ed
# JSON next to it still load (file access from files is allowed for this run).
[[ $1 == -h || $1 == --help ]] && { sed -n '2,5p' $0; exit 0; }
[[ -f $1 ]] || { echo "usage: check-page.sh <page.html> [query] [delay-ms] [screenshot-dir]  (no page at '$1')"; exit 2; }
SRC=${1:A}; Q=${2:-}; DELAY=${3:-1500}; SHOTS=${4:-}
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
T=$(mktemp -d); HERE=${0:A:h}
python3 - "$SRC" "$T" "$DELAY" "$HERE/check.js" <<'PY'
import sys, pathlib, re
src, t, delay, chk = sys.argv[1:5]
page = pathlib.Path(src).read_text()
head = '<base href="file://%s/">' % pathlib.Path(src).parent + \
  "<script>(function(){var th=new URLSearchParams(location.search).get('theme');if(th)document.documentElement.dataset.theme=th;})();</script>"
m = re.match(r'\s*<!doctype[^>]*>', page, re.I)          # keep the doctype first, or the page drops into quirks mode
page = (page[:m.end()] + head + page[m.end():]) if m else head + page
check = pathlib.Path(chk).read_text().replace('__DELAY__', delay)
pathlib.Path(t, 'page.html').write_text(page + '\n<script>\n' + check + '\n</script>\n')
pathlib.Path(t, 'wrap.html').write_text('''<meta charset="utf-8"><body style="margin:0">
<iframe id="f" style="width:400px;height:2400px;border:0;display:block"></iframe>
<script>document.getElementById('f').src='page.html'+location.search;
addEventListener('message',e=>{const p=document.createElement('pre');p.id='__out';p.textContent=JSON.stringify(e.data);document.body.appendChild(p);});</script>''')
PY
H=(--headless=new --disable-gpu --hide-scrollbars --no-first-run --no-default-browser-check --allow-file-access-from-files --user-data-dir=$T/prof --virtual-time-budget=$((DELAY+7000)))
EXT='import sys,re,json,html
m=re.search(r"<pre id=\"__out\"[^>]*>(\{.*?\})</pre>",sys.stdin.read(),re.S)
if not m: print("NO OUTPUT (page error, or raise delay-ms)"); sys.exit(1)
d=json.loads(html.unescape(m.group(1))); bad=len(d["contrast"])+len(d["overlap"])+len(d["wide"])+len(d.get("clipped",[]))+int(d["hscroll"])
print(json.dumps(d)); sys.exit(1 if bad else 0)'
fail=0
for th in light dark; do
  q="?theme=$th${Q:+&$Q}"
  for spec in "1280:1280,1400:page" " 400:600,2400:wrap"; do lab=${spec%%:*}; rest=${spec#*:}; size=${rest%%:*}; pg=${rest#*:}
    for try in 1 2; do   # a headless render occasionally ends before the check fires; one retry settles it
      out=$("$CH" $H --window-size=$size --dump-dom "file://$T/$pg.html$q" 2>/dev/null | python3 -c "$EXT"); rc=$?
      [[ $out != NO\ OUTPUT* ]] && break; done
    print -r -- "$lab $th: $out"; (( rc )) && fail=1; done   # print -r: the JSON holds \u escapes zsh echo would mangle
  if [[ -n $SHOTS ]]; then mkdir -p $SHOTS
    "$CH" $H --window-size=1280,1300 --screenshot=$SHOTS/desk-$th.png "file://$T/page.html$q" >/dev/null 2>&1
    "$CH" $H --window-size=600,2400 --screenshot=$SHOTS/phone-$th.png "file://$T/wrap.html$q" >/dev/null 2>&1; fi
done
rm -rf $T
[[ $fail == 0 ]] && echo PASS || { echo "FAIL (tiny = rendered text under 9 px; listed, not counted)"; exit 1; }
