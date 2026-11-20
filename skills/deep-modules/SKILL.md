---
name: deep-modules
description: Designs software by Ousterhout's A Philosophy of Software Design - complexity as dependencies plus obscurity, deep modules over shallow, information hiding over leakage, general-purpose interfaces, errors defined out of existence, design it twice, strategic over tactical. Use when designing or reviewing a module, class or API, or on "deep module", "shallow", "information leakage", "design it twice" or "Ousterhout".
when_to_use: Before settling an interface, splitting or merging classes, or adding an exception. Build-it-at-all and factor-late go to grug-brain (§2 reconciles), clean code to code-practice.
---

# Deep modules

"Complexity is anything related to the structure of a software system that makes it hard to understand and modify the
system." John Ousterhout's A Philosophy of Software Design (2018; second edition 2021) is a short book about that one
enemy: where it comes from, how to recognize it, and the handful of moves that keep it out of an interface and inside
an implementation. Ousterhout recommends grug-brain's essay and grug lists his book; the two agree on the enemy and
differ on timing (§2). In the order the work runs: read the complexity (§1), take the strategic stance (§2), make the
module deep (§3), hide the information (§4), make the interface somewhat general (§5), pull complexity down (§6),
define the errors away (§7), design it twice (§8), write the comments first (§9), and review by the red flags (§10).

## Gotchas

- **Tcl's `unset` threw an error on a missing variable.** Callers wrapped every call in `catch`; Ousterhout calls it
  "one of the biggest mistakes I made in the design of Tcl". Fix: define the operation as "ensure the variable no longer
  exists", and the error is gone (§7).
- **Java's `substring` throws when an index is out of range**, so a one-line call grows to 5 to 10 lines of clamping.
  Python's slices return the overlap and nothing else. Fix: return the characters in range, which also makes the
  method deeper.
- **Three objects to read one file in Java** (FileInputStream, BufferedInputStream, ObjectInputStream), and a forgotten
  BufferedInputStream means slow I/O with no warning. Fix: buffering on by default and a separate constructor to turn
  it off, so the common case needs one object (§3).
- **A reader class and a parser class for HTTP requests.** Both had to parse headers to find Content-Length, so the
  format leaked into both and callers had two methods to call in order. Fix: one class that reads and parses (§4).
- **`getParams()` returned the internal Map.** Every caller depended on the representation and could mutate it. Fix:
  `getParameter(name)` and `getIntParameter(name)`, which hide the map and do the conversion (§4).
- **A network module that masked every exception.** Applications could not learn that a message was lost or a peer
  died. Fix: hide what nobody outside needs and expose what callers must act on (§7, taking it too far).
- **"Any method longer than N lines must be split."** The rule yields shallow methods whose interfaces cost more than
  they hide; in the Martin debate Ousterhout judges a split by whether the piece has a simpler interface than its
  implementation, not by line count (§3).
- **A configuration parameter for the retry interval.** Nobody downstream knows the right value. Fix: measure the
  response time of requests that succeed and retry at a multiple of it, which also tracks changing conditions (§6).

## 1. Read the complexity

- **Complexity is what the reader meets**, weighted by how often: the system's complexity is each part's complexity
  times the fraction of time developers spend there, so complexity isolated where nobody goes is nearly eliminated.
  "If other people think a piece of code is complex, it is."
- **Three symptoms.** Change amplification: one small change needs edits in many places (a banner colour set on every
  page). Cognitive load: how much a developer must know to make a change (a C function that returns memory the caller
  must free); fewer lines are not always simpler. Unknown unknowns: it is not obvious which code to change or what to
  know (the darker emphasis colour on a few pages that must track the banner colour); the worst, because nothing tells
  you it is there.
- **Two causes.** Dependencies: code that cannot be understood or changed alone (a method's signature binds every
  caller). Obscurity: important information that is not obvious (a variable named `time` with no unit; a status
  table nobody told you about). Dependencies give amplification and load; obscurity gives unknown unknowns.
- **Complexity is incremental**: thousands of small dependencies and obscurities, none decisive alone, so the stance is
  zero tolerance ("you have to sweat the small stuff"), and a system whose design needs a lot of documentation is
  showing a red flag about the design.

## 2. Strategic over tactical

- **Working code is not enough.** Tactical programming finishes the task and leaves a kludge each time; the "tactical
  tornado" ships fastest and others clean up. Strategic programming's goal is a great design that also works, paid for
  with continual small investments, about 10 to 20% of development time, which pays back within months.
