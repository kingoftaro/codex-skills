---
name: phase-step-planner
description: Create, resume, reconcile, or advance a repository-backed multi-stage phase that requires persistent STATUS/STEP artifacts and independent acceptance. Do not use merely because a task is large, a code review is requested, or unrelated phase files exist.
---

# Phase Step Planner

Coordinate multi-stage engineering work through one authoritative phase state,
bounded steps, independent acceptance, and executable handoffs. This skill owns
execution structure, not implementation, requirements, or architecture
decisions.

## Entry gate

Use this skill only to create, resume, reconcile, accept, or advance a
repository-backed phase whose multiple outcomes require persistent STATUS/STEP
state and independent acceptance. A large task, review request, risk label, or
the presence of phase-like files alone does not establish applicability.

Handle ordinary exploration and trivial edits directly; use
`deliver-code-change` for one bounded implementation outcome. Create phase
process only while persistent coordination reduces execution risk.

## Planning boundary

Define the phase objective, scope, dependency-aware outcomes, risks, validation,
and acceptance gates without inventing requirements or architecture. When a
material decision remains unresolved, stop with the decision, viable options
and tradeoffs, affected contracts, and smallest safe temporary boundary.

Each STEP has one outcome, bounded scope, acceptance evidence, and stop
conditions. Keep one authoritative STATUS and exactly one detailed current
STEP. Create phase artifacts only when the entry gate passes, using bundled
templates only when no repository convention exists.

## Execution cycle

1. Inspect current code, Git, tests, migrations, configuration, contracts, and
   raw evidence.
2. Reconcile observed repository state with intended behavior.
3. Define phase scope and dependency-aware bounded outcomes.
4. Prepare and validate exactly one current executable STEP.
5. Hand it to `deliver-code-change`.
6. Independently inspect the returned diff and verification evidence; accept or
   reject it.
7. Update phase state and prepare a successor only from the newly verified
   state.

## Repair-loop Circuit Breaker

Only a `CONFIRMED` or `STRONG`, material, `repair-introduced`, non-duplicate
finding under the same current STEP and invariant counts. `TENTATIVE`, P3,
pre-existing, style-only, and ordinary documentation findings do not.

Do not create successor repair STEP files for repeated symptoms under one
governing invariant. Symptom count does not determine STEP count. On the first
qualifying regression, or whenever STATUS records a non-`inactive` `Repair
loop`, read
[references/repair-loop.md](references/repair-loop.md) before advancing the
phase or revising its current STEP.

After two consecutive qualifying regressions, set the handoff `BLOCKED` and
reconcile root cause before further implementation. Split only when independent
acceptance or rollback boundaries are proven.

## Evidence and phase state

Code, Git, tests, migrations, configuration, raw output, and validation establish
observed state; accepted requirements and contracts establish intended
behavior. Chat, assumptions, and generated plans are not evidence. Record
conflicts explicitly: use `STALE` for evidence-backed artifact synchronization,
`BLOCKED` for a material implementation, contract, authority, or evidence
conflict, and `PASS` only when executable. Acceptance requires satisfied
criteria, current validation evidence, and documented remaining risks.

## Executable handoff

Before a validator, checkpoint, or hash comparison, confirm that the request
implements, resumes, accepts, or advances one identified non-terminal phase;
its STATUS and current STEP govern the requested outcome; and the requested
files and effects fit that STEP. Phase-like files alone do not establish
applicability. Without phase authority, use the ordinary workflow; with phase
authority but a boundary conflict, reconcile instead of falling back.

An applicable handoff is executable only when:

1. `STATUS.md` names exactly one current `STEP_*.md` and the phase is not
   terminal.
2. STATUS and STEP name the same supported handoff schema.
3. Semantic review and the authoritative validator are `PASS`, with no material
   repository, contract, or evidence contradiction.
4. The STEP checkpoint matches its bytes and its path stays inside the phase
   directory.
5. The STEP defines one outcome, non-goals, file and side-effect boundaries,
   acceptance evidence, and stop conditions.

The validator named by repository instructions is authoritative; never bypass
its failure with the bundled validator, a manual digest, inferred
compatibility, or silent repair. If no repository validator exists, resolve
`<python>` and `<skill-root>` to explicit paths and run:

```text
<python> <skill-root>/scripts/validate_phase_artifacts.py <phase-directory>
```

Bundled validation uses schema `1`; a repository may declare a stricter schema.
Do not infer cross-version compatibility. Bundled `PASS` proves only structural
and internal consistency, not live state, semantics, independence, or authority.

A checkpoint mismatch is always non-executable, but it is not automatically
`BLOCKED`. Treat an expected, attributable STEP text edit after review as
`STALE` until semantic review is repeated and a new checkpoint is recorded.
Treat unexplained drift or a material contract, boundary, authority, or evidence
conflict as `BLOCKED`. Never refresh the hash alone or silently repair STATUS.

Give the executor only applicable repository instructions, STATUS, the current
STEP, and named read-only references. Handoff `PASS` grants no extra authority.

## Validation and role separation

Match validation depth to risk and never promote blocked or inferred evidence
to `PASS`. The planner owns boundaries, handoff validation, and independent
acceptance. The executor implements and verifies only the current STEP; it
cannot redefine scope or acceptance, approve itself, or define a successor.
The planner does not implement while acting as planner.

## Resources and final rule

Load or use only what the current condition requires:

- `assets/PHASE_README_TEMPLATE.md`, `assets/STATUS_TEMPLATE.md`, and
  `assets/STEP_TEMPLATE.md` when new artifacts are justified and no repository
  convention exists;
- `references/FAILURE_PATTERNS.md` when a matching failure appears, converting
  the relevant pattern into a concrete guard, test, or stop condition;
- `references/repair-loop.md` on the first qualifying repair regression or
  whenever STATUS records a
  non-`inactive` `Repair loop`;
- `scripts/validate_phase_artifacts.py` before handing off, resuming, accepting,
  or advancing an applicable bundled-contract phase;
- `scripts/validate_handoff_contract.py` after changing bundled templates,
  validator, or executor handoff contract.

Keep project architecture, paths, commands, thresholds, and stricter schemas in
repository instructions or phase artifacts, not this skill.

Prefer fewer bounded steps, evidence over assumptions, and execution over
documentation. Use process only while it reduces risk.
