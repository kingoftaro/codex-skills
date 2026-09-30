# {{STEP_ID}}: {{STEP_NAME}}

> Draft until readiness review and handoff validation; STATUS records executability.

## One outcome

{{SINGLE_VERIFIABLE_OUTCOME}}

Describe one complete behavior, including necessary implementation, consumers,
and tests. Split only for independent acceptance, material risk, or rollback.

- Acceptance signal: {{EXACT_ACCEPTANCE_SIGNAL}}

## Non-goals

- {{EXPLICITLY_EXCLUDED_WORK}}

## Entry conditions and verified baseline

- Handoff schema: 1
- Review route: {{FAST_STANDARD_OR_HIGH_RISK}}
- Required predecessor: {{PREDECESSOR}}
- Relevant code, interface, schema, or migration baseline: {{RELEVANT_BASELINE}}
- Baseline command and result: `{{BASELINE_COMMAND}}` → {{ACTUAL_RESULT}}
- Git/worktree checkpoint: {{GIT_CHECKPOINT}}

## File boundary

This section is the authoritative implementation boundary. `STATUS.md` must reference this step and must not redefine the boundary.

| Access | Path | Purpose |
|---|---|---|
| {{ADD_OR_MODIFY}} | `{{PATH}}` | {{PURPOSE}} |

For Fast and Standard work, prefer explicit module or directory scopes plus
exclusions. Include directly relevant tests and private helpers in those
scopes; do not require an exhaustive file list unless authority or risk needs
one. Read-only and forbidden rows override a broader allowed scope. Stop
before changing a file outside the boundary; an explicit allowlist stays binding.

## Contracts and invariants

- Governing contract or invariant: {{RELEVANT_CONTRACT_OR_INVARIANT}}
- Relevant interface, fact source, or state transition: {{RELEVANT_FLOW_OR_NONE}}
- Conditional controls such as concurrency, compatibility, migration, or security: {{APPLICABLE_CONTROLS_OR_NONE}}
- Executable guard: {{TEST_CONSTRAINT_OR_VALIDATOR}}

## Side-effect policy

- External or persistent effects: {{APPLICABLE_EFFECTS_OR_NONE}}
- Test isolation, restoration, or recovery: {{APPLICABLE_CONTROL_OR_NONE}}

Use `none` when no relevant effect exists; do not invent controls.

## Required pre-code rehearsal

- Fast: confirm files, relevant invariant, validation, and stop condition.
- Standard: also confirm affected consumers and material failure paths.
- High-risk: also confirm applicable call chains, effects, isolation, recovery,
  and failure-mode tests.

Keep this check concise and choose the implementation within the approved
boundary. Do not prescribe file-by-file operations or describe absent risks.

## Acceptance

- Core acceptance: {{CORE_ACCEPTANCE_TEST}}
- Applicable consumer, failure, or adversarial checks: {{APPLICABLE_CHECKS_OR_NONE}}

### Validation commands

Run from `{{WORKDIR}}`:

```text
{{EXACT_COMMANDS}}
```

Record actual exit codes and results. Do not copy historical test counts.

## Stop and degrade

- Stop when: {{STOP_CONDITION}}
- Do not: {{FORBIDDEN_SHORTCUT}}
- Degradation, rollback, or recovery when applicable: {{APPLICABLE_RECOVERY_OR_NONE}}

## Deliverables

- {{CODE_OR_MIGRATION}}
- {{TESTS}}
- {{EVIDENCE}}

Do not update the phase status or acceptance report until these deliverables are verified.
