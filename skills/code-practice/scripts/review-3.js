export const meta = {
  name: 'review-3',
  description: 'Three reviewers of different schools review one PR apart, vote blind on each other, and review3.py tallies 2 of 3 and posts one review',
  whenToUse: 'A PR needs a review the person does not have to do. First run review3.py prep; pass {run, repo, pr}. Then review3.py ready RUN.',
  phases: [
    { title: 'Find', detail: 'grug, Ousterhout and maintainability each review the PR alone' },
    { title: 'Vote', detail: 'each votes blind on the findings the other two raised' },
    { title: 'Post', detail: 'review3.py tallies 2 of 3 in code and posts one PR review' },
  ],
}

// Judgement here, rules in code: agents find and vote; review3.py counts the votes, renders and posts.
// Node map: Find (3 agents, apart) -> candidates (code) -> Vote (3 agents, blind) -> Post (1 agent runs the script).
const { run: RUN, repo: REPO, pr: PR } = args || {}
if (!RUN || !REPO || !PR) throw new Error('args needs {run, repo, pr}; run is the folder review3.py prep printed')
const SCRIPT = '"$HOME/.claude/skills/code-practice/scripts/review3.py"'
const MAX_FINDINGS = 8 // per reviewer: noise is what makes people stop reading reviews

const SCHOOLS = [
  { key: 'grug', name: 'grug', skill: 'grug-brain', lens:
    'Complexity is the enemy. Flag an abstraction, layer, config option, class, generic or dependency this change adds ' +
    'that the problem has not earned; name the 80/20 version that would do. Flag clever one-liners that hide which ' +
    'branch fired, refactors far from shore, and new behaviour with no integration-level test or demo. Repetition of ' +
    'simple, obvious code is fine by you. Naming polish and doc comments are not your concern.' },
  { key: 'ousterhout', name: 'Ousterhout', skill: 'deep-modules', lens:
    'Read it as A Philosophy of Software Design. Flag shallow modules and pass-through functions; information leakage ' +
    '(one decision, format or rule known in two places); temporal decomposition; special-general mixture; errors that ' +
    'could be defined out of existence; settings pushed up to callers; non-obvious behaviour with no interface comment. ' +
    'Design it twice: when you flag a design, name the other design. A long function with a simple interface is fine ' +
    'by you; splitting for a line count is not.' },
  { key: 'maintainability', name: 'maintainability', skill: 'code-practice', lens:
    "Read it as code-practice's 'Design rules, read as code', for the next reader in six months. Start from " +
    'audit_new.txt: those are checks that failed, cite them. Then: one job per function (60 lines or fewer), one home ' +
    'per helper (no copied blocks), names that say the job and carry units, a legend line atop each script, README ' +
    'paths that exist, no clutter (v2/_old files, commented-out code), numbers from data or a named rule, comments that ' +
    'say why.' },
]

const FILES = [
  `- ${RUN}/pr.json: title, body, changed files, head and base shas`,
  `- ${RUN}/diff.patch: the diff as GitHub shows it, minus the built pages in generated.txt`,
  `- ${RUN}/head/: the repo at the PR head; read the code around each change here`,
  `- ${RUN}/audit_new.txt: code_audit.py findings new in this PR (empty means none)`,
  `- ${RUN}/generated.txt: pages a script builds, each with its script; do not open these pages, judge the script`,
].join('\n')

const FIND = { type: 'object', required: ['verdict', 'findings'], properties: {
  verdict: { type: 'string', description: 'one line, in your school\'s voice' },
  findings: { type: 'array', maxItems: MAX_FINDINGS, items: { type: 'object',
    required: ['file', 'line', 'severity', 'title', 'why', 'fix'], properties: {
      file: { type: 'string', description: 'path as in the diff' },
      line: { type: 'integer', minimum: 1, description: 'line on the PR head (new side) where the code starts' },
      severity: { type: 'string', enum: ['important', 'nit'] },
      title: { type: 'string', description: 'the claim, one short sentence' },
      why: { type: 'string', description: 'one or two sentences, your school\'s reason' },
      fix: { type: 'string', description: 'one sentence' } } } } } }

const VOTE = { type: 'object', required: ['votes'], properties: {
  votes: { type: 'array', items: { type: 'object', required: ['id', 'agree', 'severity', 'reason'], properties: {
    id: { type: 'string' }, agree: { type: 'boolean' },
    severity: { type: 'string', enum: ['important', 'nit'], description: 'what you would rate it if real' },
    reason: { type: 'string', description: 'one sentence' } } } } } }

const POSTED = { type: 'object', required: ['tally_exit', 'post_exit', 'review_url', 'output'], properties: {
  tally_exit: { type: 'integer' }, post_exit: { type: 'integer' },
  review_url: { type: 'string' }, output: { type: 'string', description: 'last lines the commands printed' } } }

