# {{STEP_ID}}: {{STEP_NAME}}

> Non-executable draft: defer review, checkpoint, and validation until handoff.

## One outcome

{{SINGLE_VERIFIABLE_OUTCOME}}

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

Add read-only or forbidden rows only when useful. Stop before changing a file
outside this boundary.

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

Do not describe absent mechanisms or risks.

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
