---
name: citations
description: Add or verify numbered citations / references / a bibliography in a document, especially HTML or web reports. Use when citing scientific papers or sources, building a reference list, formatting footnotes/endnotes, or when citation numbering needs to be trustworthy. Enforces two things that bite repeatedly — verify each source's real bibliographic details before citing, and keep in-text markers in sync with the reference list.
when_to_use: Whenever a document gains citations/references, or a numbered reference list's indexing needs to be trusted — especially in HTML, where separate ordered lists silently desync the numbers.
---

## 1. Verify before you cite — never from memory

Even canonical papers get volume/issue/pages/year wrong from memory. For each
source, web-verify: authors, year, exact title, journal, **volume(issue), pages,
DOI**. Confirm the DOI resolves. A neuroscience/technical audience *will* notice.

## 2. Numbered-citation markup (house style)

```html
in-text:  <sup class="ref"><a href="#r3">3</a></sup>
list:     <ol class="refs">
            <li id="r3">Author, A., &amp; Author, B. (year). Title. <i>Journal</i>,
              vol(iss), pp–pp. <a href="https://doi.org/...">doi:...</a></li>
          </ol>
```

## 3. The indexing gotcha (why this skill exists)

HTML `<ol>` auto-numbers, and **restarts at 1 in every separate `<ol>`**. If you
split references into grouped lists, the *visible* number desyncs from the `#rN`
id and the superscript — so a citation silently points at the wrong reference.
(Hit this twice across projects.)

**Rule:** the item with `id="rN"` must *visibly show* N, and every in-text
superscript must both *display* N and *link* to `#rN`. With a single `<ol>` this
is automatic. **Grouped lists are fine** (e.g. subheadings between groups) — just
set `start=` on each `<ol>` *after the first* to `(items so far) + 1`, so the
visible numbering continues. The first list needs no `start=` (it defaults to 1).
The failure mode is a 2nd+ `<ol>` **missing** `start=`: it silently restarts at 1,
so #r32 then shows "1".

## 4. Verify the indexing — don't eyeball it

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check-citations.py path/to/file.html
```
It computes each item's *displayed* number (its `<ol>`'s `start=` + position) and
checks it equals the id — so correct grouped lists pass and only genuine restarts
fail. Also flags: superscript ≠ its `#rN`, ids out of order, cited-but-missing
refs, and (as a note) refs listed but never cited. Exit 0 = clean, 1 = problems.
