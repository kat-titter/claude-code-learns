# The HCI canon, as criteria

Each list below is a set of criteria worded so that more is good, ready to score options against (SKILL.md §3). The
definitions are condensed from the sources named, retrieved 2026-11-05.

## Design Space Analysis and QOC

MacLean, Young, Bellotti and Moran, "Questions, Options, and Criteria: Elements of Design Space Analysis",
Human-Computer Interaction 6(3-4), 201-250, 1991; summary at acawiki.org.
- **Questions**: key issues for structuring the space of alternatives.
- **Options**: possible alternatives.
- **Criteria**: the bases for choosing among the options.
- **Assessments**: whether an option supports or challenges a criterion; drawn solid (positive) or dashed (negative)
  between an option and a criterion.
- Against IBIS: a question structures the exploration of options, where an IBIS issue can be about anything; criteria
  are written after reflection, where IBIS arguments capture discussion on the fly. A QOC is a condensation of the
  history that keeps the elements that matter for argument.
- The paper's test of the notation includes that it is a co-product of the design process, made while designing.

UCT MSc-IT notes, "Design Rationale" (cs.uct.ac.za, 2010): a rationale lays out which options were considered and why;
when a better solution appears later it shows whether that solution was considered and discarded or never considered;
same context, reuse the rationale unchanged; changed context, decide anew in the light of the old decisions. Example:
Q how to keep users from getting lost in menus; O flatten to depth three, show the path as text, stack menus visibly;
C screen space, functions available, accuracy of the user's sense of place.

## Nielsen's ten usability heuristics

Jakob Nielsen, nngroup.com, 1994, last reviewed 2024-01-30. Rules of thumb, not specific guidelines.
1. **Visibility of system status**: keep users informed through appropriate feedback within a reasonable time.
2. **Match between system and the real world**: the users' words and concepts, real-world conventions, natural order.
3. **User control and freedom**: a clearly marked emergency exit (undo, redo, cancel) from an unwanted action.
4. **Consistency and standards**: the same words, situations and actions mean the same thing; platform conventions
   (Jakob's law: people spend most of their time in other products).
5. **Error prevention**: remove error-prone conditions, or check for them and confirm before the user commits.
6. **Recognition rather than recall**: elements, actions and options visible; nothing to remember between screens.
7. **Flexibility and efficiency of use**: shortcuts for experts, hidden from novices; frequent actions tailorable.
8. **Aesthetic and minimalist design**: every extra unit of information competes with the relevant ones.
9. **Help users recognize, diagnose and recover from errors**: plain language, the precise problem, a constructive fix.
10. **Help and documentation**: best when not needed; otherwise there, for the task at hand.

## Shneiderman's eight golden rules of interface design

Ben Shneiderman, cs.umd.edu, from Designing the User Interface, sixth edition (2016), section 3.3.4; original list 1985.
1. **Strive for consistency**: same action sequences, terms, colour, layout, fonts; few, explained exceptions.
2. **Seek universal usability**: novice to expert, ages, disabilities, locales, devices; explanations and shortcuts.
3. **Offer informative feedback**: modest for frequent minor actions, substantial for rare major ones.
4. **Design dialogs to yield closure**: a beginning, middle and end, with a confirmation that completes the group.
5. **Prevent errors**: grey out what does not apply, reject bad input at the field, and recover without retyping.
6. **Permit easy reversal of actions**: undo relieves anxiety and invites exploration.
7. **Keep users in control**: no surprises, no changes in familiar behaviour, no tedious sequences.
8. **Reduce short-term memory load**: seven plus or minus two chunks; nothing carried from one display to another.

## Norman's vocabulary

Don Norman, The Design of Everyday Things (1988; revised 2013); summarized from en.wikipedia.org.
- **Affordance**: what the thing can do, as a relation between the thing and the person (a door can be pushed or pulled).
- **Signifier**: the mark that tells which (a flat plate: push; a bar: pull); added in the revision to separate the cue
  from the capability.
- **Gulf of execution**: the gap between what the person wants to do and the sequence the thing demands (the projector
  that needed a long, unclear sequence to set up).
- **Gulf of evaluation**: the gap between the thing's state and what the person can see of it.

## Laws of sizes, counts and time

Fitts (time to a target falls with size and nearness), Hick (choice time grows with the number of options), the Doherty
threshold (answer within 400 ms), Gestalt proximity, similarity and common region, and Jakob's law are applied with
their cases in app-design/references/great-apps.md.
