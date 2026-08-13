# Phase {{PHASE_ID}} current status

> This is the phase's single verified snapshot. Update it only from repository evidence after acceptance; do not use it as a speculative plan.

## Snapshot identity

- Updated at: {{TIMESTAMP_WITH_TIMEZONE}}
- Repository root: `{{REPOSITORY_ROOT}}`
- Branch: `{{BRANCH}}`
- Verified Git checkpoint: `{{COMMIT_OR_UNCOMMITTED_EXPLANATION}}`
- Worktree state: {{CLEAN_OR_SUMMARY}}
- Post-review synchronization check: {{DOCUMENT_CODE_GIT_STATE_AND_RECOMMENDED_ACTION}}

## Position

- Phase state: not started / in progress / development complete / accepted / release blocked
- Last accepted step: `{{LAST_ACCEPTED_STEP}}`
- Next outlined step: `{{NEXT_STEP}}`

## Current handoff

- Handoff schema version: 1
- Current executable step: `{{CURRENT_STEP_DOCUMENT}}`
- Current STEP checkpoint: `sha256:{{CURRENT_STEP_SHA256}}`
- Repository/worktree checkpoint reviewed: {{REVIEWED_REPOSITORY_CHECKPOINT}}
- Result: {{PASS_STALE_OR_BLOCKED}}

Only `PASS` is executable. Recompute the STEP checkpoint after every material
STEP edit and repeat the consistency review when code, documents, or the
reviewed worktree changes. The reviewed checkpoint may be a commit or an exact
dirty-worktree description, but STATUS and STEP must record the same value.

## Verified capabilities

| Capability | Code evidence | Test/evidence | State |
|---|---|---|---|
| {{CAPABILITY}} | `{{PATH_OR_SYMBOL}}` | `{{TEST_OR_REPORT}}` | implemented / tested / accepted |

## Not yet verified or implemented

- {{MISSING_OR_SCAFFOLDED_ITEM}}

## Current contracts and data baseline

- Schema/migration version: {{SCHEMA_VERSION}}
- Authoritative fact source: {{FACT_SOURCE}}
- Stable interfaces: {{INTERFACES}}
- Active compatibility constraints: {{COMPATIBILITY}}

| Interface | Authority | Producer | Consumers | Version/hash | Compatibility |
|---|---|---|---|---|---|
| {{INTERFACE}} | `{{AUTHORITY_PATH}}` | {{PRODUCER}} | {{CONSUMERS}} | {{VERSION_OR_HASH}} | {{COMPATIBILITY_RULE}} |

## Validation baseline

| Command | Executed at | Exit/result | Scope |
|---|---|---|---|
| `{{COMMAND}}` | {{TIME}} | {{ACTUAL_RESULT}} | {{SCOPE}} |

## Open risks, defects, and deferred gates

| Item | Severity | Evidence | Required resolution or gate |
|---|---|---|---|
| {{RISK}} | {{SEVERITY}} | {{EVIDENCE}} | {{RESOLUTION}}

## Current implementation boundary

- Allowed files/scopes: {{ALLOWED_SCOPE}}
- Read-only references: {{READ_ONLY_SCOPE}}
- Forbidden files/scopes: {{FORBIDDEN_SCOPE}}
- Allowed external effects: {{ALLOWED_EFFECTS}}
- Effects blocked in tests: {{BLOCKED_EFFECTS}}

## Next-step entry gate

- {{VERIFIABLE_ENTRY_CONDITION}}

## Evidence integrity

- Do not infer completion from file existence, a previous model summary, or a stale report.
- Re-run the named baseline when code, dependencies, migrations, tests, or acceptance claims change.
- Keep behavioral guarantees in executable code and tests; link them here.
