---
name: phase-step-planner
description: Audit and split a large software phase into bounded, independently verifiable implementation steps with a single evidence-backed status snapshot and safe handoff prompts. Use when planning a multi-stage phase, reviewing or re-reviewing a completed phase step, when a phase is too large for one model context, when work will be handed to a lower-capability model, when creating or updating phase README/STEP/STATUS Markdown files, or before continuing a partially implemented phase after another model or session.
---

# Phase Step Planner

Turn a large phase into repository-backed, evidence-driven handoffs. Never rely on chat history or a model's completion claim as the current project state.

## Apply the phase entry gate

Use this Skill only when work has multiple independently accepted outcomes, must
survive a session or model handoff, or requires reconciliation of an existing
phase. Route a single bounded change directly to `deliver-code-change`; do not
create phase artifacts for it. The phase workflow is intentionally stricter,
but its documentation depth must still be proportional to active risk.

## Choose the operating mode

1. **Plan a new phase**: inspect the project rules and accepted predecessor state, create the dependency map, and detail only the first executable step.
2. **Resume an existing phase**: audit code, migrations, tests, Git state, and retained evidence before writing status or steps.
3. **Phase still being edited elsewhere**: do not audit mutable files, generate status, or rewrite the phase. Limit work to stable global templates and wait for an explicit handoff.
4. **Accept a completed step**: verify evidence first, inspect document, code, and Git synchronization, report any pending closure work, then advance only from a consistent state.

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

Immediately before creating, detailing, or materially rewriting an executable STEP, read `references/CONSISTENCY_REVIEW.md` and apply its `PASS`, `STALE`, and `BLOCKED` gate. Read `references/FAILURE_PATTERNS.md` only for patterns relevant to the current phase or review finding, activate only the triggered risk packs defined there, and record their names in the STEP.

For every review finding, classify it as a latent defect, a repair-introduced regression, or an environment/evidence contradiction. Record the failing reproduction, governing invariant, regression guard, affected artifacts, and closure evidence in the phase's existing issue table or STATUS; do not create a second status file.

Before closing a fix, apply the `adjacent-paths` risk pack when its trigger is present. Mark an item closed only when the original reproduction fails before the fix, passes after it, and the affected neighboring paths pass.

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

- Copy and adapt `assets/PHASE_README_TEMPLATE.md` for the dependency map and the single registry of stable constraints, interfaces, data baselines, boundaries, and compatibility rules. Give each entry a stable ID and point to its authoritative code, schema, decision, or executable guard.
- Copy and adapt `assets/STATUS_TEMPLATE.md` for the phase's single machine-readable snapshot. Keep phase state, current STEP, review result, digest, and repository checkpoint there; do not copy stable contracts or STEP boundaries into STATUS.
- Copy and adapt `assets/STEP_TEMPLATE.md` for each executable step. Reference registry IDs and state only this step's delta, file boundary, active risk packs, acceptance, and stop conditions.

Keep project-specific paths, commands, architecture, and acceptance thresholds in the project artifacts, not in this Skill.

The bundled templates use handoff schema 2. Schema 1 is deprecated as of
2026-08-17 and receives compatibility fixes only; no schema 1 templates are
distributed and new handoffs must use schema 2. CLI validation emits a
deprecation warning. Support will be removed in the first breaking release on
or after 2026-12-01.

Delete unused table rows instead of filling them with `N/A`. Never repeat a
fact merely so that two Markdown files can agree; store intent once and let the
validator bind generated repository facts.

Migrate a schema 1 handoff by rebuilding STATUS and the current STEP from the
schema 2 templates, consolidating stable contracts in the phase registry, and
rerunning the semantic review before preparation. Do not mechanically preserve
legacy review facts or checkpoints that have not been compared with the live
repository.

Schema 2 STEP headings, backticked contract-ID rows or ID bullets, and the
`- Active packs:` line form a restricted Markdown protocol. Preserve their
template labels and keep live machine metadata outside fenced examples. The
validator ignores headings and metadata-like lines inside backtick or tilde
fences.

When the failure resembles hidden shared state, test-order dependence, accidental OS actions, stale plans, or false-green acceptance, incorporate the relevant guardrails from `references/FAILURE_PATTERNS.md` and activate the matching risk pack without copying the incident narrative into every step.

## Prepare an implementation handoff

Give the implementation model only:

1. applicable `AGENTS.md` files;
2. the phase `STATUS.md`;
3. the current `STEP_*.md`;
4. the phase contract registry named by STATUS;
5. explicitly named read-only references.

Include `references/FAILURE_PATTERNS.md` among those references when the STEP
names an active pack; omit it when the STEP records `none`.

Require a proportional pre-code rehearsal that confirms exact file touchpoints,
authoritative definitions and consumers, acceptance evidence, and the stop point.
Extend it only with the items required by active risk packs.

Never authorize the model to complete the whole phase, update a passing report before evidence exists, or silently expand the allowed file scope.

For a schema 2 Git handoff, finish the semantic consistency review and set its
result in `STATUS.md`. First preflight the complete candidate without writing:

```text
python scripts/validate_phase_artifacts.py --prepare <PHASE_DIRECTORY> --dry-run
```

Then prepare the handoff:

```text
python scripts/validate_phase_artifacts.py --prepare <PHASE_DIRECTORY>
```

Preparation verifies that every STEP contract ID exists in the phase registry,
computes registry and STEP digests, then records HEAD and a worktree fingerprint.
It excludes STATUS and the separately digested STEP from that fingerprint,
validates the candidate in memory, atomically writes generated facts once in
the STATUS JSON block, and immediately validates them against live Git. A final
validation failure restores the original STATUS when no concurrent edit has
intervened. A later validation run is read-only and rejects drift.
For a non-Git repository, use manual checkpoint mode and compare its immutable
checkpoint separately. Never use manual mode merely to bypass an available Git
failure.

The validator rejects incomplete core STEP structure, non-executable phase
states, a non-PASS review, unknown contract IDs, unresolved bundled template
placeholders, registry or STEP digest drift, path escape, and repository drift.
Schema 1 validation remains available
for existing handoffs but cannot perform the schema 2 live Git check. Do not
hand off a STEP when validation fails. After changing the bundled handoff
schema, templates, validator, or executor contract, run
`scripts/validate_handoff_contract.py`; when `deliver-code-change` is installed
adjacent to this Skill, that command also validates the cross-Skill contract.

## Accept and advance

After implementation:

1. inspect the diff and untracked files;
2. run the STEP acceptance gate and the checks required by its active risk packs;
3. verify that no forbidden external effect occurred and run the repository's evidence-consistency checker when available;
4. compare affected phase contracts, STEP, acceptance evidence, open items, and STATUS with final code and evidence, then inspect Git state again;
5. if anything is not synchronized, report the exact stale or pending item, its effect, and the smallest recommended update or commit action;
6. update documents or create a commit only with existing authority, rerun affected checks, prepare the next handoff snapshot, and detail the successor only from mutually consistent inputs.

`PASS` describes the review evidence; it does not silently grant authority to edit, commit, or push. Do not stage unrelated user changes. A dirty but internally consistent worktree may retain `PASS` when reported exactly. If the closure check reveals facts that contradict the review, change the handoff to `STALE` or `BLOCKED`; do not leave an executable `PASS` in place while only warning the user.

Keep executable guarantees in code, database constraints, tests, and validation scripts. Markdown records the contract and evidence; it does not enforce behavior by itself.
