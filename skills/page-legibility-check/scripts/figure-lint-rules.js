// In-page probe for figure-lint.cjs. Defines window.__figlint with three passes:
//   figures()  one entry per figure-text rule it breaks (floaters, sentences, meta lines, titles, sizes, keys, axes)
//   clip()     one entry per text box clipped, truncated or overlapping another, at the current width and theme
//   tips()     the same clipping rules applied to each hover card, opened one at a time
// Every finding is {rule, fig, text, detail}. The driver groups and counts them; nothing here prints.
(function () {
  'use strict';

  /* ---------- words ---------- */

  const WORD = /[A-Za-z]/;
  const words = s => String(s || '').trim().split(/\s+/).filter(w => WORD.test(w));
  const norm = s => String(s || '').toLowerCase().replace(/[‘’'`]/g, '')
    .replace(/[^a-z0-9%$+µ°\/.\-]+/g, ' ').replace(/\s+/g, ' ').trim();
  const tokens = s => norm(s).split(' ').filter(t => t.length > 2 && !STOP.has(t));
  const STOP = new Set(('a an the of in on at to for from with by and or as is are was were be been it its that this ' +
    'than then but not no into over under per each one two three both all any more most less least same other ' +
    'which what when where how why who whose can could may might must should would will shall').split(' '));

  // Verbs a declarative scientific finding is built on. A title with none of these, and no -s/-ed form, is read as
  // a noun phrase rather than a finding; a panel title WITH one is read as a sentence.
  const VERBS = new Set(('is are was were be been being has have had does do did can could may might must should ' +
    'would will shall falls fall rises rise increases increase decreases decrease drops drop grows grow shrinks ' +
    'shrink varies vary crosses cross keeps keep lets let shows show carries carry blocks block binds bind needs ' +
    'need costs cost scales scale tracks track predicts predict separates separate reaches reach remains remain ' +
    'holds hold stops stop moves move sets makes make turns turn sells sell splits split raises raise lowers lower ' +
    'cuts cut adds add differs differ depends depend survives survive clears clear enters enter leaves leave ' +
    'reduces reduce matches match fails fail works work runs run gives give takes take passes pass lands land ' +
    'sits sit spans span exceeds exceed leads lead follows follow drives drive limits limit shapes explains ' +
    'explain accounts account peaks peak returns return persists persist competes compete inhibits inhibit ' +
    'activates activate antagonises antagonizes stimulates stimulate triggers trigger releases release transports ' +
    'transport cleaves cleave degrades degrade spares spare costs rank ranks ranked beat beats outlives outlast ' +
    'buys buy pays pay earns earn gains gain loses lose wins win ends end begins begin starts start').split(' '));
  const QUESTION = new Set('what why how when where which who whose can could does do is are should would will did'.split(' '));
  const PLURAL_NOUNS = new Set(('peptides drugs cells acids residues doses sales trials studies routes doors ' +
    'organs tissues costs mass class loss analysis synthesis series species cross-links contacts claims names ' +
    'molecules proteins receptors markets patents layers years months weeks hours grams values levels').split(' '));

  // Words that end in s without being verbs: function words, Latin and medical endings, mass nouns.
  const NOT_VERB_S = /(ss|us|is|ics|ness|osis|itis|ous|sis)$/;
  const bare = str => norm(str).replace(/\([^)]*\)/g, ' ').replace(/\s+/g, ' ').trim();
  const FINITE = new Set(('is are was were has have does do can will must should would may might falls rises drops ' +
    'grows shrinks varies crosses keeps lets shows carries binds needs tracks predicts separates reaches remains ' +
    'stops moves turns sells splits raises lowers differs depends survives clears enters leaves reduces matches ' +
    'fails exceeds follows drives explains accounts persists competes inhibits activates activated antagonises ' +
    'stimulates triggers transports cleaves degrades spares bind cross keep let show carry need reach '
    + 'makes make adds add stays stay holds hold costs buys sells pays leaves leave ' +
    'remain stop move turn sell split raise lower differ depend survive clear enter leave reduce match fail ' +
    'exceed follow drive explain account persist compete inhibit activate transport cleave degrade').split(' '));
  // a verb anywhere (used to ask whether a figure title is a finding at all: a generous set risks only a miss)
  const hasVerb = str => {
    const t = bare(str).split(' ');
    if (t.some(w => VERBS.has(w))) return true;
    return t.some(w => /^[a-z]{3,}(?:ed|s)$/.test(w) && !PLURAL_NOUNS.has(w) && !STOP.has(w) && !NOT_VERB_S.test(w));
  };
  // a finite verb that makes a phrase a sentence (used on panel titles: a narrow set risks only a miss)
  const isSentence = str => {
    const t = bare(str).split(' ').filter(Boolean);
    if (t.some(w => FINITE.has(w))) return true;
    const last = t[t.length - 1] || '';
    return /^[a-z]{4,}ed$/.test(last) && !STOP.has(last);
  };

  /* ---------- geometry ---------- */

  const seen = el => {
    if (!el || !el.getBoundingClientRect) return false;
    if (el.checkVisibility && !el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
    const b = el.getBoundingClientRect();
    return b.width > 0.5 && b.height > 0.5;
  };
  // A mark can be zero-thickness: getBoundingClientRect on an SVG <line> returns 0 in one dimension, so the
  // text test (both sides > 0.5) threw away every axis line and tick.
  const seenMark = el => {
    if (!el || !el.getBoundingClientRect) return false;
    if (el.checkVisibility && !el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
    const b = el.getBoundingClientRect();
    return b.width > 0.5 || b.height > 0.5;
  };
  const gap = (a, b) => {                       // 0 when the boxes touch or overlap, else the shortest distance
    const dx = Math.max(0, Math.max(a.left - b.right, b.left - a.right));
    const dy = Math.max(0, Math.max(a.top - b.bottom, b.top - a.bottom));
    return Math.hypot(dx, dy);
  };
  const area = b => Math.max(0, b.width) * Math.max(0, b.height);
  const inter = (a, b) => ({
    left: Math.max(a.left, b.left), right: Math.min(a.right, b.right),
    top: Math.max(a.top, b.top), bottom: Math.min(a.bottom, b.bottom),
    get width() { return this.right - this.left; }, get height() { return this.bottom - this.top; }
  });

  // What an ancestor's clip actually leaves on screen. Text cut away by an svg's edge or an overflow:hidden box is
  // invisible, so comparing it with its neighbours invents collisions; null means nothing of it is painted.
  function visibleBox(el) {
    let b = el.getBoundingClientRect();
    for (let p = el.parentElement || (el.ownerSVGElement || null); p && p !== document.body; p = p.parentElement) {
      const st = getComputedStyle(p);
      const clips = p.tagName.toLowerCase() === 'svg' || /^(hidden|clip)$/.test(st.overflowX) || /^(hidden|clip)$/.test(st.overflowY);
      if (!clips) continue;
      b = inter(b, p.getBoundingClientRect());
      if (b.width <= 0.5 || b.height <= 0.5) return null;
    }
    return { left: b.left, right: b.right, top: b.top, bottom: b.bottom, width: b.width, height: b.height };
  }

  const SKIP_PAINT = 'defs,clipPath,mask,marker,pattern,symbol';
  // Shapes a label could be naming: painted, inside this drawing, not a hit target and not the label's own backing.
  function shapesOf(svg) {
    return [...svg.querySelectorAll('rect,circle,ellipse,path,line,polygon,polyline,use,image')].filter(e => {
      if (e.closest(SKIP_PAINT)) return false;
      // a highlighter band drawn under a label (data-band) is the backing for that label, a halo, not a mark on it
      if (e.hasAttribute('data-band')) return false;
      const st = getComputedStyle(e);
      const fill = st.fill, stroke = st.stroke;
      const noFill = !fill || fill === 'none' || fill === 'transparent' || /rgba\(.*,\s*0\)$/.test(fill);
      const noStroke = !stroke || stroke === 'none' || st.strokeWidth === '0px';
      if (noFill && noStroke) return false;
      return seenMark(e);
    }).map(e => ({ el: e, box: e.getBoundingClientRect() }));
  }

  // A <text> whose <tspan>s carry their own x or y paints several separate runs; measuring the parent's box
  // merges a panel letter with the title beside it and reports a gap neither of them has.
  const texts = root => [...root.querySelectorAll('text')].flatMap(t => {
    if (!t.textContent.trim() || !seen(t)) return [];
    const runs = [...t.children].filter(c => c.tagName === 'tspan'
      && ['x', 'y', 'dx', 'dy'].some(a => c.hasAttribute(a))
      && c.textContent.trim() && seen(c));
    return runs.length ? runs : [t];
  });
  const sizeOf = t => Math.round(parseFloat(getComputedStyle(t).fontSize) * 2) / 2;
  const boldOf = t => {
    const w = getComputedStyle(t).fontWeight;
    return (w === 'bold' ? 700 : +w || 400) >= 600;
  };
  const drawings = f => [...f.querySelectorAll('svg')].filter(s => !s.closest('.fkey') && !s.parentNode.closest('svg'));

  /* ---------- figure rules ---------- */

  const FLOAT_PX = 24;        // a label this close to a mark plainly names it
  const REACH_PX = 150;       // ...and past that, only if it lines up with the mark: a side label on the mark's
  const ALIGN_PX = 60;        //    own row, or a label squarely above or below it. Both are how a reader pairs
                              //    them (fig8's annotation column sits 30-60 px right of each protein, centred
                              //    on it, and reads correctly; a 24 px rule called all 19 of them floaters).
  // Two runs of text are in one table when they share a column and a row with other runs: a cell belongs to its
  // grid, not to a mark. Without this, every cell of a table-shaped figure was a floater.
  function gridded(ts) {
    const near = (a, b) => Math.abs(a - b) <= 3;
    const boxes = ts.map(t => t.getBoundingClientRect());
    return boxes.map((b, i) => {
      let col = 0, row = 0;
      boxes.forEach((c, j) => {
        if (i === j) return;
        // a column lines up on any of its three edges: cells may be left-, right- or centre-set
        if (near(b.left, c.left) || near(b.right, c.right) || near((b.left + b.right) / 2, (c.left + c.right) / 2)) col++;
        if (near(b.top, c.top) || near(b.bottom, c.bottom) || near((b.top + b.bottom) / 2, (c.top + c.bottom) / 2)) row++;
      });
      // a cell has company down its column and across its row; two of one and one of the other is a table
      return (col >= 2 && row >= 1) || (row >= 2 && col >= 1);
    });
  }
  const alignedTo = (box, sh) => {
    const vMid = (box.top + box.bottom) / 2, sMid = (sh.top + sh.bottom) / 2;
    const sameRow = vMid > sh.top - 4 && vMid < sh.bottom + 4 && Math.abs(sMid - vMid) < ALIGN_PX;
    const hMid = (box.left + box.right) / 2, shMid = (sh.left + sh.right) / 2;
    const sameCol = hMid > sh.left - 4 && hMid < sh.right + 4 && Math.abs(shMid - hMid) < REACH_PX;
    if (sameRow) return Math.max(0, Math.max(box.left - sh.right, sh.left - box.right)) <= REACH_PX;
    if (sameCol) return Math.max(0, Math.max(box.top - sh.bottom, sh.top - box.bottom)) <= ALIGN_PX;
    return false;
  };
  const SENT_WORDS = 6;       // past this, a line inside a drawing is a sentence
  const META = /\b(point at|hover|hovering|tap (a|on|the)|click|press →|press ←|drag|scroll (right|to)|see (below|above)|typical values?|values? (are )?typical|not retrieved|not reported here|placeholder|to be confirmed|tbd|data not shown|illustrative only|schematic only|for illustration)\b/i;
  const UNIT = /(\bnmol|µmol|\bmol\b|µg|\bmg\b|\bng\b|\bpg\b|\bkg\b|\bg\b|µM|\bnM\b|\bmM\b|\bpM\b|\bmm\b|\bcm\b|\bnm\b|µm\b|\bkDa\b|\bDa\b|\bh\b|\bhours?\b|\bmin\b|\bsec|\bdays?\b|\bweeks?\b|\byears?\b|%|\$|\bUSD\b|\bper\b|\/cm|\bresidues?\b|\bcount\b|\bn\s*=|\bkcal|\bpH\b|\blog\b|×|\bfold\b|\brank\b|\bscore\b)/i;
  const NSTAT = /(\bn\s*=|\bn\b\s*(of|per)\b|±|\bSD\b|\bSEM\b|\bs\.d\.|\bs\.e\.m\.|95\s*%\s*CI\b|\bIQR\b|\bmedian\b|\bmean of\b|\bone\s+\w+\s+per\b|\beach\s+\w+\s+is\b|\bper\s+\w+,\s*n)/i;
  const NAME_RE = /\b(?:[A-Z]{2,6}-\d{1,4}[a-z]?|[A-Z]{3,6}-[A-Za-z]{1,3}|GLP-\d|[A-Za-z]{4,}tides?)(?![A-Za-z0-9-])/g;
  const NOT_A_NAME = new Set(('peptide peptides polypeptide polypeptides oligopeptide dipeptide tripeptide ' +
    'nucleotide nucleotides').split(' '));

  // Where an axis's tick labels and title sit. Both the floater rule (they name the axis) and the unit rule read it.
  const AXIS_BAND = 70;
  const inBand = (ax, b) => ax.dir === 'x'
    ? b.top > ax.box.top - 8 && b.top < ax.box.bottom + AXIS_BAND
    : b.right < ax.box.right + 10 && b.right > ax.box.left - 90;

  function figureName(f) {
    const k = f.querySelector('figcaption .k');
    return (k ? k.textContent : f.id || '?').trim();
  }
  function titleOf(f) {
    const b = f.querySelector('figcaption b');
    return b ? b.textContent.replace(/\s+/g, ' ').trim() : '';
  }
  // Stacked <text> lines that make one wrapped sentence: same x, stepping down by about one line, 3+ words each.
  function lineGroups(svg) {
    const out = [], used = new Set();
    const style = t => { const c = getComputedStyle(t); return c.fontSize + '/' + c.fontWeight + '/' + c.fill; };
    const ts = texts(svg).map(t => ({ t, b: t.getBoundingClientRect(), n: words(t.textContent).length, s: style(t) }));
    ts.forEach((a, i) => {
      if (used.has(i) || a.n < 3) return;
      const run = [a]; used.add(i);
      for (let j = i + 1; j < ts.length; j++) {
        const c = ts[j], last = run[run.length - 1];
        if (used.has(j) || c.n < 3) continue;
        const open = /[A-Za-z,\u2013-]$/.test(last.t.textContent.trim());
        if (open && c.s === last.s && Math.abs(c.b.left - last.b.left) <= 2 && c.b.top - last.b.top > 0 && c.b.top - last.b.top < last.b.height * 2.2) {
          run.push(c); used.add(j);
        }
      }
      if (run.length > 1) out.push(run);
    });
    return out;
  }

  // A figure's panel title: bold, two or more words, no digits, at or above the figure's median bold size.
  // Both the panel-title rule and the sentence rule read it, so it is asked in one place.
  // Nature's convention: the panel letter is its own run ahead of the title, and the title itself need not be
  // bold. Reading boldness alone missed four panel titles whose letter was the only bold tspan.
  const panelLettered = t => {
    const owner = t.tagName === 'tspan' ? t.parentElement : t;
    const first = owner && owner.firstElementChild;
    return !!first && first.tagName === 'tspan' && /^[A-Z]$/.test(first.textContent.trim());
  };
  const isPanelTitle = (t, s, med) => !/\d/.test(s) && words(s).length >= 2
    && (panelLettered(t) || (boldOf(t) && sizeOf(t) >= med));

  function textRules(f, add) {
    const caption = (f.querySelector('figcaption') || {}).textContent || '';
    const capTokens = new Set(tokens(titleOf(f)));
    drawings(f).forEach(svg => {
      const shapes = shapesOf(svg);
      const ts = texts(svg);
      const axes = axesOf(svg);
      const inGrid = gridded(ts);
      const sizes = new Set(ts.map(sizeOf));
      if (sizes.size > 3) add('sizes', f, [...sizes].sort((a, b) => a - b).join(', ') + ' px',
        sizes.size + ' rendered label sizes in one drawing');

      const bold = ts.filter(t => boldOf(t) && !/\d/.test(t.textContent) && words(t.textContent).length >= 2);
      const med = bold.length ? bold.map(sizeOf).sort((a, b) => a - b)[Math.floor(bold.length / 2)] : 0;

      ts.forEach((t, ti) => {
        const s = t.textContent.replace(/\s+/g, ' ').trim();
        const box = t.getBoundingClientRect();

        // floater: no shape within FLOAT_PX. A shape that merely sits behind the text is its backing, not a subject.
        let near = Infinity, nearTag = '', lined = false;
        for (const sh of shapes) {
          const st2 = getComputedStyle(sh.el);
          const unstroked = st2.stroke === 'none' || st2.strokeWidth === '0px';
          const backing = unstroked && sh.box.left <= box.left + 1 && sh.box.right >= box.right - 1 &&
            sh.box.top <= box.top + 1 && sh.box.bottom >= box.bottom - 1 && area(sh.box) < area(box) * 3;
          if (backing) continue;
          const g2 = gap(box, sh.box);
          if (g2 < near) { near = g2; nearTag = sh.el.tagName; }
          if (!lined && alignedTo(box, sh.box)) lined = true;
          if (near <= FLOAT_PX) break;
        }
        const heading = panelLettered(t) || boldOf(t);
        if (near > FLOAT_PX && !lined && !inGrid[ti] && !heading && !axes.some(ax => inBand(ax, box)))
          add('floater', f, s, (near === Infinity ? 'no shape in the drawing' : Math.round(near) + ' px from the nearest shape')
            + ' [' + (isPanelTitle(t, s, med) ? 'heading' : 'label') + (boldOf(t) ? ', bold' : '') + ', ' + sizeOf(t) + 'px'
            + (nearTag ? ', nearest ' + nearTag : '') + ']');

        // a sentence where a label belongs
        const n = words(s).length;
        const stop = /[a-z’)%\]]\.$/.test(s) && !/\b([A-Z]|no|fig|vs|cf|e\.g|i\.e)\.$/.test(s);
        // An axis's own title and tick labels are not floaters or sentences: an axis title must carry its unit
        // and direction, so it is long by design (figure-design section 1). A data label that names a quantity
        // and its unit, and a comma-separated list of names, are labels too, however many words they run to.
        const onAxis = axes.some(ax => inBand(ax, box));
        const quantity = UNIT.test(s) && !isSentence(s);
        const list = (s.match(/,/g) || []).length >= 2 && !isSentence(s);   // two commas is a list of three
        if ((n > SENT_WORDS && !onAxis && !quantity && !list && !isPanelTitle(t, s, med)) || stop)
          add('sentence', f, s, n + ' words' + (stop ? ', ends in a full stop' : ''));

        if (META.test(s)) add('meta', f, s, 'instruction or meta line');

        // a label that repeats the figure's own title
        // A panel title names its panel, so it shares the figure's own nouns by design: judging it against the
        // caption title made "Two cAMP sensors of the beta cell" an echo of a caption about cAMP in the beta cell.
        const tk = isPanelTitle(t, s, med) ? [] : tokens(s);
        if (tk.length >= 4) {
          const hit = tk.filter(w => capTokens.has(w)).length;
          if (hit / tk.length >= 0.7) add('echo', f, s, 'repeats the caption title (' + hit + '/' + tk.length + ' words)');
        }

        // panel title: a bold, wordy, digit-free label should be a noun phrase, not a sentence
        if (isPanelTitle(t, s, med)) {
          const w0 = bare(s).split(' ')[0];
          const ws = bare(s).split(' ').filter(Boolean);
          if (/^(a|an|the|how|what|why|when|where|who)$/.test(w0) || (/ing$/.test(w0) && ws.length > 2) || isSentence(s))
            add('panel-title', f, s, 'reads as a sentence, not a scientific noun phrase');
        }
      });

      markOnText(f, svg, ts, add);

      lineGroups(svg).forEach(run => {
        const s = run.map(r => r.t.textContent.trim()).join(' ');
        const n = words(s).length;
        if (n > SENT_WORDS * 2 && !(UNIT.test(s) && !isSentence(s)))
          add('sentence', f, s, 'wrapped over ' + run.length + ' lines, ' + n + ' words');
      });
    });

    // figure title: a declarative finding, never a question
    const title = titleOf(f);
    if (title) {
      const w0 = norm(title).split(' ')[0];
      if (/\?$/.test(title)) add('title-not-finding', f, title, 'a question');
      else if (QUESTION.has(w0)) add('title-not-finding', f, title, 'opens with "' + w0 + '"');
      else if (!hasVerb(title)) add('title-not-finding', f, title, 'no verb: reads as a label, not a finding');
    }

    // a key entry for a mark the drawing already names in place
    const drawn = drawings(f).flatMap(svg => texts(svg).map(t => norm(t.textContent)));
    f.querySelectorAll('.fkey .key').forEach(k => {
      const label = k.textContent.replace(/\s+/g, ' ').trim();
      const head = norm(label.split(/[,;(]/)[0]);
      if (head.length < 3) return;
      if (norm(label).length > head.length + 2) return;   // ", counted on its own" is the information: it earns the row
      const control = k.hasAttribute('data-k') || k.hasAttribute('tabindex');
      if (drawn.some(d => d === head || (head.length >= 4 && d.includes(head))))
        add(control ? 'key-dup-control' : 'key-dup', f, label, 'the drawing already labels "' + head + '" in place'
          + (control ? ', and this row is also the figure\'s control' : ''));
    });

    // the same peptide named twice inside one block. A panel is the block, not the whole drawing: a figure with
    // four panels names its subject once in each, which is how each panel stands on its own; twice inside one
    // panel is the repeat. Panels are split at the panel-lettered headings, top to bottom.
    // A block is the smallest self-contained unit the reader takes in on its own: a callout, a panel. Each one
    // has to name its subject, so a cell map with four callouts about MOTS-c names it four times by design
    // (a peptide explainer's cell map, 2026-11-22). Blocks are the identified groups in the drawing, or the panels when it has none.
    const panels = {};
    drawings(f).forEach((svg, si) => {
      const unit = t => {
        let u = null;
        for (let g = t.parentElement; g && g !== svg; g = g.parentElement) {
          if (g.tagName === 'g' && (g.hasAttribute('data-k') || g.hasAttribute('aria-label')
            || g.hasAttribute('role') || g.hasAttribute('id'))) u = g;
        }
        return u;
      };
      const ts = texts(svg).map(t => { const b = t.getBoundingClientRect();
        return { t, y: b.top, x: b.left, u: unit(t) }; }).sort((a, b) => a.y - b.y);
      // Panels sit side by side as well as stacked (one figure's B and C shared a heading row), so a text
      // belongs to the last heading above it AND, within that heading's row, the nearest one to its left.
      const heads = ts.filter(o => panelLettered(o.t)).map(o => ({ x: o.x, y: o.y }));
      const units = new Map();
      ts.forEach(o => {
        let key;
        if (o.u) {
          if (!units.has(o.u)) units.set(o.u, 'group ' + si + '.' + units.size);
          key = units.get(o.u);
        } else {
          let k = 0;
          for (let i = 0; i < heads.length; i++) {
            if (o.y < heads[i].y - 1) continue;
            const row = heads.filter(hh => Math.abs(hh.y - heads[i].y) <= 6);
            if (row.length > 1) {                      // a row of panels: take the one this text sits under
              const own = row.filter(hh => hh.x <= o.x + 2).pop() || row[0];
              if (own !== heads[i]) continue;
            }
            k = i + 1;
          }
          key = 'panel ' + si + '.' + k;
        }
        panels[key] = (panels[key] || '') + ' ' + o.t.textContent;
      });
    });
    const panelCount = Object.keys(panels).length;
    const blocks = Object.assign(panels, {
      key: [...f.querySelectorAll('.fkey .key')].map(k => k.textContent).join(' '), caption });
    Object.entries(blocks).forEach(([name, txt]) => {
      const hits = {};
      (txt.match(NAME_RE) || []).forEach(m => {
        if (NOT_A_NAME.has(m.toLowerCase())) return;
        hits[m] = (hits[m] || 0) + 1;
      });
      const most = name === 'caption' ? 2 : 1;      // labels name a thing once; a caption's prose may repeat it
      const where = /^(panel|group) /.test(name) ? (panelCount > 1 ? name : 'drawing') : name;
      Object.entries(hits).filter(([, c]) => c > most).forEach(([m, c]) =>
        add('name-twice', f, m, 'named ' + c + ' times in the ' + where));
    });
  }

  // Marks that cross a label. Asked for as "avoid overlap of arrows with text" (2026-11-22). One figure's
  // panel-A arrow runs through panel B's title, and the cAMP blob sits on PKA's R.
  // A stroke is judged on its own geometry, sampled along its length: a diagonal arrow's bounding box covers
  // a great deal it never paints. A fill is judged by sampling the label's box. A shape that CONTAINS the
  // whole label is the house style for systems figures (the protein's name sits inside its glyph), and a
  // label with a paper halo is the sanctioned fix, so neither counts.
  const HALO = t => {
    const c = getComputedStyle(t);
    return /stroke/.test(c.paintOrder || '') && c.stroke && c.stroke !== 'none' && c.strokeWidth !== '0px';
  };
  const TEXT_INSET = 2;        // a leader may stop at the label's edge; only the inside counts as a crossing
  const ATOM = /^(?:[HCNOPSF]|Cl|Br|Na|Mg|Zn|Cu|Fe|HN|NH|HO|OH|H[\u2080-\u2089\d]?N|N[\u2080-\u2089\d]?H[\u2080-\u2089\d]?|CH[\u2080-\u2089\d]?|H[\u2080-\u2089\d]?C|COOH|HOOC|SH|PO[\u2080-\u2089\d]?|SO[\u2080-\u2089\d]?)[\u2080-\u2089\d'\u2032]*$/;

  // Every stroked mark in one drawing, as points in client space, sampled about every 2 px of its length.
  function strokePoints(svg) {
    const out = [];
    svg.querySelectorAll('path,line,polyline,polygon').forEach(e => {
      if (e.closest(SKIP_PAINT) || !seenMark(e)) return;
      const st = getComputedStyle(e);
      if (!st.stroke || st.stroke === 'none' || st.strokeWidth === '0px') return;
      let len, m;
      try { len = e.getTotalLength(); m = e.getScreenCTM(); } catch (err) { return; }
      if (!len || !m || len > 40000) return;
      const step = Math.max(2, len / 600), pts = [];
      for (let d = 0; d <= len; d += step) {
        let q; try { q = e.getPointAtLength(d); } catch (err) { break; }
        const z = new DOMPoint(q.x, q.y).matrixTransform(m);
        pts.push([z.x, z.y]);
      }
      if (pts.length) out.push({ el: e, pts });
    });
    return out;
  }

  // A label's own oriented box, inset, in client space. An axis-aligned box around a 45-degree column head
  // is a large empty square, and a table rule passing under the head crosses the square without touching a
  // glyph (Figure 21's seven column heads, 2026-11-22). Same trap as the overlap rule's rotated labels.
  function textQuad(t, inset) {
    let g, m;
    try { g = t.getBBox(); m = t.getScreenCTM(); } catch (e) { return null; }
    if (!g || !m || g.width <= 0 || g.height <= 0) return null;
    const sc = Math.hypot(m.a, m.b) || 1;
    const i = Math.min(inset / sc, g.width / 3, g.height / 3);
    const x0 = g.x + i, x1 = g.x + g.width - i, y0 = g.y + i, y1 = g.y + g.height - i;
    const pt = (x, y) => { const z = new DOMPoint(x, y).matrixTransform(m); return [z.x, z.y]; };
    return { quad: [pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)],
             grid: (() => { const out = [];
               for (let r = 1; r <= 5; r++) for (let c = 1; c <= 3; c++)
                 out.push(pt(x0 + (x1 - x0) * r / 6, y0 + (y1 - y0) * c / 4));
               return out; })(),
             corners: [pt(g.x, g.y), pt(g.x + g.width, g.y), pt(g.x + g.width, g.y + g.height), pt(g.x, g.y + g.height)],
             low: y0 + (y1 - y0) * 0.72, m };
  }
  // point inside a convex quad, by consistent cross-product sign
  function inQuad(p, q) {
    let pos = 0, neg = 0;
    for (let i = 0; i < q.length; i++) {
      const c = q[i], d = q[(i + 1) % q.length];
      const z = (d[0] - c[0]) * (p[1] - c[1]) - (d[1] - c[1]) * (p[0] - c[0]);
      if (z > 0) pos++; else if (z < 0) neg++;
    }
    return !(pos && neg);
  }

  function markOnText(f, svg, ts, add) {
    const strokes = strokePoints(svg);
    const fills = shapesOf(svg).filter(sh => {
      const st = getComputedStyle(sh.el);
      return st.fill && st.fill !== 'none' && !/rgba\(.*,\s*0\)$/.test(st.fill);
    });
    ts.forEach(t => {
      if (HALO(t) || ATOM.test(t.textContent.trim())) return;
      const Q = textQuad(t, TEXT_INSET);
      if (!Q) return;
      const b = t.getBoundingClientRect();
      const named = new Set();
      const say = (el, how) => { named.add(el);
        add('mark-on-text', f, t.textContent.replace(/\s+/g, ' ').trim(), how); };

      strokes.forEach(sp => {
        if (named.has(sp.el) || t.contains(sp.el) || sp.el.contains(t)) return;
        const inside = sp.pts.filter(q => inQuad(q, Q.quad));
        if (!inside.length) return;
        // an underline runs the length of the name along its foot; a stroke clipping a corner does not
        const local = inside.map(q => { const z = new DOMPoint(q[0], q[1]).matrixTransform(Q.m.inverse()); return [z.x, z.y]; });
        const ys = local.map(q => q[1]), xs = local.map(q => q[0]);
        const g2 = t.getBBox();
        const underline = inside.length >= 3 && ys.every(y => y >= Q.low)
          && Math.max(...ys) - Math.min(...ys) < 3
          && Math.max(...xs) - Math.min(...xs) > g2.width * 0.4;
        if (!underline) say(sp.el, 'a ' + sp.el.tagName + ' stroke runs through it ('
          + inside.length + ' sampled points inside)');
      });

      fills.forEach(sh => {
        if (named.has(sh.el) || sh.el.contains(t) || t.contains(sh.el)) return;
        if (!(sh.box.left < b.right && sh.box.right > b.left && sh.box.top < b.bottom && sh.box.bottom > b.top)) return;
        let inv; try { inv = sh.el.getScreenCTM().inverse(); } catch (e) { return; }
        const inFill = ([x, y]) => { const q = new DOMPoint(x, y).matrixTransform(inv);
          try { return sh.el.isPointInFill(q); } catch (e) { return false; } };
        const n = Q.grid.filter(inFill).length;
        if (Q.corners.every(inFill) || n >= Q.grid.length * 0.9) return;   // the label sits inside its glyph
        if (n >= 2) say(sh.el, 'a ' + sh.el.tagName + ' fill covers part of it (' + n + ' of 15 sampled points)');
      });
    });
  }

  // An axis is a long straight hairline with at least three ticks on it. Its label must carry a unit.
  function axesOf(svg) {
    const sb = svg.getBoundingClientRect();
    const marks = [...svg.querySelectorAll('line,path,rect')].filter(e => !e.closest(SKIP_PAINT) && seenMark(e))
      .map(e => ({ el: e, b: e.getBoundingClientRect() }));
    const ticks = marks.filter(m => (m.b.width <= 3 && m.b.height >= 3 && m.b.height <= 12) ||
      (m.b.height <= 3 && m.b.width >= 3 && m.b.width <= 12));
    const out = [];
    marks.forEach(m => {
      const horiz = m.b.height <= 3 && m.b.width >= sb.width * 0.4;
      const vert = m.b.width <= 3 && m.b.height >= sb.height * 0.4;
      if (!horiz && !vert) return;
      const n = ticks.filter(t => t !== m && (horiz
        ? Math.abs((t.b.top + t.b.bottom) / 2 - (m.b.top + m.b.bottom) / 2) < 10 && t.b.left >= m.b.left - 4 && t.b.right <= m.b.right + 4
        : Math.abs((t.b.left + t.b.right) / 2 - (m.b.left + m.b.right) / 2) < 10 && t.b.top >= m.b.top - 4 && t.b.bottom <= m.b.bottom + 4)).length;
      if (n >= 3) out.push({ dir: horiz ? 'x' : 'y', box: m.b, ticks: n });
    });
    return out;
  }

  function chartRules(f, add) {
    let axes = 0, bars = 0;
    drawings(f).forEach(svg => {
      const ts = texts(svg);
      axesOf(svg).forEach(ax => {
        axes++;
        const near = ts.filter(t => inBand(ax, t.getBoundingClientRect()));
        const labelled = near.some(t => UNIT.test(t.textContent) && words(t.textContent).length >= 1) ||
          UNIT.test(svg.getAttribute('aria-label') || '');
        if (!labelled) add('axis-unlabelled', f, ax.dir + ' axis (' + ax.ticks + ' ticks)',
          'no label with a unit within reach of the axis');
      });
      // bars: three or more painted rects on one baseline
      const base = {};
      [...svg.querySelectorAll('rect')].filter(e => !e.closest(SKIP_PAINT) && seenMark(e)).forEach(e => {
        const b = e.getBoundingClientRect();
        if (b.width < 3 || b.height < 6) return;
        const k = Math.round(b.bottom);
        base[k] = (base[k] || 0) + 1;
      });
      bars += Object.values(base).filter(c => c >= 3).length;
    });
    const money = /(\$|US\$|USD|\bper month\b|\bprice\b|\binflows?\b|\bsales\b|\bcost\b)/i.test(f.textContent || '');
    const measured = /(\bnmol|\u00b5mol|\u00b5g|\bmg\b|\bng\b|\bnM\b|\u00b5M\b|\bkDa\b|\bDa\b|\bfold\b|\b%\b|\bper cm|\/cm|\bresidues?\b|\bhalf-life\b|\bt\u00bd)/i.test(f.textContent || '');
    // A figure that says it is a schematic plots no measurement, so it owes no n (a figure captioned
    // "Schematic, not to scale").
    const schematic = /\bschematic\b|\bnot to scale\b|\bcartoon\b/i.test(f.textContent || '');
    if ((axes || bars) && measured && !money && !schematic && !NSTAT.test((f.textContent || ''))) {
      add('no-n', f, figureName(f) + (axes ? ' (' + axes + ' axes)' : ' (bars)'),
        'a measurement is plotted with no n and no error definition');
    }
  }

  /* ---------- clipping ---------- */

  // The visually-hidden idiom: present for assistive tech, painted nowhere. Measuring it reported every chapter
  // summary as truncated by an ellipsis it has no reader for.
  const srOnly = el => {
    const st = getComputedStyle(el);
    if (st.clip === 'rect(0px, 0px, 0px, 0px)') return true;
    if (/inset\(\s*(50%|100%)/.test(st.clipPath)) return true;
    const b = el.getBoundingClientRect();
    return st.position === 'absolute' && (b.width <= 1.5 || b.height <= 1.5);
  };

  const TEXTY = el => {
    for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) return true;
    return false;
  };
  function textBoxes() {
    const out = [];
    document.querySelectorAll('body *').forEach(el => {
      if (el.closest('script,style,#__out,template')) return;
      if (el.tagName === 'text' || el.namespaceURI === 'http://www.w3.org/2000/svg') {
        if (el.tagName !== 'text') return;
      } else if (!TEXTY(el)) return;
      if (!seen(el) || srOnly(el)) return;
      out.push(el);
    });
    return out;
  }
  const label = el => (el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className
    ? '.' + el.className.trim().split(/\s+/)[0] : '')) + ' | ' + (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 46);
  const figOf = el => { const f = el.closest('figure.fig,section,header,nav,footer'); return f ? (f.id || f.tagName.toLowerCase()) : 'page'; };

  function clipFindings(els, W, add) {
    els.forEach(el => {
      const b = el.getBoundingClientRect();
      const st = getComputedStyle(el);

      // past an ancestor that hides its overflow (a scrolling ancestor is the reader's own pan, not clipping)
      for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
        if (p.tagName.toLowerCase() === 'svg') continue;   // an svg's own clip is the clip-viewbox rule's business
        const ps = getComputedStyle(p);
        const hid = d => /^(hidden|clip)$/.test(d);
        if (!hid(ps.overflowX) && !hid(ps.overflowY)) continue;
        const pb = p.getBoundingClientRect();
        const over = [];
        if (hid(ps.overflowX)) { if (b.right > pb.right + 1) over.push('right by ' + Math.round(b.right - pb.right)); if (b.left < pb.left - 1) over.push('left by ' + Math.round(pb.left - b.left)); }
        if (hid(ps.overflowY)) { if (b.bottom > pb.bottom + 1) over.push('bottom by ' + Math.round(b.bottom - pb.bottom)); if (b.top < pb.top - 1) over.push('top by ' + Math.round(pb.top - b.top)); }
        if (over.length) { add('clip-ancestor', el, over.join(', ') + ' px past ' + label(p).split(' | ')[0]); break; }
      }

      // cut by its own overflow box: with no ellipsis the reader gets no sign the text goes on
      const ownHid = d => /^(hidden|clip)$/.test(d);
      if (ownHid(st.overflowX) && st.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth + 1)
        add('clip-ancestor', el, 'its own overflow:hidden cuts ' + (el.scrollWidth - el.clientWidth) + ' px of text, with no ellipsis');

      // truncated in place
      const clamp = st.webkitLineClamp && st.webkitLineClamp !== 'none';
      if (st.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1)
        add('clip-ellipsis', el, 'ellipsis cuts ' + (el.scrollWidth - el.clientWidth) + ' px of text');
      else if (clamp && el.scrollHeight > el.clientHeight + 1)
        add('clip-ellipsis', el, 'line-clamp ' + st.webkitLineClamp + ' cuts ' + (el.scrollHeight - el.clientHeight) + ' px');

      // past the viewport, unless a scrolling box holds it on purpose
      const scroller = (() => {
        for (let p = el.parentElement; p; p = p.parentElement) {
          const o = getComputedStyle(p).overflowX;
          if (/^(auto|scroll)$/.test(o) && p.scrollWidth > p.clientWidth + 1) return p;
        }
        return null;
      })();
      if (!scroller) {
        if (b.right > W + 1) add('clip-viewport', el, Math.round(b.right - W) + ' px past the right edge');
        if (b.left < -1) add('clip-viewport', el, Math.round(-b.left) + ' px past the left edge');
      }

      // NOT MEASURED: text running out of the box drawn around it. Figure 28's step card held a 140 px
      // subtitle in a 132 px card and crossed its stroke at every width, which no svg-edge rule catches, so
      // the rule is worth having — but "a container" is the hard part. Smallest enclosing <rect> read every
      // bead as a box (28 false positives); requiring the rect to hold another mark still left 17, because a
      // highlight band behind a bead run holds the beads. A real version needs the container to be declared
      // (a class, a role) or inferred from holding a whole group. Until then, measure a suspect figure
      // directly: compare each label's box with the card rect it sits in (scratchpad probe, 2026-11-22).

      // an svg label cut off at its drawing's edge. An svg clips its own overflow, so this is the clip that
      // getBBox cannot see: bbox is in the label's own coordinates, and a transform (a rotated residue name)
      // makes it read as far outside a viewBox it sits well inside.
      if (el.tagName === 'text') {
        const svg = el.closest('svg');
        if (svg) {
          const sb = svg.getBoundingClientRect(), tb = el.getBoundingClientRect();
          const out = [];
          if (tb.left < sb.left - 1) out.push('left by ' + Math.round(sb.left - tb.left));
          if (tb.right > sb.right + 1) out.push('right by ' + Math.round(tb.right - sb.right));
          if (tb.top < sb.top - 1) out.push('top by ' + Math.round(sb.top - tb.top));
          if (tb.bottom > sb.bottom + 1) out.push('bottom by ' + Math.round(tb.bottom - sb.bottom));
          if (out.length) add('clip-viewbox', el, out.join(', ') + ' px past the edge of its drawing');
        }
      }
    });
  }

  // Text over text, measured on what is painted. An element's bounding box is the union of its lines, so a
  // caption's <b> appears to sit under the reference marker on its last line and a wrapped key entry appears to
  // sit on its neighbours; per-line rects end both. An svg label's box is axis-aligned, so a rotated residue
  // name appears to collide with the one beside it; its own oriented quad ends that.
  function quadsOf(el, vis) {
    const q = [];
    const keep = p => {
      const xs = p.map(c => c[0]), ys = p.map(c => c[1]);
      const bb = { left: Math.min(...xs), right: Math.max(...xs), top: Math.min(...ys), bottom: Math.max(...ys) };
      if (bb.right - bb.left < 1 || bb.bottom - bb.top < 1) return;
      const o = inter(bb, vis);
      if (o.width > 0.5 && o.height > 0.5) q.push({ p, bb });
    };
    if (el.tagName === 'text') {
      let b, m;
      try { b = el.getBBox(); m = el.getScreenCTM(); } catch (e) { return q; }
      if (!b || !m) return q;
      const pt = (x, y) => { const z = new DOMPoint(x, y).matrixTransform(m); return [z.x, z.y]; };
      keep([pt(b.x, b.y), pt(b.x + b.width, b.y), pt(b.x + b.width, b.y + b.height), pt(b.x, b.y + b.height)]);
      return q;
    }
    const r = document.createRange();
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      r.selectNodeContents(n);
      for (const c of r.getClientRects()) keep([[c.left, c.top], [c.right, c.top], [c.right, c.bottom], [c.left, c.bottom]]);
    }
    return q;
  }

  // Shoelace area, and one winding for every polygon so the clip below keeps the inside, not the outside.
  function polyArea(p) {
    let s2 = 0;
    for (let i = 0; i < p.length; i++) { const c = p[i], d = p[(i + 1) % p.length]; s2 += c[0] * d[1] - d[0] * c[1]; }
    return Math.abs(s2) / 2;
  }
  const wound = p => {
    let s2 = 0;
    for (let i = 0; i < p.length; i++) { const c = p[i], d = p[(i + 1) % p.length]; s2 += c[0] * d[1] - d[0] * c[1]; }
    return s2 < 0 ? [...p].reverse() : p;
  };

  // Sutherland-Hodgman: the area two convex quads share.
  function shared(a0, b0) {
    const b = wound(b0);
    let poly = wound(a0);
    for (let i = 0; i < b.length; i++) {
      const p1 = b[i], p2 = b[(i + 1) % b.length];
      const side = pt => (p2[0] - p1[0]) * (pt[1] - p1[1]) - (p2[1] - p1[1]) * (pt[0] - p1[0]);
      const next = [];
      for (let j = 0; j < poly.length; j++) {
        const c = poly[j], d = poly[(j + 1) % poly.length], sc = side(c), sd = side(d);
        if (sc >= 0) next.push(c);
        if ((sc < 0 && sd > 0) || (sc > 0 && sd < 0)) {
          const t = sc / (sc - sd);
          next.push([c[0] + t * (d[0] - c[0]), c[1] + t * (d[1] - c[1])]);
        }
      }
      poly = next;
      if (!poly.length) return 0;
    }
    return polyArea(poly);
  }

  const OVERLAP_SHARE = 0.2;   // a fifth of the smaller run: deeper than any leading, shallower than a collision

  function overlapFindings(els, add) {
    const runs = [];
    els.forEach(el => {
      const vis = visibleBox(el);
      if (!vis) return;
      quadsOf(el, vis).forEach(q => runs.push({ el, p: q.p, bb: q.bb, a: polyArea(q.p) }));
    });
    runs.sort((x, y) => x.bb.top - y.bb.top);
    const said = new Set();
    for (let i = 0; i < runs.length; i++) {
      for (let j = i + 1; j < runs.length; j++) {
        const a = runs[i], c = runs[j];
        if (c.bb.top > a.bb.bottom) break;
        if (a.el === c.el || a.el.contains(c.el) || c.el.contains(a.el)) continue;
        const o = inter(a.bb, c.bb);
        if (o.width <= 0 || o.height <= 0) continue;
        const sh = shared(a.p, c.p);
        if (sh < Math.min(a.a, c.a) * OVERLAP_SHARE) continue;
        const k = label(a.el) + '\u241f' + label(c.el);
        if (said.has(k)) continue;
        said.add(k);
        add('text-overlap', a.el, 'overlaps ' + label(c.el) + ' over ' + Math.round(sh) + ' px\u00b2, '
          + Math.round(sh / Math.min(a.a, c.a) * 100) + '% of the smaller run');
      }
    }
  }

  /* ---------- entry points ---------- */

  const idOf = el => { const f = el && el.closest && el.closest('figure.fig'); return f ? f.id : ''; };

  function collector(out, ctx) {
    return (rule, where, text, detail) => {
      const el = where && where.nodeType === 1 ? where : null;
      const fig = el ? (el.classList.contains('fig') ? figureName(el) : figOf(el)) : String(where);
      out.push(Object.assign({ rule, fig, id: el ? idOf(el) : '', text: String(text).slice(0, 110), detail }, ctx));
    };
  }

  window.__figlint = {
    figures() {
      const out = [];
      const add = collector(out, {});
      document.querySelectorAll('figure.fig').forEach(f => {
        const drawn = drawings(f).reduce((k, svg) => k + texts(svg).length, 0);
        if (!drawn && f.querySelector('svg text')) {
          add('unmeasurable', f, f.id || '?',
            'the drawing has svg text but none of it measured as painted: a closed fold, display:none, or a '
            + 'zero box. Nothing below is a verdict on this figure.');
          return;
        }
        textRules(f, add); chartRules(f, add);
      });
      return out;
    },
    clip(W, theme) {
      const out = [];
      const add = (rule, el, detail) => out.push({ rule, fig: figOf(el), id: idOf(el), text: label(el), detail, w: W, theme });
      const els = textBoxes();
      clipFindings(els, W, add);
      overlapFindings(els, add);
      return out;
    },
    // Opens each hover card in turn and measures only what the card itself paints.
    tips(W, theme) {
      const out = [];
      const add = (rule, el, detail) => out.push({ rule, fig: figOf(el), id: idOf(el), text: label(el), detail, w: W, theme, tip: true });
      const hosts = [...document.querySelectorAll('[data-tip]')].filter(seen);
      hosts.forEach(h => {
        const r = h.getBoundingClientRect();
        ['mouseenter', 'mouseover', 'focus', 'focusin'].forEach(type => {
          h.dispatchEvent(new MouseEvent(type, { bubbles: type !== 'mouseenter', clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }));
        });
        h.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }));
        const cards = [...document.querySelectorAll('.stip,.tip,[role=tooltip],#tip')].filter(seen);
        cards.forEach(c => {
          clipFindings([c, ...[...c.querySelectorAll('*')].filter(e => TEXTY(e) && seen(e))], W, add);
        });
        ['mouseleave', 'mouseout', 'blur', 'focusout'].forEach(type => h.dispatchEvent(new MouseEvent(type, { bubbles: type !== 'mouseleave' })));
      });
      return out;
    },
    expected() {
      const o = {};
      document.querySelectorAll('figure.fig[data-expect]').forEach(f => {
        o[f.id] = f.dataset.expect.split(/\s+/).filter(Boolean);
      });
      return o;
    },
    open() { document.querySelectorAll('details').forEach(d => { d.open = true; }); return document.querySelectorAll('details').length; }
  };
})();
