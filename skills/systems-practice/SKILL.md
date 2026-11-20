---
name: systems-practice
description: Runs software well on real machines - memory and precision, compression and light repos, logs that answer questions later, servers, tunnels and background jobs that survive, and privacy by default. Use when a job runs out of memory or swaps, a file or page is too big, a log is missing or noisy, a server or tunnel misbehaves, or personal data might leak.
when_to_use: Before a heavy run; before shipping a page with embedded media; when adding a server, tunnel or background job; before anything leaves the machine (a push, a publish, a shared link).
---

# Systems practice

Software lives on a machine with finite memory, a disk, a network and other people's data. Each section is a way to
respect one of those.

## Gotchas

- Base64 images or PDFs embedded in a page or repo ("repos should be memory efficient"): link, compress, or keep them local.
- A server or tunnel from an earlier session still holding the port: name ports and give each service one owner.
- Home paths, emails or names in logs, URLs or commits: scrub before anything leaves the machine.

## Memory

- **Size before you run**: model weights times precision plus activations; know the peak before the job starts.
- **Use the lowest precision that stays correct**: fp16 for weights where it holds, fp32 where it NaNs or drifts.
  (An image pipeline on Apple silicon, 2026-10-25: UNet and text encoder in fp16, the VAE kept in fp32, attention
  slicing off because it produced NaNs in fp16 on MPS.)
- **Stream rather than load**: iterate files, chunks and frames; memory-map large arrays; write results as they finish.
- **Free what is done** (delete references, empty device caches) and run one heavy job at a time on a shared machine
  (macos-long-render for load, swap and threads).
- **Size a worker pool from measurements, then watch it**: one unit's peak times the workers, plus every Claude session
  and agent, must fit with headroom. On a Mac, macos-long-render holds the formula and `mem-watch.py`, which pauses the
  newest worker before memory runs out (2026-11-19: a five-worker rebuild beside several sessions took the Mac down).

## Compression

- **Pick the format for the content**: WebP or AVIF for images, H.264/HEVC or WebM for video, Parquet or compressed
  NumPy for tables and arrays, gzip/brotli on served text.
- **Embed sparingly**: base64 data URIs grow a file by a third and block caching; link assets unless the page must be
  one file, and then downscale first.
- **Parse embedded data with a real parser** (a JSON decoder, an HTML parser), since delimiters appear inside the data. (2026-10-15: splitting on ";" stopped inside
  "data:image/webp;base64" and the overwrite cost a seven-minute rebuild; use `json.JSONDecoder().raw_decode`.)
- **Repos stay light**: binaries, renders and models live outside git, as release assets or on disk (github-practice).

## Logging

- **Log to answer tomorrow's question**: what ran, with which inputs and settings, how long it took, what it wrote
  and where; one line per step, timestamped, with the run's id.
- **Levels on purpose**: info for milestones, debug behind a flag, errors with the value that broke and the next step.
- **Machine-readable where scripts read it**: JSON lines for anything a waiter or dashboard parses; a format change is
  an interface change. (2026-10-09: 14 waiters polled for days because a log format changed and their pattern never
  matched.)
- **Keep secrets and personal data out of logs**; redact at the source.

## Infrastructure

- **Every waiter has a deadline**: a timeout or a loop counter, and a loud message when it expires.
- **One owner per service and port**: a named process, a known port, a pid file or a supervisor; stop what you start.
- **Long jobs stay awake and resumable** (macos-long-render; work-practice, "Do each piece of work once").
- **Shell scripts quote and use arrays** for lists of arguments; zsh does not word-split `$VAR` the way bash does
  (2026-10-06: a list of ids passed as one string crashed a parser).
- **Tunnels and public addresses are deliberate**: named, temporary by default, and on a personal domain only with
  the owner's yes.

## Privacy

- **Personal data stays out of code, logs, URLs and history**: names, emails, home paths, hostnames, private links.
  Commit with a no-reply identity (github-practice). (2026-10-26: a public repo's history carried a laptop hostname as
  the author address on 15 commits.)
- **Local first**: process private data on the machine; send only what the task needs, to services the person chose.
- **Public only on purpose**: an audit of the whole history and the owner's yes before a repo, page or tunnel opens.

## Related

code-practice (clean code, refactors), debug-practice (finding bugs), github-practice (history, identity, publishing),
macos-long-render (shared machines, sleep, thermal), work-practice (resume points, rebuild safely).

## Provenance

2026-10-26: "computer skills: memory efficiency, privacy, infrastructure, logging, bug finding and debugging, refactors,
compression"; cases from the lessons inbox and project memory.
