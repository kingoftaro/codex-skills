# Phase Handoff Execution

Use this mode only when a phase planner has produced an applicable `STATUS.md` and current `STEP_*.md` for the requested change.

## Validate the handoff

1. Read applicable user instructions and `AGENTS.md` files first.
2. Accept handoff schema `1` or `2`; stop on any other version. Schema 2 is the preferred low-duplication format. It stores machine facts once in the `phase-handoff` JSON block in `STATUS.md`; the STEP does not repeat them. Schema 1 is deprecated, receives compatibility fixes only, and will be removed in the first breaking release on or after 2026-12-01.
3. Confirm that `STATUS.md` identifies exactly one current executable STEP, records a `PASS` consistency result, and is not terminal. `STALE` and `BLOCKED` are not executable. Phase states `development complete` and `accepted` are not executable; `release blocked` is executable only when STATUS intentionally identifies a remediation STEP.
4. Verify that the STEP path is relative, exists inside the phase directory, and matches the detailed step in the phase index when present.
5. Use `phase-step-planner/scripts/validate_phase_artifacts.py <phase-dir>` when available. It verifies the contract-registry and STEP digests, rejects unknown contract IDs and unresolved bundled template placeholders, and, for schema 2 Git mode, compares the recorded HEAD and worktree fingerprint with live Git. Never run `--prepare` as the executor; preparation mutates and rebinds the handoff and belongs to the planner.
6. For schema 2 manual repository mode, independently compare its immutable checkpoint with repository reality. For schema 1, confirm that STATUS and STEP record the same schema/migration baseline and reviewed repository/worktree checkpoint, then independently inspect live Git.
7. Trace every ID in `Contract references and delta` to its authoritative phase entry and code or schema symbol. Stop when an authority is absent, a consumer contradicts the recorded delta, the live repository differs from the reviewed state, or the requested work exceeds the STEP.

Do not silently repair phase artifacts while acting as the implementation executor.

## Execute one step

- For schema 2, treat Outcome, Contract references and delta, File boundary, Risk controls, Acceptance, and Stop conditions as binding after higher-priority instructions. For schema 1, retain its named binding sections.
- Rehearse the exact file touches, authoritative definitions and consumers, acceptance evidence, and stop conditions before editing. Extend the rehearsal only for active risk packs.
- Select Fast, Standard, or High-risk within that boundary. Risk may increase verification depth but does not authorize broader scope.
- Modify only allowed files. Read-only and forbidden scopes remain unchanged unless the user or phase planner explicitly revises the STEP.
- Apply only the packs named under Risk controls. If a newly discovered trigger would change the approved boundary or acceptance gate, stop and return it to the planner.
- Block every external effect that the STEP or default risk policy forbids in automated tests.
- Stop when a missing interface, migration, dependency, or side effect requires work assigned to a later step.

## Return evidence

Report:

1. outcome and changed files;
2. exact commands, exit results, and relevant observations;
3. normal, failure, adversarial, rollback, and degraded evidence required by the STEP;
4. confirmation that file and side-effect boundaries were respected;
5. deviations, contradictions, blocked checks, and remaining risks.

Do not mark the STEP accepted, update `STATUS.md`, write an acceptance report, or detail the next step. The phase planner performs acceptance from repository evidence.
