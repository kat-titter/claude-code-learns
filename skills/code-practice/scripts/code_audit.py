#!/usr/bin/env python3
"""Audit a repo's code against design rules carried over to code; exit 1 if any rule fails.

Each check is a page-design rule read as a code rule:
  focus   one focal point per view      -> one job per function, files a reader can hold
  once    each fact once                -> no block of code living in two places
  front   the page opens with its point -> a README that names files which exist, and the entry points
  clutter erase chartjunk               -> no v2/_old/final files, no commented-out code
  space   negative space groups things  -> a top level short enough to read at a glance
  legend  every figure has a caption    -> every script opens with a line saying what it does
  light   embedded media stays small    -> no heavy binaries tracked in git

Usage: code_audit.py REPO [REPO ...] [--detail N] [--fn-lines 60] [--file-lines 500] [--dup-lines 8]
Function length for JS is found by brace matching, so it is approximate; Python uses the AST.
"""
import argparse
import ast
import hashlib
import os
import re
import subprocess
import sys
from collections import defaultdict

CODE_EXT = {".py", ".js", ".mjs", ".sh", ".css"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".mp3", ".wav", ".flac", ".mp4", ".mov",
              ".zip", ".npy", ".npz", ".pt", ".ckpt", ".safetensors", ".onnx", ".sdf"}
SKIP_PARTS = {"node_modules", "vendor", ".git", "archive", "history", "dist", "build"}
VERSION_NAME = re.compile(r"(^|[_\-.])(v\d+|old|new|final\d*|copy|backup|bak|tmp|test\d+)([_\-.]|$)", re.I)
COMMENTED_CODE = {
    "#": re.compile(r"^\s*#\s*(import |from \S+ import|def |class |print\(|return\b|if .*:$|for .*:$|\w+\s*=[^=]|\w+\(.*\)$)"),
    "//": re.compile(r"^\s*//\s*(const |let |var |function |return\b|if ?\(|for ?\(|\w+\s*=[^=]|[\w.]+\(.*\);?$)"),
}
PROSE_RUN = re.compile(r"\b[a-zA-Z]+(?: [a-zA-Z]+){3}\b")  # four bare words in a row: a sentence, not code
WRITES = re.compile(r"write_text\(|\.write\(|open\([^)]*['\"]w|>\s*\S+\.html")
BUILT_README = re.compile(r"built pages|generated|do not edit|written by", re.I)
GENERATED_HEAD = re.compile(r"generated|do not edit", re.I)
LOCAL_ONLY = re.compile(r"local only|not in git|out of git|gitignored|ignored by git", re.I)
SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S | re.I)
STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
JS_FN_START = re.compile(r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|\w+\s*=>))")


def tracked_files(repo):
    out = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f]


def skipped(path):
    return bool(SKIP_PARTS & set(path.split("/"))) or path.endswith(".min.js")


def read(repo, path, limit=-1):
    with open(os.path.join(repo, path), encoding="utf-8", errors="replace") as fh:
        return fh.read(limit)


def generated_pages(repo, files):
    """Map each generated HTML page to what makes it: a .src sibling, a script here that writes it, or the README."""
    pages = {f for f in files if f.endswith(".html")}
    made = {f: f.replace(".src.html", ".html") for f in pages if f.endswith(".src.html")}
    made = {out: f"{src} (source)" for src, out in made.items() if out in pages}
    made.update({f: "its own header" for f in files if os.path.splitext(f)[1] in CODE_EXT and not skipped(f)
                 and GENERATED_HEAD.search(read(repo, f, 300).split("\n", 2)[0])})
    for script in (f for f in files if f.endswith((".py", ".sh")) and not skipped(f)):
        lines = read(repo, script).splitlines()
        writes = [i for i, l in enumerate(lines) if WRITES.search(l)]
        for page in pages - set(made) - {p for p in pages if p.endswith(".src.html")}:
            name = os.path.basename(page)
            named = [i for i, l in enumerate(lines) if name in l]
            # written within three lines of where it is named, or through a variable that holds its name
            names = {m.group(1) for i in named for m in [re.match(r"\s*(\w+)\s*=", lines[i])] if m}
            if any(abs(w - i) <= 3 for w in writes for i in named) or \
                    any(re.search(rf"\b{v}\b", lines[w]) for w in writes for v in names):
                made[page] = script
    readme = next((f for f in files if f.lower() == "readme.md"), None)
    if readme:
        for line in read(repo, readme).splitlines():
            if BUILT_README.search(line):
                named = [p for p in pages if os.path.basename(p) in line] or (sorted(pages) if "built pages" in line else [])
                made.update({p: "README" for p in named if p not in made and not p.endswith(".src.html")})
    return made


