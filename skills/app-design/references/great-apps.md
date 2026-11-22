# What makes great apps great

Guidelines for the apps people come back to, each with the principle behind it and the case it came from (a DJ studio's design audit, 2026-10-24: six specialist reviews, each finding refuted or kept by a sceptic). Momentum and delight, never tricks.

- **The primary action is the biggest, roundest, nearest target, and it repeats wherever the loop restarts** (Fitts's law: time to a target falls with its size and distance). A 14 px '▶ play' pill under the deck view was the only way to hear her Keep while every card led with a 55 px disc; the strip takes the same disc and the mix play grows to 44 px on touch.
- **An action sits beside its effect; reference material folds, the action does not** (progressive disclosure, Gestalt proximity). The steer box, the feature the product is named for, was the last element of a closed fold under a 300 px map and a nine-row key, and its result landed out of view; it now sits above the cards it redraws, and the 'render' button sits under the dot it renders.
- **Absence of a mark means fine** (figure-ground, data-ink). 160 boxed ✓ formed a grid the eye read before the 6 flags; a bare quiet tick lets the flags be the figure.
- **One control, drawn once.** A figure shows each control in one place, the real one (the sink's handle on the front view), and that one works; copies on other views or beside the figure read as three handles (an art piece's sink drawing, 2026-10-26: "showing handle in 3 different places ... one should be enough").
- **One affordance per kind of control, learned once** (Gestalt similarity, consistency). Three disclosure marks on one screen, four play buttons and four pressed looks across the tabs become one arrow, one disc, one white fill.
- **Vary the element, not just the words.** A page made of the same two-column table (a short word, then its detail) over and over
  reads as a form; turn the detail blurbs into prose or a figure and keep tables for real comparisons. (A process doc,
  2026-10-26: "too many tables with col 1 simple word col 2 detail"; a tech-detail step became one paragraph.)
- **Answer within 400 ms, at the control that was pressed** (the Doherty threshold; visibility of system status). A press state on every button, the pressed Keep kept lit while it saves, a pulse while a cold take buffers, a one-shot glow when a render lands; disabling all three verdict buttons read as 'switched off' and a silent card swap missed the moment the loop paid off.
- **The plain story first, the detail one click away** (progressive disclosure). Eighteen figures sat between the map and the table it promised, seven screens down; chapters fold with the first open, and a 42-word description becomes its first sentence with the rest in the fold.
- **Fewer choices first, the full list one step away** (Hick's law). Pick unfolded eight named buttons although the take the person had just A/B'd was pre-marked; the default plus 'another take' folded is one keypress.
- **Entry points at the top of the reading order** (discoverability). 'new playlist: start here' sat after the map, the figures and a count line; a 'start here' that is not at the start contradicts itself.
- **A stable frame with shared edges across views** (Gestalt common region). Each tab set its own width, so the brand, switch and nav jumped up to 200 px between tabs and the about card ran 21 px wider than the set panel; one --w and one card rule.
- **Phones get a true layout, not a shrunk one** (Fitts on touch, the thumb zone). On a 375 px screen the transition title sticks, the page tabs move to a bottom bar in thumb reach, the playlist table pins its action column, and 44 px targets never overlap. A canvas forced wider than the screen is not scrollable when a sideways finger already means scrub: a DJ tool's deck drew 640 px wide on a 375 px phone and the second half of every transition was unreachable; it now draws at the screen's width and redraws on resize, and labels that would run past an edge sit inside it or are left out (2026-10-24).
- **Momentum and delight come from the loop paying off visibly, never from dark patterns** (variable reward, framed as momentum). The reward is a new take lighting as it lands and a hollow dot filling, with 'stop after this one' always in reach; no streaks, nags, fake urgency or hidden steps (the render queue's honest countdown is the model).
- **A switch between versions shows both, in words.** Two labelled segments (name and one plain word each), the current one
  filled, each a link to the same page in the other version; an icon can mark the product but is not the control. (a DJ tool
  studio, 2026-10-24: a round icon that toggled A and B on click read as a logo; "toggle between version i and version ai
  should be more clear in app, as demo" became "p[i]lot human | p[ai]lot algorithm".)
- **First clicks are instant, waits are named.** Compute what a click will need before the click (warm the cache at start
  and after each job), and when a wait still happens, show a skeleton and past about 2 s one quiet line saying what is being
  done. Three blank cards for 7 seconds read as broken. (a DJ studio, 2026-10-24: a cold transition took 4 to 7 s of
  empty skeletons; cards are now made after every render job.)
- **Borrow the conventions people already know** (Jakob's law: users spend most of their time on other apps). Before
  designing an interaction, look at how the field's leading apps do it (music: Spotify, SoundCloud, Beatport, rekordbox)
  and take their patterns; forms from a neighbouring science travel well too (flow-cytometry gates to pick songs, chemical
  safety signs for warnings, GitHub's contribution grid for coverage). Data from a service carries that service's small
  mark where it shows. (a DJ studio, 2026-10-27: "look @ spotify, beatport, soundcloud. get ideas for common intuitive
  design practices for interacting with music"; "learn from single cell flow, 'gates'"; "add spotify, beatport,
  soundcloud logos where appropriate".)
