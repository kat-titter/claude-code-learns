---
name: pitch-deck-story
description: Shapes a short pitch or talk (about five minutes, investors and scientists in the room) slide by slide - story beats, which slides it needs, what each says and shows, word budgets, the appendix, a timed script and judge Q&A. Use when drafting or revising a pitch deck or contest talk, or when a reviewer says it is "too dense", "too much text", "not clear or compelling", "the value isn't clear" or asks "why now, why me?".
when_to_use: Before writing slides; after evidence is added; before a rehearsal; when a deck runs long. Building and publishing the HTML deck goes to html-slide-deck.
---

# Pitch deck story

A pitch is a few ideas the room remembers, each slide making the next one wanted. These guidelines come from one five-minute
pitch (an AI × Bio contest, Oct 2026) and the primary sources listed in `references/slide-patterns.md`, which also
gives every slide type its layout, figure, usual miss and a worked example. Building the deck lives in html-slide-deck,
the page and its colour in design-practice, axes and keys in figure-design, the arc in storytelling.

## Gotchas

- Too many words for five minutes: move them to the script ("less text per slide. can always add this to script!").
- The value isn't clear ("value add should be clear"): say who pays for what, in one line, on the product slide.
- A competition slide that flatters the pitch: show the field's everyday tools fairly (a judge flagged it).
- A chart that disagrees with the image beside it (A12): check that each figure shows the claim its caption makes.
- A deck that dwells on the problem's pain: keep the tone positive and excited, and lead with what becomes possible.

## Key story beats