def code_units(repo, files, generated=()):
    """Yield (path, kind, first_line, text) for each block of code: whole code files and inline HTML blocks."""
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if skipped(f) or f in generated or (ext not in CODE_EXT and ext != ".html"):
            continue
        try:
            text = open(os.path.join(repo, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if ext != ".html":
            yield f, ext, 1, text
            continue
        for rx, kind in ((SCRIPT_RE, ".js"), (STYLE_RE, ".css")):
            for m in rx.finditer(text):
                yield f, kind, text.count("\n", 0, m.start(1)) + 1, m.group(1)


def python_functions(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [(n.name, n.lineno, n.end_lineno - n.lineno + 1)
            for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def js_functions(text):
    """Find named JS functions and their length by matching the braces after each start."""
    found = []
    for m in JS_FN_START.finditer(text):
        brace = text.find("{", m.end())
        if brace < 0 or text.count("\n", m.end(), brace) > 2:
            continue
        depth, i, quote = 0, brace, None
        while i < len(text):
            c = text[i]
            if quote:
                if c == "\\":
                    i += 1
                elif c == quote:
                    quote = None
            elif c in "'\"`":
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        start = text.count("\n", 0, m.start()) + 1
        found.append((m.group(1) or m.group(2), start, text.count("\n", m.start(), i) + 1))
    return found


def check_focus(units, fn_max, file_max):
    hits = []
    for path, kind, off, text in units:
        n_lines = text.count("\n") + 1
        if kind in {".py", ".js", ".mjs"} and n_lines > file_max:
            hits.append((path, off, f"{n_lines} lines of {kind[1:]} in one {'block' if path.endswith('.html') else 'file'}"))
        fns = python_functions(text) if kind == ".py" else js_functions(text) if kind in {".js", ".mjs"} else []
        hits += [(path, off + line - 1, f"{name}() {length} lines") for name, line, length in fns if length > fn_max]
    return hits


def normalise(line, kind):
    s = line.strip()
    if not s or s.startswith(("#", "//", "/*", "*")) and kind != ".css":
        return None
    return re.sub(r"\s+", " ", s) if len(s) > 3 else None


def check_once(units, min_lines):
    """Find blocks of min_lines meaningful lines that appear in two or more places."""
    windows = defaultdict(list)
    for path, kind, off, text in units:
        lines = [(off + i, normalise(l, kind)) for i, l in enumerate(text.splitlines())]
        lines = [(n, s) for n, s in lines if s]
        for i in range(len(lines) - min_lines + 1):
            chunk = "\n".join(s for _, s in lines[i:i + min_lines])
            if len(chunk) >= 25 * min_lines:
                windows[hashlib.sha1(chunk.encode()).hexdigest()].append((path, lines[i][0]))
    pairs = defaultdict(set)
    for locs in windows.values():
        if len(locs) > 1:
            first = locs[0]
            for other in locs[1:]:
                pairs[(first[0], other[0])].add((first[1], other[1]))
    hits = []
    for (a, b), starts in sorted(pairs.items(), key=lambda kv: -len(kv[1])):
        la, lb = min(starts)
        hits.append((a, la, f"{len(starts) + min_lines - 1}+ lines shared with {b}:{lb}"))
    return hits


def check_front(repo, files):
    readme = next((f for f in files if f.lower() in {"readme.md", "readme"}), None)
    if not readme:
        return [(".", 1, "no README at the top level")]
    text = open(os.path.join(repo, readme), encoding="utf-8", errors="replace").read()
    hits, tracked = [], set(files)
    for f in files:
        while "/" in f:
            f = f.rsplit("/", 1)[0]
            tracked.add(f)
    for n, line in enumerate(text.splitlines(), 1):
        if LOCAL_ONLY.search(line):
            continue
        # a link, or a backticked path with a folder in it; a bare `CLAUDE.md` in prose may name a file elsewhere
        for ref in re.findall(r"`([\w.-]+/[\w./-]+)`|\]\((?!https?:|#|mailto:)([\w./%-]+)\)", line):
            ref = (ref[0] or ref[1]).split("#")[0].replace("%20", " ").rstrip("/")
            ref = ref[2:] if ref.startswith("./") else ref
            # `results/e16` may name a family of files (e16-*.json), so a prefix match counts
            if ref and ref not in tracked and not any(f.startswith(ref) or f.endswith("/" + ref) for f in files):
                hits.append((readme, n, f"names {ref}, which is not in the repo"))
    top_code = [f for f in files if "/" not in f and os.path.splitext(f)[1] in CODE_EXT]
    hits += [(readme, 1, f"top-level {f} not mentioned") for f in top_code if f not in text]
    return hits


def check_clutter(units, files):
    hits = [(f, 1, "name carries a version, not a job") for f in files
            if not skipped(f) and VERSION_NAME.search(os.path.splitext(os.path.basename(f))[0])]
    for path, kind, off, text in units:
        rx = COMMENTED_CODE["#"] if kind in {".py", ".sh"} else COMMENTED_CODE["//"] if kind in {".js", ".mjs"} else None
        if rx:
            hits += [(path, off + i, "commented-out code: " + l.strip()[:60])
                     for i, l in enumerate(text.splitlines()) if rx.match(l) and is_code(l, kind)]
    return hits


def is_code(comment_line, kind):
    """A comment is dead code when its body parses (Python) and carries no run of plain words."""
    body = re.sub(r"^\s*(#|//)\s?", "", comment_line).rstrip()
    if comment_line.lstrip().startswith("#!") or PROSE_RUN.search(re.sub(r"\b(if|else|not|in|is|and|or|for|return)\b", "", body)):
        return False
    if kind == ".py":
        try:
            ast.parse(body.rstrip(":") + (":\n pass" if body.endswith(":") else ""))
        except SyntaxError:
            return False
    return True


def check_space(files, max_top):
    top = {f.split("/")[0] for f in files if not f.startswith(".")}
    return [(".", 1, f"{len(top)} entries at the top level (budget {max_top})")] if len(top) > max_top else []


def check_legend(repo, files):
    hits = []
    for f in files:
        ext = os.path.splitext(f)[1]
        if skipped(f) or ext not in {".py", ".sh", ".js", ".mjs"} or os.path.basename(f) == "__init__.py":
            continue
        head = open(os.path.join(repo, f), encoding="utf-8", errors="replace").read(800).lstrip()
        head = re.sub(r"^#!.*\n", "", head).lstrip()
        head = re.sub(r"^#.*coding[:=].*\n", "", head).lstrip()
        workflow_meta = re.match(r"export const meta = \{[^}]*description:", head, re.S)  # a Workflow script's caption
        if not head.startswith(('"""', "'''", "#", "//", "/*")) and not workflow_meta:
            hits.append((f, 1, "opens without a line saying what it does"))
    return hits


def check_light(repo, files, max_kb):
    hits, total = [], 0
    for f in files:
        if os.path.splitext(f)[1].lower() in BINARY_EXT:
            size = os.path.getsize(os.path.join(repo, f)) // 1024
            total += size
            if size > max_kb:
                hits.append((f, 1, f"{size / 1024:.1f} MB binary in git"))
    return hits, total


def audit(repo, args):
    files = tracked_files(repo)
    generated = generated_pages(repo, files)
    units = list(code_units(repo, files, generated))
    code_lines = sum(t.count("\n") + 1 for _, k, _, t in units if k != ".css")
    light, binary_kb = check_light(repo, files, args.binary_kb)
    return generated, {
        "focus": check_focus(units, args.fn_lines, args.file_lines),
        "once": check_once(units, args.dup_lines),
        "front": check_front(repo, files),
        "clutter": check_clutter(units, files),
        "space": check_space(files, args.top_level),
        "legend": check_legend(repo, files),
        "light": light,
    }, code_lines, binary_kb


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("repos", nargs="+")
    p.add_argument("--fn-lines", type=int, default=60, help="longest function, in lines")
    p.add_argument("--file-lines", type=int, default=500, help="longest .py/.js file or inline script")
    p.add_argument("--dup-lines", type=int, default=8, help="shortest duplicated block reported")
    p.add_argument("--top-level", type=int, default=15, help="most entries at the repo's top level")
    p.add_argument("--binary-kb", type=int, default=1024, help="largest binary file kept in git")
    p.add_argument("--detail", type=int, default=3, help="findings listed per rule per repo (0 = table only)")
    args = p.parse_args()

    rules = ["focus", "once", "front", "clutter", "space", "legend", "light"]
    print(f"{'repo':24} {'code ln':>8} {'bin MB':>7} {'gen':>4}  " + "  ".join(f"{r:>7}" for r in rules))
    results, failed = [], False
    for repo in args.repos:
        generated, res, code_lines, binary_kb = audit(repo, args)
        results.append((repo, generated, res))
        failed |= any(res.values())
        cells = "  ".join(f"{('ok' if not res[r] else len(res[r])):>7}" for r in rules)
        print(f"{os.path.basename(repo.rstrip('/')):24} {code_lines:>8} {binary_kb / 1024:>7.1f} {len(generated):>4}  {cells}")
    if args.detail:
        for repo, generated, res in results:
            shown = [(r, h) for r in rules for h in res[r][:args.detail]]
            if shown or generated:
                print(f"\n{os.path.basename(repo.rstrip('/'))}")
                for page, source in sorted(generated.items()):
                    print(f"  {'gen':7} {page}  made by {source}; judged at its source")
                for rule, (path, line, msg) in shown:
                    print(f"  {rule:7} {path}:{line}  {msg}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
