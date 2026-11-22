#!/usr/bin/env node
// Lints a page's figures for text that does not belong in a drawing (floaters, sentences, instruction lines,
// titles that are not findings, duplicated keys, unlabelled axes) and sweeps every text box on the page for
// clipping, truncation and collisions across widths and themes, with folds open and each hover card opened.
//
//   NODE_PATH=<dir holding playwright> node figure-lint.cjs PAGE.html [options]
//     --pass figures|clip|both   default both
//     --width N                  width for the figure pass (default 1000)
//     --widths LO:HI:STEP        clipping sweep (default 360:1440:40)
//     --themes light,dark        default both
//     --tips / --no-tips         open each hover card during the sweep (default on)
//     --json PATH                write every finding as JSON
//     --max N                    findings printed per rule (default 6)
// Exits 1 when anything is flagged, 0 when clean.
const fs = require('fs'), os = require('os'), path = require('path');
const { chromium } = require('playwright');

const RULES = {
  unmeasurable: 'a figure whose text could not be measured — not a clean figure',
  floater: 'text far from any shape it could name',
  sentence: 'a sentence where a label belongs',
  meta: 'instruction or meta line',
  echo: 'a line repeating the figure caption',
  'title-not-finding': 'figure title is not a declarative finding',
  'panel-title': 'panel title is not a scientific noun phrase',
  sizes: 'more than three rendered label sizes in one drawing',
  'mark-on-text': 'an arrow or a mark crossing a label',
  'key-dup': 'key entry for a mark already labelled in place',
  'key-dup-control': 'key entry duplicating an in-place label, but also the figure\'s control',
  'name-twice': 'one name twice in one block',
  'axis-unlabelled': 'axis without a label and unit',
  'no-n': 'a measurement plotted without n or an error definition',
  'clip-ancestor': 'text past an ancestor that hides overflow',
  'clip-viewbox': 'svg label outside its viewBox',
  'clip-viewport': 'text past the viewport',
  'clip-ellipsis': 'text truncated by ellipsis or line-clamp',
  'text-overlap': 'text over text'
};

function args(argv) {
  const o = { pass: 'both', width: 1000, widths: '360:1440:40', themes: 'light,dark', tips: true, max: 6, json: '', expect: false };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--expect') o.expect = true;
    else if (a === '--no-tips') o.tips = false;
    else if (a === '--tips') o.tips = true;
    else if (a.startsWith('--')) o[a.slice(2)] = argv[++i];
    else rest.push(a);
  }
  o.src = rest[0];
  o.width = +o.width; o.max = +o.max;
  return o;
}

// A copy with <base href> so relative assets still load, the probe appended, and ?theme honoured.
function stage(src) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'figlint-'));
  const abs = path.resolve(src);
  let page = fs.readFileSync(abs, 'utf8');
  const head = '<base href="file://' + path.dirname(abs) + '/">';
  const m = page.match(/^\s*<!doctype[^>]*>/i);
  page = m ? page.slice(0, m[0].length) + head + page.slice(m[0].length) : head + page;
  const probe = fs.readFileSync(path.join(__dirname, 'figure-lint-rules.js'), 'utf8');
  fs.writeFileSync(path.join(dir, 'page.html'), page + '\n<script>\n' + probe + '\n</script>\n');
  return { dir, url: 'file://' + path.join(dir, 'page.html') };
}

async function settle(page, theme) {
  await page.evaluate(t => { document.documentElement.dataset.theme = t; }, theme);
  await page.evaluate(() => {
    if (typeof window.__still === 'function') window.__still();   // a page's own hook: put it in its still state
    document.querySelectorAll('details').forEach(d => { d.open = true; });
    document.getAnimations().forEach(a => { try { if (a.effect && a.effect.getTiming().iterations !== Infinity) a.finish(); } catch (e) {} });
  });
  await page.waitForTimeout(260);
}