Choose the five to seven points the room must leave with; after a full session most people recall one or two (YC,
Kevin Hale). Each beat is one slide, or a set of at most three (YC's seed template), said once.

1. **What it is**, one declarative sentence a listener can repeat (Sequoia's "company purpose"; Michael Seibel: make it
   sound dumber than you think it should). a pitch deck: "A shared map of every lab's control cells."
2. **Why now**: the change in the world that makes it possible and urgent, with winners and losers (Andy Raskin's
   strategic narrative; Sequoia). Successful decks put purpose, why now and why you early and say them briefly; failed
   ones opened on the product and drew four times the reading time there (DocSend data, TechCrunch 2019).
   On the slide, why now is three beats in time order that end on now, each a verb with its number and the
   last one bold ("2023 1.8B cells go public", "2026 $1.8B push: Google, Meta join", "now AI reads cells"): the
   world got bigger, more players came, and the tool exists now (a pitch deck, 02d, 2026-11-09: "why now needs to
   be punchier. datasets are getting bigger, more distributed, NOW"). Where one evidence slide already shows both
   causes, why now can sit on it instead, as two forces meeting: its two halves titled "more public cell data"
   and "AI thirsty for large data pools" (a pitch deck, 03b, kept 2026-11-17).
3. **The problem, felt**: one person, how it is done today, what each way costs in money or months.
4. **The insight**: what you see about the problem that the field has missed, specific and plain (Seibel), shown as a
   test the room can play before it is named.
5. **The product**: the noun first, then the future it makes possible, then the few things it does to get there
   (Raskin's promised land and gifts). A short list of steps beats a screenshot (Hale).
6. **Proof**: traction if you have it, else the strongest evidence on real data, a pilot or a letter, with the honest
   paid count, even zero (YC: "Make the numbers clear and meaningful").
7. **Market, bottom-up**: who buys, how many, at what price, and the share you aim for (Seibel).
8. **Business model, competition, go-to-market**: one simple model as a price list; the tools the field uses today,
   fairly, with the gap only you fill; who buys first and how you reach them.
9. **Why us**: the founders' fit to this problem, with proof; the hire you need, named.
10. **The ask**: the amount, what it buys line by line, the milestone it reaches in 12 to 18 months. A nonprofit
    says so on the title slide, spelled out once, and its money words follow: "raising $1.8M to start a nonprofit
    FRO", the hire by its title ("an executive director"), a share target as what makes it self-sustaining;
    "pre-seed", "seed" and "round" go (a pitch deck, 2026-11-17: "Nonprofit FRO").
11. **The close**: the five-year picture (Sequoia's "vision") calling back to the opening, the ask still on screen.

The order can flex: a contest talk may open on the founder and the question (a pitch deck) as long as what it is and why
now land in the first minute. Go-to-market and milestones are the beats decks most often skip; projections, risks, IP
and the methods behind each number go to the appendix boards.

## Check the beats before the slides

- **Read the headlines alone, in order**: they tell the pitch beat by beat, each picking up the last slide's idea and
  handing the next its question (a pitch deck, 2026-10-26: "slide <> slide concepts should connect and flow clearly"). A
  word that recurs (the title's "One normal" returning as "one shared change") ties the arc.
- **Map every beat to a slide** with the table in `references/slide-patterns.md`: a beat with no slide is the slide to
  add, a beat on three slides has two to cut.
- **The email test** (Seibel): send the two-sentence "what we do" to a smart friend; any question back means rewrite.
- **The glance test**: show a stranger a slide for three seconds (Duarte); it is obvious when they say its idea back
  (Hale: legible, simple, obvious).

## Story order

The arc, opening and close follow storytelling; these are the moves that work on slides.

- **Open with the person, land the question.** A quiet title, the founder in two plain sentences, then the question
  everyone in the field asks ("Do my cells look 'normal'?") as that slide's punchline.
- **Show how it's done today, specifically, with what each way costs**: the query as typed, the email to a paper's
  authors, the money or months each burns (a pitch deck, 02c, 2026-10-25: "show more specifically web search for U2OS").
- **Say the value in one sentence in the first minute, and sell on the slide where it works.** Prove the problem once
  or twice, not four times; the slide where the product visibly works says so in its headline ("Controls alone flagged
  the batches whose drug results shifted"; 2026-10-25: "more direct, clear, compelling, value add should be clear").
- **Lead with the positive frame**: what becomes possible; failure modes live in the appendix, one board each.
- **A lived example in the middle**: the founder's own control experiment, then the field-wide version.
- **Name what each audience gets, with a proof beside it**: one tile per user, the gain in six words or fewer and one
  number the talk already showed ("Scientists: catch a drifting batch before the screen. 3 batches flagged from
  controls alone"; 2026-10-26: "value for scientists, AI researchers, whole field is just still not clear").
- **The whole before its parts; a marked difference says what it does.** Show the mechanism assembled (the lock with
  its key in it) before the parts compared (three keys), and when a figure marks what one item lacks, the slide gives the
  consequence with its number: fentanyl has no OH, grips as tight, is 580× more fat-soluble, so reaches the brain in
  minutes (a drug-mechanism deck, 2026-10-27: "show lock and key, then keys? ... explain this if so").
- **Similar slides sit together, and a figure is drawn once**: the second becomes a click view of the first with only
  the new thing added (the certificate became the lab map's second view; "similar slides should be next to each other").

## Each slide

- **The title states the finding, with its number**, or asks the question the slide answers: "Automated seeding
  keeps well-to-well CV under 10% (mean 7%)", "What is DPC, and why use it?". A topic label ("Results") makes the room
  read the slide to learn its point. (The presenter's own 2023 talk, every results slide.)
- **A title with money in it names the quantity**: revenue, a budget, the raise, a price. "Every likely buyer: $84M/year
  in revenue." and "An eighteen-month budget of about $1.8M", never a bare "About $84M a year". Sweep every title that
  holds a currency sign, and render each reworded one, since the added words can wrap it (a pitch deck, 07, A21 and A22,
  2026-11-17: "'about x million' what? should be clear in title. revenue").

- **One idea, one figure, one key number.** The headline is the plain answer; two short statements on two lines when it
  needs two ("Labs ask for free." / "Companies that buy cell data pay."), each read at a glance.
- **One count, deck-wide**: a count the room hears (labs, sites, samples) is the same number on every slide; a subset
  count lives in the reader's layer with its reason in the judge Q&A (a pitch deck showed six labs on 03 and eleven
  elsewhere until the author asked "6 or 11?", 2026-10-26).
- **Every key number traces to a source, kept off the slide.** The slide carries the number and the fewest words that
  make it land; its source, legend and exact statistics go to the speaker notes and the script, read out or shown on
  request (a pitch deck, 2026-11-10: "the text figure legends and fine print on the bottom of the slides is reading busy.
  lets save this info for slide notes and/or script. try to keep the slides lowest essential text"; this replaced the
  one-line source in the foot slot, 2026-10-26).
- **Name the field's terms for the other room at first mention.** A concrete noun plus a five-word gloss on the slide
  where it first appears: "DMSO, no drug" under the first micrograph, then "DMSO vehicle control: solvent only, no drug"
  where the controls are compared, and "same cells: U2OS, same protocol: Cell Painting" instead of "same cells" (a pitch
  deck 03a, 2026-11-10: "which cells? ... vehicle control DMSO concept should be introduced for non-bio ML folks").

- **Evidence, then the so-what, then the fix, on one slide**: the chart, what it costs in the audience's terms with an
  icon each ("hits don't replicate, data won't pool, models learn the lab"), then the one number the product changes.
- **Plain words a non-native-English investor can read**: no jargon, acronyms or "platform" (Seibel); field terms in the
  reader's layer, checked by a scientist for truth.
- **Comparisons stay fair**: each tool gets the question it answers, your own gaps are said ("fluorescence only
  today") and point to the tools that cover them (a pitch deck, 08; a judge flagged the first, unfair version).
- **Show the work as it really runs**: captures of the running work in the real object's photo, in true perspective,
  each captioned with what made it (an art pitch, 2026-10-25: "realistic").
- **The founder's role reads between the lines** when the plan needs a different leader: "a leader" first in what the
  company needs, the founder as scientific lead, the full statement in the script.
- **One colour, one meaning**: the accent marks the one point and the base colour the field (a pitch deck: pink for the
  one lab or outlier, green for the field); design-practice owns colour.

## Words, type and density

- **Headline numbers answer the reader's question.** For a funder that is money, data and the field's direction,
  each with a source; the team's own evidence sits one line below (a pitch deck's one-pager, 2026-11-01: lab-ID and
  drift stats "not super helpful, focus on FRO financial, data, trend landscape"; swapped for $1.8B, 120M, $30-50M).
- **Word budgets.** Headline: the answer in ten words or fewer, two short lines at most. A talk slide: 30 to 50 words,
  labels included; a pitch deck settled near 35 (506 words over 15 talk slides) after two rounds of "at least 50% fewer
  words". Labels: one or two lines, siblings of even length. Godin's six words a slide (2007) is the far end; the
  script carries the rest, and slides reinforce the voice rather than repeat it. Labels that name the data (a lab's
  number on its column or row) stay on stage whatever the count; cut prose first (a pitch deck, 05, 2026-10-26: numbering
  only lab 2 read as "only lab 2 labelled?").
- **Type the back row reads.** Kawasaki's floor is 30 points, or the oldest listener's age halved, because a room reads
  ahead of the speaker (2005). On a 1280 px HTML slide: nothing on stage under 22 px (keys, ticks, kickers and links
  included), headlines about 44 px, the key number 56 px or more; text near the top reads best from the back (Hale).
  Raising the floor forces the cuts: what no longer fits moves to the reader's layer (a pitch deck, 26 Oct 2026: floor
  18 to 22 px on all 15 views). html-slide-deck's deck-stats (`--floor 22`) and view-audit measure it.
- **Density: a few zones, each full.** The figure fills its zone, about half the slide or more, with the key number
  beside it; space goes around the zones, not scattered inside them; everything else moves to the reader's layer (the
  PDF) or the script. Expect each round to ask for fewer words, so start lean (1,445 to 823 stage words in one day,
  25 Oct 2026, story intact).
- **Numbers in words on stage** ("six times", "14–22%"), exact statistics in the reader's layer; every axis says which
  way is good ("1 = perfect agreement").
- **Motion only when it is the evidence**: a point landing on the map, a bar growing to its value, one move per click,
  ending on a frame that reads still. Hale lists animations and transitions among a deck's distractions; html-slide-deck
  owns how motion is built.

## Figures that carry a slide

- **One message per figure, written on it**, as the headline or a label at the mark (Rougier et al. 2014: "Identify your
  message"; Hale: "CliffsNotes right on the slide"), so the room gets the point at a glance.
- **The form follows the message**: a line with one threshold for change over time, a waffle of rounded squares for
  counts and money, sorted bars for a few items, a scatter with ρ for two measures, a confusion matrix with chance for a
  classifier, paired images on one scale for before and after, three to five icon steps for a process, a check table
  for tools. Vary the forms across the deck; the full table is in `references/slide-patterns.md`.
- **One accent point per figure**: the lab, the batch, the target share, your row.
- **A "how does X hurt Y" panel draws the mechanism and keeps the statistic as its number.** Two arrows from the same
  normal, one as usual with a check, one turned by the drift with a cross, and the rank correlation beside them; the
  scatter of every batch moves to the reader's line. A scatter alone shows that, not how (a pitch deck, 04c,
  2026-11-09: "cluttered and noisy. how does batch drift negatively affect a bioactive drug's phenotypic profile
  estimation?").
- **Real data and real objects**: micrographs with a scale bar and a channel key, the running product; no screenshots on
  stage, which are small, busy and slow to read (Hale).
- **Check it at the size the room sees it**, scaled down and from across a room (Wilke, ch. 24), then with
  page-legibility-check; captions that explain how to read it go to the reader's layer (Rougier: "Captions Are Not
  Optional").

## Icons

- **An icon names a noun the room must hold** (labs, plates, money, time, people) or a step in a process. Clip art,
  emoji and logos as ornament stay off; logos appear as evidence (the founder's institutions, the tools on the
  landscape).
- **Always beside its word.** Few icons are universal (home, search, print), so labels stay visible; if no icon comes to
  mind in about five seconds, use the word alone (Nielsen Norman Group, 2014: "a word is worth a thousand pictures").
- **One icon per meaning, the same everywhere the noun returns**; simple line icons at one stroke weight in ink, the
  accent only on the icon of the point (design-practice owns the shapes).
- **Big enough for the back row**: 24 px or more on a 1280 px slide; html-slide-deck's view-audit flags smaller ones
  and any without a word.

## Patterns from decks that raised

From SEC filings and company pages (Ginkgo, Recursion, Snowflake, Benchling, Hugging Face, Owkin), in
`references/slide-patterns.md`: borrow a shape the room knows; name the data asset with a count that grows; two sides,
one line each; who pays, as names and numbers; pre-empt the free alternative.

From a biotech services deck (Axiom Bio, 2025), in the same file: "Topic:" claim titles, one accent for "us",
them-vs-us cards with cost, the brand mark as a diagram node, evidence grids, headline cases, one quiet frame.

## Appendix boards

- One board per question a judge might ask; the headline is the plain answer; the top line names the question and the
  talk slide it backs ("A9, if asked whether it changes the answer, from slide 05"). An index board maps questions to
  boards. A board the talk keeps needing moves into the talk as a view of the slide it backs.
- **The pitch is the pitch; the supporting science sits behind links.** The talk carries the minimum science and
  figures that still compel, and the appendix is an index that links each judge question out to the board, document
  or result that answers it, so the printed deck stays short. When half the room is from another field, the talk
  still owes it the basics at first mention, a gloss or one small figure each: for ML people at a cell-imaging
  pitch, what cell image data is, how staining makes the image, signal against noise, a drug's mechanism of action
  (a pitch deck, 2026-11-17: "pitch should be pitch, appendix link out to supporting science and figures. use minimum
  necessary compelling science and figures for pitch. will have to introduce ML folks to cell image data, ICC,
  signal and noise, MoA of bioactive(s)").
- **One deck for a second room.** When the same deck must also serve another community (open science, DeSci, a
  patient group), keep one deck: say its core value once on stage in that room's words, put its questions on the board
  that already owns them, and link the open code or data where the room will look. a pitch deck, 2026-10-26 ("ready for
  desci community"): 06 says "Labs own their data, earn a share", 10 links the MIT code, A24 adds "open code and data,
  today" beside "No crypto token", and the README gains "Open, owned, verifiable".

## Script and Q&A

- Time the spoken words (about 130 a minute); keep the talk under five minutes with room to breathe (a pitch deck: 4:20).
- A prompter script has three levels by size and indent: the one-minute spine large, supporting points smaller, detail
  smallest and indented, so the speaker can cut to any length live. Each audience's path (funder, bio VC, AI VC, bio
  colleague, ML colleague) is marked by highlight, key facts carry their citation, and room is left for the speaker to
  choose (a pitch deck's prompter, 2026-11-19: "3 levels of detail, text size and indentation"; "multiple paths,
  audiances. some room for human to operate"; "key facts citated w/ reference").
- Each slide gets its spoken lines, a cue for every click, and "precision to hold" notes: what is true, what to say,
  what the numbers rest on.
- Judge Q&A answers the hard questions with the evidence and its limits ("seven wells: an example, not proof").
- Script and Q&A live in a private folder; the public site carries the deck, the PDF and the documents. Event dates stay
  off public pages, since a deck travels between events; provenance dates (data accessed, analysis rebuilt) can stay;
  partners appear by name once they agree in writing.

## Review rounds

- Ask "is it human?" and "is it legible?" as separate reviews, with numbers: words on stage, smallest text, decimals,
  separator dots. A short panel of single-lens reviewers (story, legibility, design, science, investor) beats a crowd.
- Before a simplification pass, name the pitch's core themes and keep each said once on stage; cut around them (a pitch
  deck, 2026-10-26: biosecurity, decentralization and data as product: "all very important parts of pitch").
- For the pass itself, measure the stage layer first (deck-stats on a print with the reader's layer hidden), give each
  reviewer the stage renders and spoken lines, and ask per view: keep, trim, merge or move, its one sentence, the words
  to delete. A synthesizer counts agreement per edit and lists the splits for the author; apply the unanimous cuts and
  keep what the author asked for in earlier rounds (a pitch deck, 25 Oct 2026: 20 views to 18, talk 4:27 to 4:17).
- When the deck is for a person with a style profile, read it too (`<name>-style`).

## Provenance

One pitch deck, 2026-09-29 to 2026-10-20, from the presenter's notes: under five minutes, little text per slide; lead with the shared
frame; two statements on two lines; a fair competition slide (a judge flagged it); plain words for a
non-native-English VC; founder opens, the question is the punchline; the founder is not the CEO, hinted on slides and
said in the script. 2026-10-26: story beats, the slide set, word budgets, density, figures and icons from primary
sources read that day ("what other slides are strongly recommended? example design of effective slides and
figures? word count, graphic organization and density, use of iconography? make sure skill is thorough"; "key story
beats, pitch should be clear and effective").