- **Design emerges in small investments.** Waterfall fails because nobody can visualize the system in advance; the
  ideal design arrives in bits as experience does. The increments of development are abstractions, not features: put off
  an abstraction until a feature needs it, then design it whole and cleanly.
- **Where grug and Ousterhout agree and differ.** Both say no to the premature abstraction and to the architecture
  before the demo; grug's "factor late" governs until a cut point has shown itself. From the moment a feature needs
  the abstraction, Ousterhout governs: design it twice (§8), make it somewhat general (§5), and resist the hack that
  "works". A prototype may be tactical; the system is not.
- **Tests first only for bugs.** Ousterhout writes unit tests and distrusts test-driven development as "tactical
  programming pure and simple"; the one place tests come first is a bug, where the failing test proves the fix
  (debug-practice, grug-brain §3 say the same).

## 3. Make the module deep

- **A module is an interface and an implementation**; the interface is everything a user must know, formal (signatures,
  types, exceptions) and informal (behaviour, side effects, the order calls must come in), and the informal part is
  usually larger and can only be written as a comment (§9).
- **Depth is functionality per unit of interface.** Draw the module as a rectangle: area is functionality, the top edge
  is the interface. Unix file I/O is five calls (`open`, `read`, `write`, `lseek`, `close`) over hundreds of thousands
  of lines that have changed radically while the calls have not; a garbage collector has no interface at all and
  shrinks the system's. A linked-list class is shallow: its interface is as complex as its code. "Interfaces are good,
  but more, or larger, interfaces are not necessarily better."
- **An abstraction omits only unimportant details.** Including unimportant ones adds load; omitting important ones (when
  a file system flushes to disk, for a database) makes a false abstraction, simple-looking and wrong.
- **Classitis**: "classes are good, so more classes are better" produces many shallow classes whose interfaces add up to
  system complexity. Size is not the measure; depth is. Classes of 200 to 2,000 lines are fine when deep.
- **The common case simple.** Sequential I/O is the default and `lseek` exists for the rest; buffering comes without
  asking. "The best features are the ones you get without even knowing they exist." Defaults do the right thing, and
  the rare feature is reachable without being learned by everyone (the overexposure red flag).

## 4. Hide the information

- **Each module encapsulates a few design decisions** (Parnas, 1972): how a B-tree stores keys, how TCP retries, that
  most files are small. Hidden knowledge simplifies the interface and lets the decision change in one place.
- **Leakage is a decision reflected in two modules.** Through the interface, or by the back door: two classes that both
  know a file format leak it without either exposing it, and the back door is worse because it is not obvious. On
  finding leakage, ask "how can I reorganize these classes so that this knowledge affects only one?"
- **Temporal decomposition is the usual cause**: a class for reading, one for transforming, one for writing, when
  reading and writing share the format. Structure by the knowledge a task needs, not by the order tasks run.
- **`private` is not information hiding** when getters and setters hand the variable back out; getters and setters are
  shallow methods that expose the implementation. Making a class a little larger often hides more.
- **Three questions for a class**: what unique value does it provide; what key knowledge does it use to provide it; what
  is the least of that knowledge the interface must expose.

## 5. Somewhat general-purpose

- **Functionality for today's needs, an interface that is not tied to them.** The student text editors with
  `backspace(cursor)`, `delete(cursor)` and `deleteSelection(selection)` leaked the user interface into the text class;
  `insert(position, text)` and `delete(start, end)` with `changePosition(position, n)` are fewer methods, deeper, and
  the UI code that uses them is more obvious (a developer can see which character backspace removes).
- **Three questions for an interface**: what is the simplest interface that covers all current needs; in how many
  situations will this method be used (one is a red flag); is it easy to use for today's need (single-character
  operations are simple and general and would loop everywhere, so ranges belong in the text class).
- **Different layer, different abstraction.** A pass-through method, one that forwards its arguments to a method with
  the same signature, adds interface and no function (13 of 15 public methods in one student class); it means the
  responsibilities of two classes overlap, so redistribute or merge. Dispatchers and multiple implementations of one
  interface share signatures legitimately, because each adds function.
- **Together or apart.** Bring code together when it shares information, when the joint interface is simpler, or when
  it removes duplication; separate general-purpose mechanism from special-purpose use, the special pulled up into the
  higher layer. Subdivision has its own cost: more interfaces, more glue, parts farther apart.

## 6. Pull complexity downward

- **"It is more important for a module to have a simple interface than a simple implementation."** Most modules have
  more users than developers, so the developer suffers on their behalf; the martyr principle of the lectures: take on
  the hard problem, solve it completely, make it easy for others.
