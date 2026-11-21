---
name: humanize-science-writing
description: Makes long-form science and technical writing read like a person wrote it, without losing rigour - blog posts, explainers, preprint-style pages, essays, newsletters and X articles - with a reviewer script for cohesion, rhythm, argument and AI-style signals. Use when drafting or revising one, or when asked to "humanize", "make it less AI", "make it readable", "make it compelling" or "check the argument or flow".
when_to_use: Before publishing long-form science text; after a big rewrite; when a reader says it is hard to follow or sounds machine-written. Single posts go to viral-tweet, voice to prose-voice.
---

# Humanize science writing

Everything below is a practice that good writers use most of the time and break on purpose some of the time. Orwell ended his six rules with the one that matters most: break any of them sooner than write something ugly. The reviewer script gives signals to look at; you make the call.

## Gotchas

- A score improves while the voice flattens: Integrity wins over every metric.
- Swapping a flagged AI word for a synonym leaves the problem: add the missing specific instead (§5).
- Stripping every em dash over-corrects: keep one where a turn needs it, and follow the author, some of whom leave them out entirely (§2).
- "I" in a science post from an author who writes "we" or "this post": choose grammatical person on purpose (§2).
- Colon counts hit target while 50-word run-ons remain: judge sentence shapes, not only the count (§2).

## Integrity first (the one thing that isn't a style choice)

- A rewrite keeps every fact, name, number and quote from the source or the author.
- Keep the author's voice, even when a metric would score a flatter version higher.
- Detectors are not verdicts; they misfire both ways.

