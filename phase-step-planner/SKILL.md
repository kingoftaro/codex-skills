---
name: phase-step-planner
description: Audit and coordinate multi-stage engineering work that needs persistent phase state, independent acceptance gates, or cross-session handoffs. Do not use for one bounded change, trivial edits, or ordinary exploration.
---

# Phase Step Planner

Coordinate multi-stage engineering work through one authoritative phase state,
bounded steps, independent acceptance, and executable handoffs. This skill owns
execution structure, not implementation, requirements, or architecture
decisions.

## Entry gate

Use this skill when work has multiple independent implementation outcomes,
needs cross-session or developer/agent handoff state, requires milestone
acceptance, or resumes, reconciles, accepts, or advances an existing phase.

Do not create phase process for ordinary exploration or work that lacks
persistent coordination:

- handle a trivial local low-risk edit directly;
- use `deliver-code-change` for one bounded implementation outcome;
- use lightweight investigation for exploration.

Use process only when it reduces execution risk.

## Planning boundary

The planner may define the phase objective, scope, outcomes, risks, validation
strategy, dependency-aware steps, and acceptance gates. It must not invent
product requirements, choose technologies, introduce system boundaries, or
make unresolved architecture decisions.

When designs need comparison, use the established architecture review. If none
exists, stop with the required decision, viable options and tradeoffs, affected
contracts, and smallest safe temporary boundary.

A phase excludes unrelated future ideas and speculative implementation detail.
Each step has one purpose, bounded scope, affected components, acceptance
criteria, validation method, and known risks. Do not combine unrelated work or
leave completion ambiguous.

Create a Phase README, STATUS, and STEP documents only when phase management is
justified. Keep one authoritative STATUS and exactly one detailed current STEP;
do not add phase artifacts for a bug fix, small feature, isolated refactor,
single-session task, or exploration. Use bundled templates only when the
repository has no authoritative convention.

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

Do not create successor repair STEP files for repeated symptoms under the same
governing invariant. Symptom count does not determine STEP count.

On the first related repair-introduced regression, or whenever STATUS records
a non-`inactive` `Repair loop`, read
[references/repair-loop.md](references/repair-loop.md) before advancing the
phase or revising its current STEP.

After two consecutive material repair-introduced regressions under that
invariant, set the handoff `BLOCKED` and reconcile root cause before further
implementation. Split only when independent acceptance or rollback boundaries
are proven.

## Evidence and phase state

Repository code, Git state, tests, migrations, configuration, raw command
output, and validation results establish observed state. Accepted requirements,
architecture, and contracts establish intended behavior. Chat, prior model
output, assumptions, and generated plans are not evidence.

When observed and intended sources disagree, record them separately with the
material contradiction and affected scope. Keep a handoff `STALE` when
artifacts need evidence-backed synchronization, and `BLOCKED` when an
implementation, contract, authority, or evidence conflict needs resolution.
Only `PASS` is executable.

An implementation is not complete merely because code exists. Acceptance
requires implementation, satisfied criteria, validation evidence, and
documented remaining risks.

## Executable handoff

A handoff is executable only when:

1. `STATUS.md` names exactly one current `STEP_*.md` and the phase is not
   terminal.
2. STATUS and STEP name the same supported handoff schema.
3. Semantic review is `PASS`; `STALE` and `BLOCKED` are not executable.
4. The STEP checkpoint matches its bytes and its path stays inside the phase
   directory.
5. The STEP defines one outcome, non-goals, file and side-effect boundaries,
   acceptance evidence, and stop conditions.
6. No material repository, contract, or evidence contradiction remains.
7. The authoritative handoff validator returns `PASS`.

The validator named by repository instructions is authoritative; never bypass
its failure with the bundled validator, a manual digest, inferred
compatibility, or silent repair. If no repository validator exists, resolve
`<python>` and `<skill-root>` to explicit paths and run:

```text
<python> <skill-root>/scripts/validate_phase_artifacts.py <phase-directory>
```

Bundled templates and validation use handoff schema `1`. A repository may
declare a stricter schema; do not infer cross-version compatibility. A bundled
`PASS` proves only structural and internal consistency, not live Git state,
semantic correctness, reviewer independence, or authorization.

Give the executor only applicable repository instructions, STATUS, the current
STEP, and explicitly named read-only references. A handoff `PASS` never grants
permission to commit, push, deploy, apply a migration, delete, or create an
external side effect.

## Validation and role separation

Match validation to risk: focused checks for low risk, module/integration checks
for medium risk, and regression, migration, and recovery evidence for high
risk. Do not impose heavyweight validation on a trivial step, and never promote
blocked or inferred evidence to `PASS`.

The planner defines phase boundaries, prepares and validates the handoff, and
accepts or rejects completed steps from repository evidence. The executor
implements and verifies only the current STEP; it must not redefine phase
scope, change acceptance, or approve itself. The planner must not implement the
current STEP while acting as planner.

## Resources and final rule

Load or use only what the current condition requires:

- `assets/PHASE_README_TEMPLATE.md`, `assets/STATUS_TEMPLATE.md`, and
  `assets/STEP_TEMPLATE.md` when new artifacts are justified and no repository
  convention exists;
- `references/FAILURE_PATTERNS.md` when a matching failure appears, converting
  the relevant pattern into a concrete guard, test, or stop condition;
- `references/repair-loop.md` on the first related repair-introduced regression
  or whenever STATUS records a non-`inactive` `Repair loop`;
- `scripts/validate_phase_artifacts.py` before handing off or advancing a
  bundled-contract phase;
- `scripts/validate_handoff_contract.py` after changing bundled templates,
  validator, or executor handoff contract.

Keep project architecture, paths, commands, thresholds, and stricter schemas in
repository instructions or phase artifacts, not this skill.

Prefer fewer bounded steps, evidence over assumptions, and execution over
documentation. Use process only while it reduces risk.
