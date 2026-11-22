// Runs review-3.js against stub agents: the review3.py it runs, what it returns, and when raw rides back.
//   node review-3.test.mjs      exits 1 with the failing assertion, 0 when every case holds
// Stubs as the Workflow runtime behaves: agent() returns null for a dead agent; parallel() maps a throw to null.
import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'

const src = readFileSync(new URL('./review-3.js', import.meta.url), 'utf8')
const body = "'use strict';\n" + src.replace(/^export const meta =/m, 'const meta =')
const AsyncFunction = (async () => {}).constructor
const run = new AsyncFunction('agent', 'parallel', 'phase', 'log', 'args', body)
const parallel = thunks => Promise.all(thunks.map(t => t().catch(() => null)))

const ARGS = { run: '/runs/o-r-7', repo: 'o/r', pr: 7, script: '/skills dir/review3.py' }
const OK = { tally_exit: 0, post_exit: 0, review_url: 'https://github.com/o/r/pull/7#pullrequestreview-1', output: '' }

// each reviewer raises one finding and agrees with every finding it is shown; the post agent returns `post`
async function review(post, args = ARGS) {
  const prompts = {}
  const agent = async (prompt, opts) => {
    prompts[opts.label] = prompt
    if (opts.label.startsWith('find:')) return { verdict: 'v', findings: [{ file: 'a.py', line: 2, severity: 'nit',
      title: 't', why: 'w', fix: 'f' }] }
    if (opts.label.startsWith('vote:')) return { votes: [...prompt.matchAll(/"id":"(\w+)"/g)].map(m =>
      ({ id: m[1], agree: true, severity: 'nit', reason: 'r' })) }
    return post
  }
  return { out: await run(agent, parallel, () => {}, () => {}, args), prompts }
}

const good = await review(OK)
const failed = await review({ ...OK, post_exit: 1, review_url: '' })
const dead = await review(null)
const refused = await review(OK, { ...ARGS, script: undefined }).catch(e => e)

const cases = [
  ['the post runs the review3.py prep named, quoted, never a guessed install path', () => {
    assert.match(good.prompts.post, /python3 "\/skills dir\/review3\.py" tally "\/runs\/o-r-7"/)
    assert.match(good.prompts.post, /python3 "\/skills dir\/review3\.py" post "\/runs\/o-r-7"/)
    assert.ok(!good.prompts.post.includes('$HOME'))
  }],
  ['the ready command is left to review3.py: no second copy here', () => assert.ok(!JSON.stringify(good.out).includes(' ready '))],
  ['a good post returns no raw', () => assert.ok(!('raw' in good.out))],
  ['a failed post returns raw whole, to rerun tally from', () => {
    assert.equal(failed.out.raw.findings.length, 3)
    assert.deepEqual(failed.out.raw.counts, failed.out.counts)
  }],
  ['a dead post agent returns raw', () => assert.equal(dead.out.raw.findings.length, 3)],
  ['args without script are refused', () => assert.match(String(refused), /args needs \{run, repo, pr, script\}/)],
]
for (const [name, test] of cases) {
  test()
  console.log(`ok  ${name}`)
}
console.log(`review-3.js: ${cases.length} cases pass against stub agents`)