- **An exception thrown or a configuration parameter exported is complexity pushed up** to every caller or every
  administrator. Before exporting a parameter ask "will users be able to determine a better value than we can here?";
  when the answer is no, compute it (the retry interval from measured response times).
- **Three conditions**, or it becomes leakage: the complexity relates to the class's own function, pulling it down
  simplifies much elsewhere, and the class's interface gets simpler. The backspace method pulled UI knowledge down into
  the text class and failed all three.

## 7. Define errors out of existence

- **Exception code is the hardest code**: it runs rarely, is hard to test, and recovery creates new exceptions; a 2014
  study found more than 90% of catastrophic failures in distributed data systems came from incorrect error handling.
  "Code that hasn't been executed doesn't work." The exceptions a class throws are part of its interface.
- **Define the error away**: Tcl `unset` as "ensure gone"; Unix deleting an open file by unlinking the name and freeing
  the data at the last close, where Windows refuses and users hunt the process; `substring` returning the overlap.
- **Mask it low**: TCP resends lost packets so no client knows; NFS hangs and retries rather than failing every
  application, which could do nothing useful with the error.
- **Aggregate it high**: one handler at the dispatcher turns every missing-parameter exception into an error response,
  with the message built where the knowledge is; RAMCloud promotes a corrupt object to a server crash so one recovery
  path exists and gets exercised.
- **Or just crash** on what cannot be handled (out of memory via `ckalloc`, an inconsistent data structure), with a
  clear message.
- **Special cases too**: an always-present selection that is sometimes empty removes every "no selection" check. The
  limit is information the caller needs; what is needed outside is exposed, even at a cost to the interface.

## 8. Design it twice

- **Sketch two or three radically different interfaces before choosing**: for the text class, line-oriented,
  character-oriented, range-oriented. List the pros and cons: ease of use for the higher-level code first, then
  simplicity, generality, efficiency. The comparison often yields a fourth design better than any (the range API came
  from noticing both others pushed text manipulation upward).
- **Then again for the implementation** (a list of lines, fixed blocks, a gap buffer), with simplicity and performance
  as the criteria. An hour or two for a class, against days of implementing it.
- **"Smart people get it right the first time" is the habit to unlearn**; the problems are hard, and the second design
  teaches what makes designs good (hci-principles holds the QOC form for recording the options and criteria).

## 9. Comments are the design tool

- **Without comments there is no abstraction**: the informal interface, what a method does and what its result means,
  cannot be written in code, and a reader who must read the body to use the method has no abstraction at all. The four
  excuses (self-documenting code, no time, comments go stale, all comments are worthless) each answer to this.
- **Comments say what is not obvious from the code**, at a different level than the code: lower for precision (units,
  whether `end` is inclusive, whether null is allowed, who frees the memory, invariants), higher for intuition (the
  abstraction, the rationale, how a parameter was chosen). A comment that repeats the code, or the name, is the common
  failure; interface documentation stays free of implementation detail.
- **Write the class comment and method headers first**, bodies empty, and tune until the structure feels right. The
  comment is "a canary in the coal mine of complexity": a method that needs a long comment to be described completely
  is a shallow or badly cut method, and the best design is the one described completely in the fewest words.
- **Where the Clean Code school differs**: Ousterhout writes 5 to 10 times more comment lines than Robert Martin and
  prefers a short name plus a comment to a very long name; both agree implementation comments belong only where the
  code is non-obvious (their 2024-25 written debate).

## 10. Review by the red flags

Shallow module; information leakage; temporal decomposition; overexposure (a common feature forces users to learn a
rare one); pass-through method; repetition; special-general mixture; conjoined methods (neither understood without the
other); comment repeats code; implementation documentation contaminates interface; vague name; hard to pick a name;
hard to describe (the comment cannot be short and complete); non-obvious code. Each names a place to look, and the fix
is one of §3 to §9.

## Provenance

Sources retrieved 2026-11-05: Ousterhout's Stanford page for the book (second edition, July 2021: a chapter "Decide
What Matters", chapter 6 expanded, comparisons with Clean Code; it recommends The Grug Brained Developer), his CS 190
lecture notes (Winter 2018: complexity, modular design, comments, exceptions, testing, wrap-up), his written discussion
with Robert Martin (September 2024 to February 2025, github.com/johnousterhout/aposd-vs-clean-code), the first edition's
chapters 2 to 13, 15, 19 and 21 with its summaries of principles and red flags, Will Larson's notes (lethain.com, 2018)
and Jimmy Koppel's review (pathsensitive.com, 2018: the POSIX `open` flags as a case where a short signature hides a
complex interface). 2026-11-05, the person chose "Tufte + Ousterhout" from a list of taste bibles.
