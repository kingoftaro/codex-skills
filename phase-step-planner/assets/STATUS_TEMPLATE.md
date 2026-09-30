# Phase {{PHASE_ID}} current status

> This is the phase's single authoritative snapshot. Update it from repository evidence during readiness, reconciliation, and acceptance; do not use it as a speculative plan.

## Snapshot identity

- Updated at: {{TIMESTAMP_WITH_TIMEZONE}}
- Repository root: `{{REPOSITORY_ROOT}}`
- Branch: `{{BRANCH}}`
- Verified Git checkpoint: `{{COMMIT_OR_UNCOMMITTED_EXPLANATION}}`
- Worktree state: {{CLEAN_OR_SUMMARY}}

## Artifact binding

- Handoff schema: 1
- Review result: PASS / STALE / BLOCKED / NOT_APPLICABLE
- Repair loop: `{"state":"inactive","invariant_id":"none","consecutive_regressions":0,"last_classification":"none","evidence":"none"}`
- Phase index: `README.md`
- Current executable step: `{{CURRENT_STEP_DOCUMENT}}`
- Current step specification checkpoint: `sha256:{{CURRENT_STEP_SHA256}}`
- Audited against repository checkpoint: `{{AUDITED_REPOSITORY_CHECKPOINT}}`

For an active handoff, use `PASS` only after the readiness review required by
the STEP's Fast, Standard, or High-risk route and structural validation. Draft
STEP files remain non-executable, normally `STALE`; ordinary draft revisions do
not require validator or hash cycles. For an `accepted` or `release-ready`
phase with no active step, use `NOT_APPLICABLE` for the review result, `none`
for the current executable step, `not-applicable` for its checkpoint, and leave
no step marked `detailed` in `README.md`.

The STEP checkpoint identifies the reviewed document version. Record it at
handoff and recheck on a new executor or resumed session, relevant artifact
changes, or an explicit repository gate. Expected implementation diffs do not
invalidate the contract. It is not a code-quality, live-Git, or permission check.

The `Repair loop` JSON is the machine-readable snapshot for the current
governing invariant. Use `observing` after the first qualifying regression and
`blocked` after the second; only `CONFIRMED` or `STRONG`, material,
repair-introduced, non-duplicate events under the same STEP and invariant count.
Use `reset` after evidence-backed root-cause review. Terminal phases use
`inactive`; keep detailed history in the risk table.

## Position

- Phase state: not-started / in-progress / development-complete / accepted / release-ready / release-blocked
- Last accepted step: `{{LAST_ACCEPTED_STEP}}`
- Next outlined step: `{{NEXT_STEP}}`

## Verified capabilities

| Capability | Code evidence | Test/evidence | State |
|---|---|---|---|
| {{CAPABILITY}} | `{{PATH_OR_SYMBOL}}` | `{{TEST_OR_REPORT}}` | absent / scaffolded / implemented / tested / accepted |

## Not yet verified or implemented

- {{MISSING_OR_SCAFFOLDED_ITEM}}

## Current contracts and data baseline

- Schema/migration version: {{SCHEMA_VERSION}}
- Authoritative fact source: {{FACT_SOURCE}}
- Stable interfaces: {{INTERFACES}}
- Active compatibility constraints: {{COMPATIBILITY}}

## Validation baseline

| Command | Executed at | Exit/result | Scope |
|---|---|---|---|
| `{{COMMAND}}` | {{TIME}} | {{ACTUAL_RESULT}} | {{SCOPE}} |

## Open risks, defects, and deferred gates

| Item | Severity | Evidence | Required resolution or gate |
|---|---|---|---|
| {{RISK}} | {{SEVERITY}} | {{EVIDENCE}} | {{RESOLUTION}}

## Current handoff

- Authoritative boundary: the File boundary and Side-effect policy sections in `{{CURRENT_STEP_DOCUMENT}}`
- Read-only references supplied to the implementation model: {{READ_ONLY_SCOPE}}
- Local overrides or exceptions: {{EXPLICIT_OVERRIDES_OR_NONE}}

## Next-step entry gate

- {{VERIFIABLE_ENTRY_CONDITION}}

## Evidence integrity

- Do not infer completion from file existence, a previous model summary, or a stale report.
- Re-run only the named checks whose evidence may be invalidated by a relevant
  code, dependency, migration, test, or acceptance change.
- Classify an expected STEP edit after readiness review as `STALE`. Material
  changes require the selected readiness review again; clearly non-material
  changes require only focused diff confirmation and checkpoint refresh.
  Classify unexplained drift or a material contract, boundary, authority, or
  evidence conflict as `BLOCKED`.
- Bundled validator `FAIL` means structural errors; `STALE` means pending
  synchronization; `BLOCKED` means a recorded conflict. All are non-executable.
  A mismatch alone does not establish drift origin or authorize hash refresh.
- Keep behavioral guarantees in executable code and tests; link them here.
