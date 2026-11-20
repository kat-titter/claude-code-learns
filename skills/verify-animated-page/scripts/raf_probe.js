// Paste into the browser tool's javascript runner (REPL semantics: the last expression is returned).
// Is this page presenting frames right now? If rafPerSecond is ~0, the pane is throttling requestAnimationFrame:
// screenshots will show an old frame and time-based state will not advance. Wake it (a tiny screenshot), then re-run.
await new Promise((resolve) => {
  let n = 0; const t0 = performance.now();
  const f = () => { n++; if (performance.now() - t0 < 1000) requestAnimationFrame(f); else resolve(n); };
  requestAnimationFrame(f);
  setTimeout(() => resolve(n), 1500);          // rAF may never fire at all; return what was counted
}).then((n) => JSON.stringify({ rafPerSecond: n, visibility: document.visibilityState, focused: document.hasFocus() }));
