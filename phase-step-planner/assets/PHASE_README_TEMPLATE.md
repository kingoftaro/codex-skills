# Phase {{PHASE_ID}} implementation index

## Authority

- Phase plan: `{{PHASE_PLAN_PATH}}`
- Applicable project rules: `{{AGENTS_PATHS}}`
- Live status: `STATUS.md`
- Previous accepted baseline: `{{PREDECESSOR_EVIDENCE}}`
- Phase directory: `{{PHASE_DIRECTORY}}`

This file describes order and dependencies. It does not claim that a step is complete.

## Phase outcome

{{ONE_PHASE_OUTCOME}}

## Non-goals

- {{NON_GOAL}}

## Stable invariants

- {{INVARIANT_AND_EXECUTABLE_GUARD}}

## Step dependency map

| Step document | One outcome | Depends on | Primary risk boundary | Specification state |
|---|---|---|---|---|
| `{{STEP_DOCUMENT}}` | {{OUTCOME}} | {{DEPENDENCY}} | {{RISK}} | detailed / outline / accepted / deferred |

## Progression rule

At most one step may be `detailed`, and it must match the current executable
step in `STATUS.md`. Keep draft handoffs non-executable, normally `STALE`; draft
revisions do not require validator or hash cycles. When a STEP is ready, run
the review required by its Fast, Standard, or High-risk route, record its
checkpoint, and validate it. Only a handoff whose review result and
authoritative validator are both `PASS` may be implemented. Verify it and
update `STATUS.md` before detailing or starting its successor. If observed
repository state and intended contracts disagree, keep the handoff `STALE` or
`BLOCKED` until the contradiction is resolved; do not let either source
silently redefine the other.

## Final phase gates

- Functional: {{FUNCTIONAL_GATE}}
- Safety/privacy: {{SAFETY_GATE}}
- Reliability/recovery: {{RELIABILITY_GATE}}
- Quality/resource: {{QUALITY_GATE}}
- Deferred release blockers: {{DEFERRED_BLOCKERS}}