async function main() {
  const o = args(process.argv.slice(2));
  if (!o.src || !fs.existsSync(o.src)) {
    console.error(fs.readFileSync(__filename, 'utf8').split('\n').slice(1, 14).join('\n').replace(/^\/\/ ?/gm, ''));
    process.exit(2);
  }
  const { dir, url } = stage(o.src);
  let expected = {};
  const browser = await chromium.launch({ channel: 'chrome' });
  const findings = [];
  try {
    const ctx = await browser.newContext({ viewport: { width: o.width, height: 1200 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    page.on('pageerror', e => console.error('page error:', e.message));
    await page.goto(url, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);  // measure in the webfont, not a fallback: counts moved run to run without this
    await page.waitForTimeout(900);

    if (o.pass === 'figures' || o.pass === 'both') {
      await settle(page, 'light');
      findings.push(...await page.evaluate(() => window.__figlint.figures()));
      if (o.expect) expected = await page.evaluate(() => window.__figlint.expected());
    }

    if (o.pass === 'clip' || o.pass === 'both') {
      const [lo, hi, step] = o.widths.split(':').map(Number);
      const themes = o.themes.split(',');
      for (const theme of themes) {
        for (let w = lo; w <= hi; w += step) {
          await page.setViewportSize({ width: w, height: 1200 });
          await settle(page, theme);
          findings.push(...await page.evaluate(([W, t]) => window.__figlint.clip(W, t), [w, theme]));
          if (o.tips) findings.push(...await page.evaluate(([W, t]) => window.__figlint.tips(W, t), [w, theme]));
        }
      }
    }
  } finally {
    await browser.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }

  report(findings, o);
  if (o.expect) process.exit(checkExpected(findings, expected) ? 0 : 1);
  process.exit(findings.length ? 1 : 0);
}

// One row per rule, then the first --max findings of each. A clipping finding is reported once per place, with
// the widths it appears at, so one narrow break does not print 28 times.
function report(findings, o) {
  const byRule = {};
  findings.forEach(f => (byRule[f.rule] = byRule[f.rule] || []).push(f));
  const fold = list => {
    const seen = new Map();
    list.forEach(f => {
      const k = [f.fig, f.text, f.detail.replace(/-?\d+(\.\d+)?/g, '#')].join('␟');
      const e = seen.get(k) || { ...f, widths: new Set(), themes: new Set() };
      if (f.w) e.widths.add(f.w); if (f.theme) e.themes.add(f.theme);
      seen.set(k, e);
    });
    return [...seen.values()];
  };
  const order = Object.keys(RULES).filter(r => byRule[r]);
  console.log('page: ' + path.resolve(o.src));
  console.log('rule                  places  hits  what it means');
  let places = 0;
  order.forEach(r => {
    const f = fold(byRule[r]);
    places += f.length;
    console.log(r.padEnd(20) + String(f.length).padStart(7) + String(byRule[r].length).padStart(6) + '  ' + RULES[r]);
  });
  if (!order.length) console.log('(nothing flagged)');
  console.log('\ntotal: ' + places + ' places, ' + findings.length + ' hits');
  order.forEach(r => {
    const f = fold(byRule[r]);
    console.log('\n== ' + r + ' (' + f.length + ') ' + RULES[r]);
    f.slice(0, o.max).forEach(e => {
      const ws = e.widths.size ? '  [' + [...e.themes].join('/') + ' ' + rangeOf([...e.widths]) + ']' : '';
      console.log('  ' + e.fig + (e.id ? ' [' + e.id + ']' : '') + ': ' + e.text + '\n      ' + e.detail + ws);
    });
    if (f.length > o.max) console.log('  ... ' + (f.length - o.max) + ' more');
  });
  if (o.json) {
    fs.writeFileSync(o.json, JSON.stringify(findings, null, 1));
    console.log('\nJSON: ' + path.resolve(o.json));
  }
}
// --expect: each data-expect figure must trip exactly the rules it names. A fixture that drifts fails here.
function checkExpected(findings, expected) {
  const got = {};
  findings.forEach(f => { if (f.id) (got[f.id] = got[f.id] || new Set()).add(f.rule); });
  let ok = true;
  console.log('\nfixture check (data-expect)');
  Object.keys(expected).sort().forEach(id => {
    const want = new Set(expected[id]), have = got[id] || new Set();
    const missing = [...want].filter(r => !have.has(r));
    const extra = [...have].filter(r => !want.has(r));
    if (missing.length || extra.length) { ok = false;
      console.log('  FAIL ' + id + (missing.length ? '  missing: ' + missing.join(' ') : '') + (extra.length ? '  unexpected: ' + extra.join(' ') : ''));
    } else console.log('  ok   ' + id + '  ' + ([...want].join(' ') || '(clean)'));
  });
  const stray = Object.keys(got).filter(id => !(id in expected));
  if (stray.length) { ok = false; console.log('  FAIL findings on figures with no data-expect: ' + stray.join(' ')); }
  console.log(ok ? 'fixture: PASS' : 'fixture: FAIL');
  return ok;
}

const rangeOf = ws => {
  const s = [...new Set(ws)].sort((a, b) => a - b);
  return s.length > 2 ? s[0] + '-' + s[s.length - 1] + ' px (' + s.length + ')' : s.join(', ') + ' px';
};

main().catch(e => { console.error(e); process.exit(2); });