## 1 · Measure first

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/review_prose.py <file.html|.md|.txt> [--main] [--captions] [--json]
```

`--main` skips collapsed `<details>` (supplements) so the numbers describe the main read. The report covers:

- **legibility and rhythm:** sentence length and spread, runs of same-length sentences, grade level, long words, nominalisations, passives, the punctuation mix, the longest sentences, and terms bolded as definitions but used earlier;
- **cohesion:** the share of sentences that pick up a word or connective from the one before, and the cold sentence and paragraph starts;
- **argument:** a concrete hook, question headings, the share of sentences carrying evidence, hedges, overclaims, stated limits, and a callback from opening to ending;
- **style signals:** AI vocabulary, negative parallelism, vague attribution, significance inflation, chatbot leftovers, and X, Y and Z lists (lists of names are skipped).

Reference points measured with this script (2026-10-20). They show a feel for range, not targets:

| Text | Words | Mean sentence | Spread | Grade | Linked | Evidence | Hedges /100 | Passives /100 | Lists /100 |
|---|---|---|---|---|---|---|---|---|---|
| Karpathy, *Unreasonable Effectiveness of RNNs* (2015, went viral, human) | 5,902 | 19.8 | 12.3 | 10.9 | 70% | 18% | 8.7 | 10 | 1.7 |
| an essay essay | 2,547 | 15.9 | 9.5 | 9.3 | 46% | 25% | 4.4 | 6 | 1.9 |
| an essay main read, before rewrite | 1,255 | 16.5 | 9.9 | 8.6 | 63% | 46% | 1.3 | 20 | 9.2 |
| Same post after a first rewrite (author: "feels a bit boring/stale") | 1,504 | 14.3 | 7.1 | 7.1 | 56% | 41% | 1.9 | 7 | 7.6 |

**Let the numbers guide, and the reader decide.** The first rewrite of an essay cut passives and grade level, and the author found it flat. Its sentence-length spread fell from 9.9 to 7.1. Clarity and flair pull against each other only when every sentence is trimmed to the same size. Keep long, rolling sentences beside the short beats, and keep a few vivid specifics and asides in each section. When the grade level and the spread both drop, read it aloud for flatness.

Human prose trips the signals too: Karpathy has a "not only ... but" and a "without further ado". Machine-made prose shows up as a cluster: many signals in one paragraph, a flat rhythm, one punctuation mark doing all the work, and claims with no specifics.

## 2 · What good human writers do

### Before the first sentence

- **Know what you think.** If you can't say the argument in one sentence, the draft can't either. Write that sentence down, then a reverse outline (one line per paragraph, saying what it adds).
- **Write for one reader.** Pinker's *curse of knowledge*: the better you know a subject, the harder it is to picture not knowing it. Choose one smart reader from outside your field and test the draft on a real one if you can.
- **Show the reader something.** Pinker's *classic style*: a conversation between equals, where the writer points at something in the world and helps the reader see it. Show first, then name it, then formalise it.

### Sentences

- **Characters as subjects, actions as verbs** (Joseph Williams). Ask who does what, then make the "who" the subject and the "does" the verb. "The census places 175 models" beats "175 models are placed by the census".
- **Wake the zombie nouns** (Helen Sword). "The regulation of" becomes "regulates". Keep a nominalisation when it names a real idea (adaptation, multistability).
- **Old information first, news last** (Gopen and Swan). Start each sentence with something the reader already holds, and end on what's new: the stress position is where readers look for the point.
- **Get to the verb fast.** Keep long openers and subject-verb interruptions for when they earn it.
- **Choose the short word when it does the job** (Orwell), and the plain word over jargon unless the jargon is the subject.
- **Cut clutter, keep warmth** (Zinsser). Remove what does no work and keep the person: a voice, specifics, and the
  asides that sound like the author.
- **Choose grammatical person on purpose.** In science writing, the work as subject ("the census finds", "this post
  tests") or "we" reads as scientific and still active; "I" suits personal essays. Follow the author's preference
  (a person's style skill may narrow this, for example no "I" in science posts).

### Rhythm and punctuation

- **Vary the structure, not only the length.** Prose reads alike when one shape repeats, most often "X: a, b and c".
  Mix the shapes instead: a question and its answer, a short beat after a long line of reasoning, a conditional, a
  turn on "but" or "so", and an ending that puts the news last. Count colons per 100 sentences as a quick signal.
  The essay's rewrite took them from 27 to 15 and semicolons from 8 to 2. Its length spread fell at the same
  time, because the 50-word run-ons were the old spread: judge the shapes as well as the number. Case:
  2026-10-25: "more varied sentence structure, re-write for human reasoning and flow of emphasis".
- **Vary sentence length.** A short sentence after two long ones lands like a beat. Runs of same-length sentences are the clearest mechanical tell there is.
- **Use the whole kit.** Each mark has its own weight. An em dash is a turn or an aside said out loud. Parentheses whisper. A colon makes a promise the next words keep, and a semicolon joins two halves of one thought. Human writing mixes them; machine writing tends to lean on one, often paired em dashes around an aside or before a reveal. Em dashes are welcome where a turn needs one.
- **Read it aloud** (Paul Graham). If you wouldn't say it to a friend, rewrite it until you would. If you run out of breath, split the sentence.

### Paragraphs and argument

- **One job per paragraph.** The reverse outline exposes paragraphs that do nothing or do two things.
- **Put evidence beside every claim:** a number, a figure or a citation, within a sentence or two. Say how sure you are once, at the claim, not in every sentence.
- **Name the limits plainly,** and say what result would change your mind.
- **Say what an empty region says about the hypothesis.** When a table or map has blank rows, state plainly what the
  blanks mean if taken at face value, what would fill them, and what would retire the axis. Example: "Loops and brakes
  are real axes; running totals are, so far, an axis with almost no one on it. If the band stays empty after better
  readings and newer releases, retire the axis and each row shrinks from (loops + 1)² to loops + 1." Mendeleev's table
  carried predictions that never came true as well; a table that can lose an axis is one that can be tested.
  Then say what each blank would do if it existed ([references/cases.md](references/cases.md): chemistry's missing elements).
- **Tell the honest failure** as a story beat, with a before and an after. It builds more trust than any claim.
- **Explain the proofs you lean on.** When a result rests on a theorem, give three things in plain words: what it
  says, the idea behind it in one sentence, and what it does not say (worked example in [references/cases.md](references/cases.md)). Methods read the same way:
  a plain lead sentence before each dense paragraph, and the intuition beside each formal condition.

### Voice

- Keep the writer's quirks. If there is a sample of their writing (a blog, posts, memory notes), match its rhythm, grammatical person and humour.
- Earn opinions with specifics, and then state them without hedging.
- Replace the generic with the particular: a name, a date, a number, an object the reader can picture.
- Let real people carry the argument: a scientist, chemist, physicist or philosopher whose verified act or short line does a step's work, one per chapter at most (an essay, 2026-10-26, on "text does not feel very human ... warm, cleverness": Maxwell's governors for the brake, Feynman's blackboard before building the missing element, Levi naming chapters after elements, Heraclitus's circle to close; each checked that session).

## 3 · Moves that help science writing travel

- **For warmth, wit and a person on the page**, follow prose-voice once the argument is clear.

- **The arc, the opening and the close follow the storytelling skill**: open on one concrete event or the reader's
  own question, carry that question through, close with a callback and one next step. What follows is how science
  writing in particular travels.
- **Put the payoff near the top:** a short summary or scorecard, then the story. Anthropic's *On the Biology of a Large Language Model* gives contents, an early note on scope, and headings that state findings.
- **Let the reader push the system before you name the property.** Use a toy example (Karpathy's "hello"), a slider or a clickable figure. Ciechanowski's explainers are figure-first throughout.
- **Use one everyday analogy per hard idea, then show the real thing.** After the toy and the analogy, name a real
  system the field knows and draw it in the field's own visual language (for cell biology: nucleus, gene, mRNA,
  proteins, membrane, receptor). Example: the ring toy teaches "odd brakes make a clock"; the circadian clock
  (CLOCK:BMAL1 switching Per and Cry on, PER and CRY switching them off) shows it in a cell, with a reference.
- **Give each worked example its own chapter, told as a story.** Open on the organism's problem in plain words (a
  bacterium deciding whether to build the machinery for lactose; a cell that must be ready for dawn before dawn), show
  the mechanism, hand the reader the control, then read it three ways in one line each: shape, pattern, function.
  One everyday metaphor per chapter (a thermostat with a long hallway) and at most one dry joke, placed where the
  point lands ("a bacterium cannot afford to be a flip-flopper"). A frame chapter before the examples names the three
  readings so each example can be short. Case: an essay's examples sat as three traces in one figure and read as
  "dry, stale, boring"; as three chapters with live figures the same facts carry the argument (2026-10-25:
  "storytelling, key points should arise naturally and land solidly. a bit of humor even. playful, but still
  professional and technical").
- **Say what it is for, three ways: the field, people, technology.** Borrow the analogue's track record where one
  exists. Example: Mendeleev's eka-silicon became germanium and the first transistor; element 43 was made before it
  was found and became medical imaging's technetium; so a loop table could give biology a shared address for every
  circuit, a diagnosis by element, and design by position.
- **Give each thing one name and keep it.**
- **Show your work:** open code, one command to reproduce, and the data a click away.
- **Set the work in its foundations,** and name and cite what it builds on.
- **To cut by a third, cut structure before sentences.** Merge chapters that tell one story (disease and early
  diagnosis), move a point to where its evidence already sits (aging beside the reset it depends on), let a contents
  block grouped into parts replace any preview of the argument, and drop paragraphs that restate a figure or a
  scorecard. Then tighten what is left, and keep every fact by leaving detail in folds. Case: an essay went from
  sixteen chapters to fourteen in five parts and its main read from 7,153 words to 3,875 with no citation lost
  (2026-10-25: "want better organization and flow, reduce length word count by at least 30%"). The structural cut is
  often a whole section that another page already owns: a README lost its design theory and twelve footnotes once its
  explainer page was found to carry both, which was 42% of its words for no loss (2026-11-21). Tightening sentences
  instead tempts you to stitch clauses with colons and dashes, which reads shorter and lands harder: one interim draft
  cut 16% of its words while its grade went 8.4 to 9.3 and its colons 54 to 72 per 100 sentences. Breaking those back
  into short sentences is what moved the grade to 7.1.
- **Balance breadth and depth.** Aim for a 5 to 12 minute main read with about 5 or 6 figures. Put methods, extra figures and caveats one click away. Budget all three layers and measure each: main read, with folds open, with supplements (an essay, 2026-11-19: "15 min without drop downs, up to 30 min with drop downs and up to 1 hr with all supplemental data and methods").
- **Use the field's own words.** Practitioners' vocabulary over names you coined while building (a DJ says playlist and transition, not crate and seam); keep coined terms in code, or define one once in plain words. The field-vocabulary skill has a checker.
- **Say each fact once,** where it does the most work. A title, a lede and a caption that repeat each other cost the reader three reads for one fact.
- **Story first, methods in an appendix.** For a system or pipeline page: a short plain story in steps (what goes in, what happens, how a person judges, what comes out), one figure per step, no formulas; every full method in folded sections below, each with a one-line plain summary.

## 3b · Secondary moves

Moves borrowed from other writing skills and explainers, worth trying once the above is done: [references/secondary-moves.md](references/secondary-moves.md).

## 3c · Scaffolding for a general reader

A post can pass every reviewer check and still read as shiny surface to someone outside the field, because the first
screen asks for every term at once. The fix is structural:

- **One idea per step, each by example or play before its name.** Let the reader flip the arrows of a ring and see it
  tick, then say "odd brakes make a clock"; let them slide a hill and watch one controller recover exactly, then say
  "running total". Name the thing after they have met it.
- **Keep a vocabulary budget for the main read.** List every term the main read introduces; halve it. Aliases and
  formal names (integrator, H1, k and j, SBML, enumeration) go to the figures, captions or supplements.
- **Withhold the reveal until the reader can see it.** Build the table in front of them (2 × 2, 3 × 3, 4 × 4), then
  say "look at the figure before reading on and notice where the blanks are". A summary at the top can promise the
  shape of the result without spelling it out.
- **Follow the field's order.** In biology, structure before function, and a familiar example (the chemistry table)
  before the biology. The data before the finding: what the data are, their structure, the hypothesis, the test and
  the unexpected result, told as the scientific method, with the pipeline drawn as a flow diagram and the method as a
  hypothesis > test > result loop (essay, 2026-11-19: "remember in biology structure > function"; "remember devil
  is in data details! introduce data, describe structure, hypothesis, test, and any unexpected result(s)"; "add a data
  processing figure, pipeline as flow diagram").
- **Surprise and correction as beats**: one circuit that lands in four places; one bug found and fixed.
- **Write the post as clearly as you would say it to a friend.** If a plain spoken summary lands and the page does
  not, rewrite the page from the summary: one everyday picture per idea (a thermostat for negative feedback, cruise
  control for integral feedback, a nudge going once round the loop for loop gain), the field's name after it, one name
  per thing, formulas and side cases in folds. Case: an essay, 2026-10-25; a findings list in its own
  jargon drew "i dont know what any of that really means?", the plain version "this clarity is awesome! the html blog
  post should be just as clear"; the rewrite took the grade level from 7.6 to 6.7 at the same read time.
- **Introduce An Acronym (AA), then use AA.** The convention in biology writing: the first time a short form appears
  in prose, write the phrase out and put the short form in brackets after it, then use the short form from then on.
  It costs four words once and saves a reader the lookup every time after. Three qualifications. A gene, protein or
  receptor symbol (VEGFR2, AMPK, NRF2, trkB) is a name, not an abbreviation, and is not expanded in the literature
  either; leave it. A figure label or a table cell has no room, so the rule binds where a reader reads sentences, and
  the short forms a reader only ever meets on a drawing go in the glossary instead, so there is one place to look.
  And pick one spelling and keep it (DPP-4 or DPP-IV, not both) except inside a quotation, which keeps the source's.
  Use only short forms the field already uses: an acronym that is not standard costs the reader a lookup that
  fails, and may collide (PoP would sit on "proof of principle"). `scripts/review_prose.py` lists a page's short
  forms and whether each was expanded at its first use in prose. Case: a peptide explainer, 2026-11-19, where GPCR, RCT,
  DPP-4, GMP, API and CDMO were all first met inside a figure and never expanded anywhere.
- **One governing metaphor carries the arc** (here: a map with blank regions, surveyed), with one small analogy per
  hard idea inside it.

Case: an essay. Let's count them.* The manuscript-shaped version (abstract, H1 to H3, scorecard first)
drew "very shiny-surface level and confusing to general human audience"; the retold version builds the three counts
by play, moves the scorecard after the findings, and cuts the term count in half at the same length.

## 4 · Reading passes

0. **Scale:** a "thorough check" asks for a revision. Before editing, set targets that can fail: which paragraphs get rewritten, a word budget for the main read, the structural change (beats, order, a figure). Draft in one pass, then measure the word count and the size of the word diff, and cut again (work-practice §1, per-item measures). (an essay, 2026-10-26: a long think, then about 20 sentence tweaks, and the main read grew 190 words under "concise"; then "changes very minimal for amount of time spent thinking". The rewrite touched every paragraph: 5,060 to 4,569 words.)
1. **Argument:** the one-sentence argument, the reverse outline, and the question each paragraph serves.
2. **Cohesion:** go through every cold start the reviewer lists. Keep the deliberate turns; bridge the rest with a word the reader already has.
3. **Legibility:** split the longest sentences, wake zombie nouns, define each term at first use (picture, then name, then formal term), and break flat runs.
4. **Evidence:** check that every claim has its support nearby, that hedges sit where real doubt is, and that overclaims are cut back.
5. **Voice:** read it aloud, match the author's sample, and replace generic phrasing with specifics.
6. **Re-run the reviewer and compare.** Numbers should move toward the reference range, but a number that stays put for a good reason is fine.

## 5 · Style signals worth a second look

These come from Wikipedia's *Signs of AI writing* (WikiProject AI Cleanup) and common chatbot leftovers:

- inflated significance ("stands as a testament", "plays a pivotal role");
- the AI vocabulary cluster (delve, tapestry, intricate, showcase, foster, landscape);
- negative parallelism ("not just X, but Y");
- reflexive lists of three;
- count-pair headlines ("One cell, nine addresses", "Two peptides, one receptor family"): say the finding in plain
  words instead (a peptide explainer, 2026-11-05: "avoid n of this, n of that phrases");
- vague attribution ("experts say");
- "-ing" tails ("highlighting its importance");
- bolded inline headers and emoji as formatting;
- leftovers ("I hope this helps", "in conclusion");
- the "that is X" verdict sentence ("That is the point.", "That is what the drain does."), and its twin "This is X":
  once in a piece at most. "that's" reads human, or cut the verdict and let the sentence before it land
  (2026-11-19: "a big AI prose tell ... maybe once in a piece. that's x is more human and natural");
- its relatives, each fine once and a tell in a cluster: the colon or question reveal ("The result? X.", "The answer:
  X."), "Here's the thing", "It's worth noting", "In other words", "the real X is Y", stacked one-word fragments
  ("Fast. Cheap. Clear."), and soft intensifiers (quietly, deeply, truly, genuinely).

When one of these turns up, fix what is underneath, which is usually a missing specific. Swapping in a synonym doesn't help.

## Provenance

Built 2026-10-20 while revising an essay (an essay repo). The author asked how to humanize scientific blog writing, wanted strategies rather than hard rules, and asked for cohesion, legibility and argument checks. Later that day the author said "some em dashes ok, remember no hard rules ... synthesize best human writing practices". That message led to section 2, a punctuation mix in place of an em-dash count, and the rhythm check.

Sources:

- Gopen and Swan, "The Science of Scientific Writing" (*American Scientist*, 1990);
- Orwell, "Politics and the English Language" (1946), six rules;
- Pinker, *The Sense of Style* (2014): classic style and the curse of knowledge;
- Williams, *Style: Lessons in Clarity and Grace*: characters and actions;
- Sword, "Zombie Nouns" (*New York Times*, 2012);
- Zinsser, *On Writing Well*: clutter, humanity and warmth;
- Paul Graham, "Write Simply" (2021);
- Wikipedia, *Signs of AI writing*, and skills built on it (blader/humanizer, stop-slop);
- the worked examples named in section 3;
- other writing skills seen in marketplace listings (davila7/claude-code-templates scientific-writing, K-Dense-AI claude-scientific-skills), read as listings and not installed.

The reviewer was validated on three different texts (the table above), including human-written prose it had never seen. The list-of-three check was refined after it counted author lists ("Baudier, Fages and Soliman") as reflexive triads.
