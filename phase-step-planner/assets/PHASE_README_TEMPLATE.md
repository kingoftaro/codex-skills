# Phase {{PHASE_ID}} implementation index

## Authority

- Phase plan: `{{PHASE_PLAN_PATH}}`
- Applicable project rules: `{{AGENTS_PATHS}}`
- Live status: `STATUS.md`
- Previous accepted baseline: `{{PREDECESSOR_EVIDENCE}}`

This file describes order and dependencies. It does not claim that a step is complete.

## Phase outcome

{{ONE_PHASE_OUTCOME}}

## Non-goals

- {{NON_GOAL}}

## Contract registry

This is the single documentation authority for stable phase constraints. Point
to executable definitions and guards instead of copying their contents into
STATUS or every STEP.

| ID | Kind | Authoritative path or symbol | Guard or evidence | Current rule |
|---|---|---|---|---|
| `{{CONTRACT_ID}}` | invariant / interface / data / boundary / compatibility | `{{AUTHORITY_PATH_OR_SYMBOL}}` | `{{GUARD_OR_EVIDENCE}}` | {{CURRENT_RULE}} |

## Step dependency map

| Step | One outcome | Depends on | Primary risk boundary | Specification state |
|---|---|---|---|---|
| `{{STEP_ID}}` | {{OUTCOME}} | {{DEPENDENCY}} | {{RISK}} | detailed / outline |

## Progression rule

Only the current detailed step may be implemented. After review, compare affected documents with the final code and evidence, inspect Git state, and report stale or uncommitted work with a recommended action. Update or commit only with existing authority, and do not detail a successor from contradictory inputs. If repository reality contradicts a step, revise the step from evidence rather than improvising in code.

## Final phase gates

- Functional: {{FUNCTIONAL_GATE}}
- Safety/privacy: {{SAFETY_GATE}}
- Reliability/recovery: {{RELIABILITY_GATE}}
- Quality/resource: {{QUALITY_GATE}}
- Deferred release blockers: {{DEFERRED_BLOCKERS}}
