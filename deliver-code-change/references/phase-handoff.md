# Phase Handoff Execution

Use this mode only when a phase planner has produced an applicable `STATUS.md` and current `STEP_*.md` for the requested change.

## Validate the handoff

1. Read applicable user instructions and `AGENTS.md` files first.
2. Require handoff schema version `1` in both `STATUS.md` and the current STEP. Stop on an unsupported or mixed version.
3. Confirm that `STATUS.md` identifies exactly one current executable STEP, records a `PASS` consistency result, and is not terminal. `STALE` and `BLOCKED` are not executable.
4. Verify that the STEP path is relative, exists inside the phase directory, and matches the detailed step in the phase index when present.
5. Verify the recorded `sha256:` checkpoint against the STEP's current bytes. Use `phase-step-planner/scripts/validate_phase_artifacts.py <phase-dir>` when that Skill is available; otherwise compute the digest with an existing local tool.
6. Confirm that STATUS and STEP record the same schema/migration baseline and reviewed repository/worktree checkpoint.
7. Stop before editing when validation fails, the worktree contradicts the recorded checkpoint, or the requested work exceeds the STEP.

Do not silently repair phase artifacts while acting as the implementation executor.

## Execute one step

- Treat the STEP's One outcome, Non-goals, File boundary, Contracts and invariants, Side-effect policy, Acceptance, and Stop and degrade sections as binding after higher-priority instructions.
- Perform the STEP's pre-code rehearsal before editing.
- Select Fast, Standard, or High-risk within that boundary. Risk may increase verification depth but does not authorize broader scope.
- Modify only allowed files. Read-only and forbidden scopes remain unchanged unless the user or phase planner explicitly revises the STEP.
- Block every external effect that the STEP forbids in automated tests.
- Stop when a missing interface, migration, dependency, or side effect requires work assigned to a later step.

## Return evidence

Report:

1. outcome and changed files;
2. exact commands, exit results, and relevant observations;
3. normal, failure, adversarial, rollback, and degraded evidence required by the STEP;
4. confirmation that file and side-effect boundaries were respected;
5. deviations, contradictions, blocked checks, and remaining risks.

Do not mark the STEP accepted, update `STATUS.md`, write an acceptance report, or detail the next step. The phase planner performs acceptance from repository evidence.
