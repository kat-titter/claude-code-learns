export const meta = {
  name: 'check-repair',
  description: 'Build units in parallel, gate each on its check exit code, repair failing units alone, escalate the rest',
  whenToUse: 'A change that splits into units with their own files and a command that checks each one',
  phases: [
    { title: 'Build', detail: 'one agent per unit, its files only' },
    { title: 'Check', detail: 'run the unit check, report the exit code' },
    { title: 'Repair', detail: 'failing units only, a scope line, a round limit' },
    { title: 'Rules', detail: 'each repair cause as a rule for the next split' },
  ],
}

// args: {
//   context: 'what the change is and why, shared by every unit',
//   units: [{ id: 'adapter-a', task: 'what to change', files: ['src/a.py'], check: 'python -m pytest tests/test_a.py' }],
//   maxRepairs: 3,
// }
// The loop lives inside each unit (build, check, repair); the graph lives between units (none waits for another).
// Units must own disjoint files: they share one checkout.

const A = args || {}
const UNITS = A.units || []
const MAX_REPAIRS = A.maxRepairs ?? 3   // 0 means check only

const BUILT = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'files_changed'],
}
// the check is a number the script gates on, never an agent's verdict
const CHECKED = {
  type: 'object',
  properties: {
    cmd: { type: 'string' },
    exit_code: { type: 'integer' },
    output_tail: { type: 'string', description: 'the last 40 lines of output, verbatim' },
  },
  required: ['cmd', 'exit_code', 'output_tail'],
}
const REPAIRED = {
  type: 'object',
  properties: {
    cause: { type: 'string', description: 'why the check failed, in one line' },
    rule: { type: 'string', description: 'the rule that would have prevented it, for whoever splits the work next time' },
    files_changed: { type: 'array', items: { type: 'string' } },
  },
  required: ['cause', 'rule', 'files_changed'],
}

const scope = u => `Scope: edit only ${u.files.join(', ')}. Other units are editing other files in this checkout at the same time; do not touch them, and do not commit, stash or reset.`

const check = (u, phase) => agent(
  `Run exactly this command from the repository root and report it, its exit code and the last 40 lines of output:\n${u.check}\nDo not fix anything.`,
  { label: `check:${u.id}`, phase, schema: CHECKED, effort: 'low' })

const passed = c => c !== null && c.exit_code === 0   // a dead check agent is a failure, not a pass

const results = await pipeline(UNITS,
  u => agent(`${A.context}\n\nYour unit: ${u.id}\n${u.task}\n\n${scope(u)}`,
    { label: `build:${u.id}`, phase: 'Build', schema: BUILT }),
  async (built, u) => {
    if (!built) return null   // a dead build agent comes back as null, not a throw: drop the unit, never check old files
    let c = await check(u, 'Check')
    const repairs = []
    for (let r = 0; r < MAX_REPAIRS && !passed(c); r++) {
      const fix = await agent(
        `${A.context}\n\nUnit ${u.id} fails its check.\nTask: ${u.task}\nCommand: ${u.check}\nExit code: ${c ? c.exit_code : 'the check agent died'}\nOutput:\n${c ? c.output_tail : ''}\n\n` +
        `Fix the cause of this failure and nothing else. ${scope(u)}` +
        (repairs.some(Boolean) ? `\nEarlier repairs that did not pass: ${repairs.filter(Boolean).map(x => x.cause).join('; ')}` : ''),
        { label: `repair:${u.id}:${r + 1}`, phase: 'Repair', schema: REPAIRED })
      repairs.push(fix)   // null for a dead repair agent, so the last entry is always the last round's
      c = await check(u, 'Repair')
    }
    return { id: u.id, pass: passed(c), check: c, built, repairs }
  })

const done = results.filter(Boolean)
const lost = UNITS.length - done.length
if (lost) log(`${lost} unit(s) dropped by a failed build agent: counted as escalated`)
const escalate = done.filter(r => !r.pass).map(r => ({
  id: r.id, exit_code: r.check ? r.check.exit_code : 'check agent died', tail: r.check && r.check.output_tail,
  tried: r.repairs.filter(Boolean).map(x => x.cause),
}))
log(`${done.filter(r => r.pass).length}/${UNITS.length} units pass; ${escalate.length + lost} escalate`)

// the rule-writing step: only the repair whose check passed names a known cause (none if that round's agent died);
// plain code collects them, the main session routes them (capture-lesson)
phase('Rules')
const rules = done.filter(r => r.pass && r.repairs.length && r.repairs[r.repairs.length - 1]).map(r => {
  const last = r.repairs[r.repairs.length - 1]
  return { unit: r.id, cause: last.cause, rule: last.rule }
})

return {
  passed: done.filter(r => r.pass).map(r => r.id),
  escalate,
  dropped: UNITS.map(u => u.id).filter(id => !done.some(r => r.id === id)),
  rules,
}
