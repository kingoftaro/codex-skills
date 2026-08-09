---
name: phase-step-planner
description: Audit and split a large software phase into bounded, independently verifiable implementation steps with a single evidence-backed status snapshot and safe handoff prompts. Use when planning a multi-stage phase, when a phase is too large for one model context, when work will be handed to a lower-capability model, when creating or updating phase README/STEP/STATUS Markdown files, or before continuing a partially implemented phase after another model or session.

---

# Phase Step Planner

Turn a large phase into repository-backed, evidence-driven handoffs. Never rely on chat history or a model's completion claim as the current project state.

## Choose the operating mode

1. **Plan a new phase**: inspect the project rules and accepted predecessor state, create the dependency map, and detail only the first executable step.
2. **Resume an existing phase**: audit code, migrations, tests, Git state, and retained evidence before writing status or steps.
3. **Phase still being edited elsewhere**: do not audit mutable files, generate status, or rewrite the phase. Limit work to stable global templates and wait for an explicit handoff.
4. **Accept a completed step**: verify evidence first, then update the single phase status file and detail the next step.

## Establish authority and boundaries

- Read all applicable `AGENTS.md` files before acting.
- Locate the repository root and inspect `git status`, including untracked files. Preserve unrelated or concurrent changes.
- Identify the authoritative phase plan, predecessor acceptance evidence, current schema or migration version, stable interfaces, and validation commands.
- Separate phase-wide design from executable step specifications.
- Keep one `STATUS.md` per phase. Do not create competing status files or treat an acceptance report as live status.
- Do not modify a phase that another model or process is still generating. Record the deferment outside its mutable files if needed.

## Audit before decomposing

For an existing phase, derive status from the repository rather than the plan:

1. Map each planned capability to concrete code, data, tests, and evidence.
2. Distinguish absent, scaffolded, implemented, tested, accepted, and release-ready states.
3. Run only safe, relevant baseline checks unless the user requests full acceptance.
4. Treat uncommitted and untracked work as unfinished unless evidence proves otherwise.
5. Record contradictions, missing tests, external side effects, stale reports, and unresolved risks.

Do not mark a step complete merely because its files exist or tests are green. Check whether the required failure paths and side-effect boundaries are covered.

## Control repeated repair loops

For every review finding, classify it as a latent defect, a repair-introduced regression, or an environment/evidence contradiction. Record the failing reproduction, governing invariant, regression guard, affected artifacts, and closure evidence in the phase's existing issue table or STATUS; do not create a second status file.

Before closing a fix, verify the changed path and its adjacent contract: default input, caller override, missing or invalid input, failure cleanup, and preserved compatibility. Mark an item closed only when the original reproduction fails before the fix, passes after it, and the relevant adjacent paths pass.

If the same step produces a new P1/P2 repair regression in two consecutive review rounds, freeze acceptance-document edits, stop adding patches, perform a root-cause review, and split the step by independently accepted outcome before resuming implementation.

Keep the evidence order strict: implementation, focused regression, adjacent-path checks, relevant full gates, raw evidence, acceptance report, then STATUS. Never write a passing claim from an intended result or from evidence produced before the latest behavior change. Run a repository evidence-consistency checker when one exists.

## Split the phase

Create steps that each have one outcome, one primary risk boundary, and an independent acceptance gate. Split again when a step:

- crosses more than two or three architectural layers;
- combines contract design, multiple adapters, UI integration, performance work, and reporting;
- requires broad file ownership or cannot be safely reverted as one checkpoint;
- cannot be described and accepted without relying on future steps.

Prefer this order when applicable: freeze contracts and failure examples, domain logic, repository or adapter, application orchestration, minimal wiring, CLI or UI, adversarial tests, performance, acceptance report.

Generate a dependency-aware outline for the whole phase, but fully specify only the current step and optionally the immediately following step. Re-detail later steps after preceding interfaces are accepted.

## Generate repository artifacts

Use the assets as output templates:

- Copy and adapt `assets/PHASE_README_TEMPLATE.md` for the phase index and dependency map.
- Copy and adapt `assets/STATUS_TEMPLATE.md` for the phase's single verified snapshot.
- Copy and adapt `assets/STEP_TEMPLATE.md` for each executable step.

Keep project-specific paths, commands, architecture, and acceptance thresholds in the project artifacts, not in this Skill.

When the failure resembles hidden shared state, test-order dependence, accidental OS actions, stale plans, or false-green acceptance, read `references/FAILURE_PATTERNS.md` and incorporate the relevant guardrails without copying the incident narrative into every step.

## Prepare an implementation handoff

Give the implementation model only:

1. applicable `AGENTS.md` files;
2. the phase `STATUS.md`;
3. the current `STEP_*.md`;
4. explicitly named read-only references.

Require a pre-code rehearsal that lists file touchpoints, traces the call chain to every external effect, identifies factories and shared mutable state, explains test isolation, names likely mistakes and their detecting tests, and states where to stop if reality differs from the step.

Never authorize the model to complete the whole phase, update a passing report before evidence exists, or silently expand the allowed file scope.

## Accept and advance

After implementation:

1. inspect the diff and untracked files;
2. run targeted validation and the relevant regression set;
3. run adjacent-path checks for changed defaults, overrides, invalid inputs, cleanup, and compatibility;
4. verify that no forbidden external effect occurred;
5. review contracts, migrations, privacy, rollback, and failure behavior in proportion to risk;
6. run the repository's evidence-consistency checker when available;
7. update acceptance documents and `STATUS.md` with actual commands, results, risks, file scope, and Git checkpoint only after verification;
8. detail the next step from the new repository state.

Keep executable guarantees in code, database constraints, tests, and validation scripts. Markdown records the contract and evidence; it does not enforce behavior by itself.