const findPrompt = s => `Review pull request ${REPO}#${PR} as the ${s.name} reviewer. Load the ${s.skill} skill first.
Read these (edit nothing, post nothing to GitHub):
${FILES}
A page built by a script is judged at the script that builds it: skip every page generated.txt lists.

Your school: ${s.lens}

Report only findings you would stake your name on, at most ${MAX_FINDINGS}, most important first. Severity "important"
means it should be fixed before merge: a bug, or a cost this PR adds that will hurt; "nit" means worth fixing, not
blocking. A correctness bug needs the concrete input or command that shows it. Leave out problems this PR does not touch
unless it makes them worse. Zero findings is a fine answer.`

const votePrompt = (s, list) => `You are the ${s.name} reviewer of ${REPO}#${PR}. Load the ${s.skill} skill first.
Your school: ${s.lens}

Other reviewers raised the findings below. You do not know who raised which, and nobody sees your vote. Files:
${FILES}

For each finding, read the code at the cited line, then vote from your school's view:
- agree: the problem is real and worth changing in this PR; give the severity you would give it
- disagree: not real, not worth it, or a taste you do not share; say why in one sentence
Vote on every id exactly once.

${list.map(c => JSON.stringify({ id: c.id, where: `${c.file}:${c.line}`, severity: c.severity, title: c.title,
  why: c.why, fix: c.fix })).join('\n')}`

// ---- Find: three reviewers, separate contexts ----
phase('Find')
const found = await parallel(SCHOOLS.map(s => () =>
  agent(findPrompt(s), { label: `find:${s.key}`, phase: 'Find', schema: FIND })))
const present = SCHOOLS.filter((s, i) => found[i])
const missing = SCHOOLS.filter((s, i) => !found[i]).map(s => s.key)
if (present.length < 2) throw new Error(`only ${present.length} reviewer returned; 2 of 3 needs at least two`)
if (missing.length) log(`missing reviewer: ${missing.join(', ')}; its votes count as abstentions`)

const candidates = SCHOOLS.flatMap((s, i) => (found[i] ? found[i].findings : []).map((f, j) =>
  ({ ...f, id: `${s.key[0]}${j + 1}`, school: s.key })))
log(`${candidates.length} findings: ${present.map(s => `${s.key} ${found[SCHOOLS.indexOf(s)].findings.length}`).join(', ')}`)

// ---- Vote: each school votes blind on the other two schools' findings ----
phase('Vote')
const ballots = await parallel(present.map(s => () => {
  const list = candidates.filter(c => c.school !== s.key)
  return list.length ? agent(votePrompt(s, list), { label: `vote:${s.key}`, phase: 'Vote', schema: VOTE })
    : Promise.resolve({ votes: [] })
}))
const votes = {}
present.forEach((s, i) => {
  const asked = new Set(candidates.filter(c => c.school !== s.key).map(c => c.id))
  const cast = (ballots[i] ? ballots[i].votes : []).filter(v => asked.has(v.id))
  const unique = [...new Map(cast.map(v => [v.id, v])).values()]
  if (unique.length < asked.size) log(`${s.key} left ${asked.size - unique.length} of ${asked.size} unvoted: abstentions`)
  votes[s.key] = unique
})

// ---- Post: the tally and the review are code ----
phase('Post')
const raw = { repo: REPO, pr: PR, findings: candidates, votes, missing_reviewers: missing,
  summaries: Object.fromEntries(present.map(s => [s.key, found[SCHOOLS.indexOf(s)].verdict])),
  // review3.py fingerprint() recounts these after the copy: a dropped row, flipped vote or moved line fails tally
  counts: { findings: candidates.length, votes: Object.values(votes).reduce((n, v) => n + v.length, 0),
    agree: Object.values(votes).reduce((n, v) => n + v.filter(x => x.agree).length, 0),
    line_sum: candidates.reduce((n, c) => n + c.line, 0) } }
const posted = await agent(`Do exactly this and nothing else.
1. Write the JSON below to ${RUN}/raw.json, byte for byte, with the Write tool.
2. Run: python3 ${SCRIPT} tally "${RUN}"
3. Only if step 2 exited 0, run: python3 ${SCRIPT} post "${RUN}"
Return each exit code (post_exit -1 if skipped), the review URL the post printed (empty if none), and the last lines
both commands printed.

${JSON.stringify(raw)}`, { label: 'post', phase: 'Post', schema: POSTED, model: 'sonnet', effort: 'low' })

if (!posted || posted.tally_exit !== 0 || posted.post_exit !== 0) {
  log(`post step failed: ${posted ? posted.output : 'agent died'}`)
}
return { review_url: posted ? posted.review_url : '', tally_exit: posted ? posted.tally_exit : null,
  post_exit: posted ? posted.post_exit : null, output: posted ? posted.output : '', counts: raw.counts,
  missing_reviewers: missing, next: `python3 ${SCRIPT} ready "${RUN}"` }
