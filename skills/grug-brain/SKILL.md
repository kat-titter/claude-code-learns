---
name: grug-brain
description: Keeps complexity out of software the grug-brained way - say no or build the 80/20 version, factor late once cut points show, a working demo before an architecture, integration tests, refactors close to shore, and "too complex for me" said out loud. Use when deciding whether to add a feature, abstraction, service or dependency.
when_to_use: When a plan feels over-engineered; on "too complex", "do we really need this", "keep it simple", "80/20", "YAGNI" or "why is this so hard to change".
---

# Grug brain

"complexity very, very bad." The Grug Brained Developer (grugbrain.dev, by the author of htmx) is a long programming
life's lessons told by a developer who stopped pretending to be big brained: complexity is the apex predator of
software, it enters through well-meaning abstractions, and the weapons against it are small and unglamorous. In the
order the work runs: decide whether to build at all (§1), let the shape emerge before the structure (§2), test where
tests pay (§3), change what runs with care (§4), write for the debugger (§5), run it with eyes open (§6), and keep the
culture honest (§7).

## Gotchas

- **The layer brought in to manage complexity is how complexity gets in.** One company adopted OSGi to trap it; the
  demon got stronger, features became impossible and several developer-years went to undoing it (grug's own case; J2EE
  the same story).
- **The bigger the refactor, the likelier it fails.** Refactors that go far from shore, with the system broken for
  days, are the ones that end worse than they started.
- **Tests at the wrong level get thrown away or ignored.** Unit tests that break on every implementation change are
  deleted; end-to-end suites that "break all the time" are ignored, and then a real break hides among them.
- **"Works on grug's machine" is the moment tests get skipped.** After the prototype firms up, the discipline is to
  write them; nothing guarantees it works on another machine, or on this one next month.
- **Fewest lines is not easiest to debug.** A one-line compound conditional hides which clause fired; named
  intermediates show it.
- **"O(n²)? Not on my watch" without a profile.** The slow part is usually the network or the disk, not the loop; one
  network call costs millions of CPU cycles.

## 1. Build it at all?

- **"No" is the best weapon against complexity**: no to the feature, no to the abstraction. Good engineering advice,
  bad career advice; say it anyway, kindly, and it gets easier with practice.
- **When no is off the table, say "ok" and build the 80/20**: 80 percent of the value with 20 percent of the code, a
  little ugly, a bell or whistle short, and the demon kept out. The person asking usually wanted the 80.
- **Every revolutionary idea gets a grain of salt.** Most have been tried at least once; the back end is calmer than
  the front end because its bad ideas have mostly been tried already. New tricks are welcome; recycled ones in a new
  coat are where the demon's power comes from.

## 2. Shape before structure

- **Factor late.** At the start everything is water and nothing holds; let the system take shape, then good cut points
  emerge on their own: a narrow interface, a few functions, the complexity trapped inside like a demon in a crystal. A
  wrong early abstraction costs more than a late right one, so bias toward waiting.
- **A working demo tomorrow beats an architecture today.** Give the big brains a prototype to build (or a UML diagram
  to draw, which hurts no code); something that runs puts reality in the room faster than any committee. Call it a
  prototype when the project manager is listening.
- **Microservices take the hardest problem, factoring, and add a network call to it.** Factor in one process first;
  split only a cut point that has already proven narrow.
- **A front end split from a back end is two lairs for the demon.** A form into a database or a brochure site is simple
  HTML with little JavaScript; a big front-end framework is a choice with a cost, taken on purpose.

## 3. Tests where they pay

- **Test along the way, after the prototype firms up**, except for a bug: reproduce it with a regression test first,
  then fix it (the one place test-first works better; debug-practice).
- **Integration tests are the sweet spot**: high enough to test the system's correctness, low enough that a debugger
  shows what broke. Pour the effort there as cut points emerge, because their interfaces outlive implementations.
- **Unit tests mostly at the start**, to get going, held loosely: they break as the implementation changes and bugs are
  mostly interactions anyway.
- **A small end-to-end suite kept green religiously**: the most common flows and a few important edge cases, few
  enough to maintain so nobody learns to ignore a red run.
- **Mock rarely and coarsely**, at a cut point or a whole system.

## 4. Change what runs with care

- **Refactor late and small, close to shore**: the system works the whole time and each step finishes before the next
  begins; end-to-end tests are the lifeline (code-practice pins the behaviour first).
- **Chesterton's fence: understand the fence before removing it.** Ugly working code is often ugly because the world
  is; "grug no like look of this, grug fix" has cost many hours for no gain. Tests are often the hint why the fence is
  there. Improve the system, after taking the time to understand it.
- **Abstraction added during a refactor is the usual cause of its failure** (the Gotchas' OSGi and J2EE).

## 5. Write for the debugger

- **Named intermediates over one clever expression**: `contactIsInactive`, `contactIsFamilyOrFriends`, then the `if`;
  each result is visible in the debugger and the condition reads as words. More lines, easier debugging.
- **DRY in balance.** Repeated code that is simple and obvious can beat a closure chain or an object model built to
  remove it; the second copy of a simple thing may stay, and the first divergence or the third copy sends it to one
  home (code-practice).
- **Locality of behaviour over separation of concerns.** Put the code on the thing that does the thing, so looking at
  the button shows what the button does; style, markup and logic split into three files means three files to read for
  one button.
- **Salt, not sauce: closures, generics and type-level cleverness in small amounts.** Closures for operations over
  collections; generics for containers; a type system's main gift is the list that pops up after the dot, with
  correctness second.

## 6. Run it with eyes open

- **Log every major branch**, with a request id across machines, a log level that changes at run time and, where
  possible, per user; the last two are the club that fights production bugs. Good logging infrastructure pays back for
  years (systems-practice holds the formats).
- **Simple concurrency models**: stateless request handlers, job queues whose jobs are independent, optimistic
  concurrency for the web; thread locals only in framework code.
- **Profile before optimizing**, with a real-world profile that shows the specific slow thing; the cause is often a
  surprise, and the network far more often than the CPU.
- **APIs layered simple-first**: `sort()` and `write()` for the common case, a richer API beside it for the rare one,
  and the method on the thing (`list.filter()` returning a list, instead of stream, collect, Collector).
- **Tools pay back in weeks.** Two weeks learning the debugger, completion and the local tools often doubles speed;
  conditional breakpoints, expression evaluation and stack navigation teach more than a course. Parsers by hand,
  recursive descent, over generator tools whose output nobody can read.

## 7. Keep the culture honest

- **A senior who says "this is too complex for me" takes the demon's power away.** Fear of looking dumb is the demon's
  main food, especially for juniors; say it publicly, with a thinking face, and the room can say it too.
- **Everybody feels like an impostor**; the two states are "ruler of all I survey" and "no idea what I am doing", and
  the second is most days. Nobody is an impostor if everybody is.
- **Agile is fine and not magic**; prototypes, tools and good people decide more than the process, and a process whose
  failures are always "you did it wrong" is a sign.

## Reads

Grug's own list: Worse is Better (and its two replies), A Philosophy of Software Design (Ousterhout; distilled in
deep-modules, whose §2 says when grug's factor-late and his design-it-twice each hold), Crafting Interpreters (Nystrom;
the visitor pattern aside).

## Provenance

2026-11-05: "add to skills: ... grug brained developer: https://grugbrain.dev/", retrieved that day (about 4,700
words). Its "no" and "80/20" are the engineering face of a working habit already in this library: scarcity brings
clarity, and one targeted run beats a fan-out (work-practice).
