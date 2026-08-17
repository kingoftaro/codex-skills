# {{STEP_ID}}: {{STEP_NAME}}

## Outcome

- Deliver: {{SINGLE_VERIFIABLE_OUTCOME}}
- Out of scope: {{EXPLICIT_NON_GOAL}}

## Contract references and delta

- Required predecessor: {{PREDECESSOR_OR_NONE}}

| Contract ID | This step's delta |
|---|---|
| `{{CONTRACT_ID}}` | {{UNCHANGED_OR_EXACT_DELTA}} |

Reference stable phase contracts by ID. State only the change introduced by this
STEP; do not copy unchanged interface definitions into this file.

## File boundary

Delete unused rows instead of inventing filler.

| Access | Path or scope | Purpose |
|---|---|---|
| Add/modify | `{{WRITE_PATH_OR_SCOPE}}` | {{WRITE_PURPOSE}} |
| Read only | `{{READ_ONLY_PATH_OR_SCOPE}}` | {{READ_PURPOSE}} |
| Forbidden | `{{FORBIDDEN_PATH_OR_SCOPE}}` | {{BOUNDARY_REASON}} |

Stop and report before writing outside this boundary.

## Risk controls

- Active packs: {{NONE_OR_COMMA_SEPARATED_BACKTICKED_PACK_NAMES}}
- Default policy: no new external effects, persisted-data changes, public
  compatibility changes, or trust-boundary changes unless an active pack
  explicitly defines and tests them.

Use `none` or comma-separated backticked names. Add only the triggered sections
from the risk-pack table in the planner's bundled `FAILURE_PATTERNS.md`.

## Acceptance

- Run from: `{{WORKDIR}}`
- Commands: `{{EXACT_COMMANDS}}`
- Required observations: {{CURRENT_SUCCESS_AND_FAILURE_EVIDENCE}}

Record actual exit codes and results; do not copy historical counts.

## Stop conditions

- Stop when: {{STOP_CONDITION}}
- Do not: {{FORBIDDEN_SHORTCUT}}

Do not update phase acceptance or detail the next STEP from implementation claims.
