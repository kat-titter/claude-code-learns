// Runs skills/workflow-design/references/check-repair.js against stub agents and checks what it returns.
//   node tests/check-repair.test.mjs      exits 1 with the failing assertion, 0 when every case holds
// The stubs follow the Workflow runtime's documented rules: agent() returns null for a dead agent; pipeline() drops an
// item to null only when a stage throws; Date.now() and Math.random() throw (they would break resume).
import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'

const src = readFileSync(new URL('../skills/workflow-design/references/check-repair.js', import.meta.url), 'utf8')
// 'use strict' as in a module, so an undeclared variable throws here as it would in the runtime
const body = "'use strict';\n" + src.replace(/^export const meta =/m, 'const meta =')
assert.ok(!body.includes('export const meta'), 'the template no longer starts with `export const meta =`')

// per unit: what its build agent returns (default: a summary), each check's exit code in order, and which repair
// rounds die (1-based); null is a dead agent
const PLAN = {
  'pass-first': { checks: [0] },
  'fix-once': { checks: [1, 0] },
  'never': { checks: [1, 1, 1] },
  'dead-check': { checks: [null, null, null] },
  'dead-build': { build: null, checks: [0] },
  'late-pass': { checks: [1, 1, 0], deadRepairs: [2] },
}
const MAX_REPAIRS = 2
const calls = []
const count = (kind, id) => calls.filter(c => c.kind === kind && c.id === id).length
const seen = {}
const thrown = []

async function agent(prompt, opts = {}) {
  const [kind, id] = opts.label.split(':')
  calls.push({ kind, id, prompt })
  const p = PLAN[id]
  if (kind === 'build') return 'build' in p ? p.build : { summary: `built ${id}`, files_changed: [`${id}.py`] }
  if (kind === 'repair') {
    const round = count('repair', id)
    return (p.deadRepairs || []).includes(round) ? null : { cause: `cause ${round}`, rule: `rule for ${id}`, files_changed: [`${id}.py`] }
  }
  if (kind === 'check') {
    seen[id] = (seen[id] || 0) + 1
    assert.ok(seen[id] <= p.checks.length, `${id}: check ${seen[id]} was not expected`)
    const code = p.checks[seen[id] - 1]
    return code === null ? null : { cmd: `check ${id}`, exit_code: code, output_tail: code ? 'FAILED' : 'ok' }
  }
  throw new Error(`unexpected agent label ${opts.label}`)
}
const pipeline = (items, ...stages) => Promise.all(items.map(async (item, i) => {
  try {
    let v = item
    for (const stage of stages) v = await stage(v, item, i)
    return v
  } catch (e) { thrown.push(e); return null }
}))
const parallel = thunks => Promise.all(thunks.map(t => t().catch(e => { thrown.push(e); return null })))
const Math_ = Object.create(Math, { random: { value: () => { throw new Error('Math.random() breaks resume') } } })
class Date_ extends Date {
  constructor(...a) { if (!a.length) throw new Error('new Date() breaks resume'); super(...a) }
  static now() { throw new Error('Date.now() breaks resume') }
}

const args = {
  context: 'test change',
  units: Object.keys(PLAN).map(id => ({ id, task: `change ${id}`, files: [`${id}.py`], check: `check ${id}` })),
  maxRepairs: MAX_REPAIRS,
}
const AsyncFunction = (async () => {}).constructor
const run = new AsyncFunction('agent', 'pipeline', 'parallel', 'phase', 'log', 'args', 'Math', 'Date', body)
const out = await run(agent, pipeline, parallel, () => {}, () => {}, args, Math_, Date_)

const cases = [
  ['no stage threw', () => assert.deepEqual(thrown.map(String), [])],
  ['passing units pass, in order', () => assert.deepEqual(out.passed, ['pass-first', 'fix-once', 'late-pass'])],
  ['units that never pass escalate', () => assert.deepEqual(out.escalate.map(e => e.id), ['never', 'dead-check'])],
  ['a dead check agent is a failure, not a pass', () => assert.equal(out.escalate[1].exit_code, 'check agent died')],
  ['a dead build agent drops its unit unchecked', () => {
    assert.deepEqual(out.dropped, ['dead-build'])
    assert.equal(count('check', 'dead-build'), 0)
  }],
  ['repairs stop at the round limit', () => {
    assert.equal(count('repair', 'never'), MAX_REPAIRS)
    assert.equal(count('repair', 'dead-check'), MAX_REPAIRS)
    assert.deepEqual(out.escalate[0].tried, ['cause 1', 'cause 2'])
  }],
  ['a unit that passes first is never repaired', () => assert.equal(count('repair', 'pass-first'), 0)],
  ['only a repair that passed leaves a rule, not a failed earlier one', () => assert.deepEqual(out.rules, [{ unit: 'fix-once', cause: 'cause 1', rule: 'rule for fix-once' }])],
  ['each repair is scoped to its unit and told what failed before', () => {
    const repairs = calls.filter(c => c.kind === 'repair')
    for (const r of repairs) assert.match(r.prompt, new RegExp(`Scope: edit only ${r.id}\\.py\\.`))
    assert.match(repairs.filter(r => r.id === 'never')[1].prompt, /Earlier repairs that did not pass: cause 1/)
  }],
]
// maxRepairs: 0 means check only: a failing unit escalates with no repair agent
const before = calls.length
seen.never = 0
const zero = await run(agent, pipeline, parallel, () => {}, () => {}, { ...args, units: args.units.filter(u => u.id === 'never'), maxRepairs: 0 }, Math_, Date_)
cases.push(['maxRepairs 0 runs no repair', () => {
  assert.deepEqual(zero.escalate.map(e => e.id), ['never'])
  assert.equal(calls.slice(before).filter(c => c.kind === 'repair').length, 0)
}])

for (const [name, test] of cases) {
  test()
  console.log(`ok  ${name}`)
}
console.log(`check-repair.js: ${cases.length} cases pass over ${Object.keys(PLAN).length} stub units`)
