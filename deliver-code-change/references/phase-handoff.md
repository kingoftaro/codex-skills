# Phase Handoff Execution

Use this mode only when a phase planner has produced an applicable `STATUS.md` and current `STEP_*.md` for the requested change.

## Validate the handoff

1. Read applicable user instructions and `AGENTS.md` files first.
2. Determine the authoritative validator. If repository instructions name one, run it and do not bypass its failure with another validator, a manual digest, inferred compatibility, or silent artifact repair.
3. Otherwise, use the adjacent bundled validator. Resolve `<python>` and
   `<planner-skill-root>` to explicit paths rather than assuming a working
   directory:

   ```text
   <python> <planner-skill-root>/scripts/validate_phase_artifacts.py <phase-dir>
   ```

   If neither an authoritative repository validator nor the bundled validator is available, report `BLOCKED` and stop before editing.
4. Confirm that STATUS identifies exactly one current executable STEP, the phase is not terminal, and its `Review result` is `PASS`. `STALE` and `BLOCKED` are not executable.
5. Confirm that STATUS and STEP declare the same supported `Handoff schema`. The bundled templates and validator use schema `1`; a repository may declare a stricter version through its own validator.
6. Verify that the STEP path is relative, remains inside the phase directory, and matches the detailed step in the phase index when present.
7. Verify that the recorded `sha256:` checkpoint matches the STEP's current bytes and that repository state does not contradict the reviewed baseline.
8. Confirm that the STATUS `Repair loop` snapshot is structurally valid and is
   not `blocked`; the authoritative validator performs this check when it
   supports the bundled contract.
9. Stop before editing when validation fails, a material contradiction remains, or the requested work exceeds the STEP.

Do not silently repair phase artifacts while acting as the implementation executor.

## Execute one step

- Treat the STEP's One outcome, Non-goals, File boundary, Contracts and invariants, Side-effect policy, Acceptance, and Stop and degrade sections as binding after higher-priority instructions.
- Perform the STEP's pre-code rehearsal before editing.
- Select Fast, Standard, or High-risk within that boundary. Risk may increase verification depth but does not authorize broader scope.
- Modify only allowed files. Read-only and forbidden scopes remain unchanged unless the user or phase planner explicitly revises the STEP.
- Block every external effect that the STEP forbids in automated tests.
- Stop when a missing interface, migration, dependency, or side effect requires work assigned to a later step.
- Classify a follow-on failure as latent, repair-introduced, or an
  environment/evidence contradiction. Do not turn it into an unapproved patch
  or a new STEP.
- If STATUS records an active repair-loop circuit breaker, or a second
  consecutive review round produces another material repair-introduced
  regression for the same STEP, stop without another patch. Return the failing
  reproduction, governing invariant, suspected fault locus, affected adjacent
  paths, and current evidence to the planner.

## Return evidence

Report:

1. outcome and changed files;
2. exact commands, exit results, and relevant observations;
3. normal, failure, adversarial, rollback, and degraded evidence required by the STEP;
4. confirmation that file and side-effect boundaries were respected;
5. deviations, contradictions, blocked checks, and remaining risks.

Do not mark the STEP accepted, update `STATUS.md`, write an acceptance report, or detail the next step. The phase planner performs acceptance from repository evidence.
