# {{STEP_ID}}: {{STEP_NAME}}

## One outcome

{{SINGLE_VERIFIABLE_OUTCOME}}

- Acceptance signal: {{EXACT_ACCEPTANCE_SIGNAL}}

## Non-goals

- {{EXPLICITLY_EXCLUDED_WORK}}

## Entry conditions and verified baseline

- Required predecessor: {{PREDECESSOR}}
- Current schema/migration: {{SCHEMA_BASELINE}}
- Stable interfaces: {{INTERFACE_BASELINE}}
- Baseline command and result: `{{BASELINE_COMMAND}}` → {{ACTUAL_RESULT}}
- Git/worktree checkpoint: {{GIT_CHECKPOINT}}

## File boundary

This section is the authoritative implementation boundary. `STATUS.md` must reference this step and must not redefine the boundary.

| Access | Path | Purpose |
|---|---|---|
| Add | `{{PATH}}` | {{PURPOSE}} |
| Modify | `{{PATH}}` | {{PURPOSE}} |
| Read only | `{{PATH}}` | {{PURPOSE}} |
| Forbidden | `{{PATH_OR_SCOPE}}` | {{REASON}} |

Stop and report before changing a file outside this boundary.

## Contracts and invariants

- Interface/data contract: {{EXACT_CONTRACT}}
- Fact source and state transition: {{BEFORE_OPERATION_AFTER}}
- Transaction/CAS/version rule: {{CONCURRENCY_RULE}}
- Compatibility rule: {{COMPATIBILITY_RULE}}
- Executable guard: {{TEST_CONSTRAINT_OR_VALIDATOR}}

## Side-effect policy

- Explicitly allowed: {{ALLOWED_EFFECTS}}
- Must be blocked in automated tests: {{BLOCKED_EFFECTS}}
- Required fakes/patch targets: {{FAKES_AND_IMPORT_PATHS}}
- Shared state restoration: {{REGISTRY_SINGLETON_CACHE_FIXTURE}}

## Implementation order

1. {{SMALLEST_SAFE_CHANGE}}
2. {{NEXT_CHANGE}}
3. {{MINIMAL_WIRING}}
4. {{TESTS_BEFORE_REPORTS}}

## Required pre-code rehearsal

Before editing, report:

1. exact files to change and why they are sufficient;
2. entry-to-side-effect call chain;
3. factories, fixtures, registries, singletons, caches, and environment writes involved;
4. how each external effect is blocked in tests;
5. three likely mistakes and the test that catches each;
6. the exact condition at which implementation stops.

## Acceptance

### Normal cases

- {{NORMAL_TEST}}

### Failure and adversarial cases

- {{FAILURE_TEST}}
- {{CONCURRENCY_OR_SIDE_EFFECT_TEST}}

### Validation commands

Run from `{{WORKDIR}}`:

```text
{{EXACT_COMMANDS}}
```

Record actual exit codes and results. Do not copy historical test counts.

## Stop and degrade

- Stop when: {{STOP_CONDITION}}
- Acceptable degradation: {{DEGRADED_PATH}}
- Do not: {{FORBIDDEN_SHORTCUT}}
- Rollback or recovery: {{ROLLBACK_OR_RECOVERY}}

## Deliverables

- {{CODE_OR_MIGRATION}}
- {{TESTS}}
- {{EVIDENCE}}

Do not update the phase status or acceptance report until these deliverables are verified.
