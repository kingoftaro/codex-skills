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

Define objective, scope, dependency-aware outcomes, risks, validation, and
acceptance from evidence; do not invent requirements or architecture. For an
unresolved material decision, report the options, tradeoffs, affected
contracts, and smallest safe boundary, then stop.

Each STEP has one outcome, bounded scope, acceptance evidence, and stop
conditions. Keep one authoritative STATUS and exactly one detailed current
STEP. Create phase artifacts only when the entry gate passes, using bundled
templates only when no repository convention exists.

Treat a STEP as an executable contract, not an exhaustive proof. Include
conditional concerns only when evidence makes them apply.
Group implementation, necessary consumers, and tests into one complete
verifiable outcome. Split for independent acceptance, material risk, or
rollback boundaries, not for individual file edits. Prefer module boundaries
with explicit exclusions for Fast and Standard work; use file allowlists when
the contract or authority requires them.

## Execution cycle

1. Inspect current code, Git, tests, migrations, configuration, contracts, and
   raw evidence.
2. Reconcile observed state and define dependency-aware outcomes.
3. Draft one current STEP and choose its review route.
4. At readiness, perform that review, checkpoint, and validate the handoff.
5. Hand it to `deliver-code-change`.
6. Independently inspect its diff and evidence; accept or reject it.
7. Update phase state and prepare a successor only from accepted evidence.

## STEP readiness review

Do not review every draft. Keep drafts non-executable, normally `STALE`, without
validator or hash cycles. At handoff, choose review depth by material risk:

- **Fast:** localized, obvious, reversible; planner self-check plus structural
  validation, with no independent pre-implementation review.
- **Standard:** cross-file behavior, interfaces, or moderate uncertainty; one
  independent executable-contract review.
- **High-risk:** material changes to trust, money, persistent data,
  shared-state correctness, irreversible effects, or operational failure
  scope; also review applicable failure, recovery, and isolation controls.

Risk overrides diff size. Every route checks the outcome, non-goals, file and
effect boundary, relevant contract or invariant, acceptance signal, and stop
condition. Do not invent controls to fill the template. Independent
post-implementation acceptance remains required.
Assess actual consequences of retries, state machines, concurrency, processes,
and external clients; a mechanism name alone does not select High-risk.

Only a material execution ambiguity or contradiction, a `CONFIRMED` or
`STRONG` P0/P1, or an explicit project gate blocks readiness. P2/P3, wording,
formatting, and speculative hardening do not trigger another round.

Allow one initial review and one focused delta review. Repeat the route only for
changes to outcome, non-goals, boundaries, contracts, invariants, acceptance,
stop/recovery, or reviewed baseline; non-material edits need only diff
confirmation and a new checkpoint. If conflict remains, split, run a bounded
spike, or obtain the missing decision. The planner owns checkpoints.

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

Code, Git, tests, migrations, configuration, and raw output establish observed
state; accepted requirements and contracts establish intent. Chat, assumptions,
and plans are not evidence. Use `STALE` for evidence-backed synchronization,
`BLOCKED` for material implementation, contract, authority, or evidence
conflict, and `PASS` only when executable. Acceptance requires current evidence
and documented remaining risks.
An unmet required acceptance criterion prevents acceptance regardless of the
finding's severity. Unavailable integrations outside the agreed outcome are
reported as limitations, not added as new gates.

## Executable handoff

Before validation or hash comparison, confirm one identified non-terminal phase
governs the request through its STATUS and current STEP, including requested
files and effects. Phase-like files alone do not establish applicability. With
no phase authority, use the ordinary workflow; with authority but a boundary
conflict, reconcile it.

An applicable handoff is executable only when:

1. STATUS names exactly one current `STEP_*.md` in a non-terminal phase.
2. STATUS and STEP use the same supported schema.
3. Route-required readiness review and the authoritative validator are `PASS`,
   with no material repository, contract, or evidence conflict.
4. The checkpoint matches the STEP bytes and its path stays in the phase.
5. Outcome, non-goals, boundaries, relevant invariants, acceptance, and stop
   conditions are executable.

Use the repository-named validator when present; do not bypass it with another
validator, manual digest, inferred compatibility, or silent repair. Otherwise
resolve the explicit paths and run:

```text
<python> <skill-root>/scripts/validate_phase_artifacts.py <phase-directory>
```

Bundled validation uses schema `1`; do not infer cross-version compatibility.
Its `PASS` proves structure and internal consistency only.
It checks STATUS, the phase index, and the current STEP. Inspect named
dependencies only where they affect the contract; unrelated drafts and
historical document hygiene do not block the bundled handoff. Optional
`--check-all-docs` reports directory-wide hygiene warnings.

Record one digest per reviewed STEP version at formal handoff. Recheck at a
new executor or resumed session, after relevant artifact changes, or when an
explicit repository gate requires it. Expected code edits do not change the
STEP digest or invalidate its contract; recheck assumptions if actual
repository changes contradict them. The digest is a document fingerprint,
not evidence of code quality, live Git state, or authorization.

A checkpoint mismatch is non-executable, not automatically `BLOCKED`. Expected,
attributable post-readiness edits are `STALE`: repeat the selected review for a
material delta, or confirm a clearly non-material diff, before recording a new
checkpoint. Unexplained drift or a material contract, boundary, authority, or
evidence conflict is `BLOCKED`. Never refresh the hash without reviewing the
delta or silently repair STATUS.
Bundled CLI results distinguish structural `FAIL`, pending synchronization
`STALE`, and recorded-conflict `BLOCKED`; all return a nonzero exit code. A
digest mismatch needs classification, not an automatic material block. Only
the planner can refresh the checkpoint after the required delta confirmation.

Give the executor only applicable repository instructions, STATUS, the current
STEP, and named read-only references. Handoff `PASS` grants no extra authority.

## Validation and role separation

Match validation depth to risk and never promote blocked or inferred evidence
to `PASS`. The planner owns boundaries, handoff validation, and independent
acceptance. The executor implements and verifies only the current STEP; it
cannot redefine scope or acceptance, approve itself, or define a successor.
The planner does not implement while acting as planner.
Acceptance inspects the actual diff and raw evidence afresh, rather than
endorsing the executor's summary. Use a separate reviewer when the project or
review route requires it; role labels alone are not an independent check.

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
- `scripts/validate_phase_artifacts.py` at handoff, a new executor or resumed
  session, relevant artifact changes, or an explicit repository gate;
- `scripts/validate_handoff_contract.py` after changing bundled templates,
  validator, or executor handoff contract.

Cross-skill prose hints are advisory maintenance checks. Missing resources,
broken references, invalid template structure, and failed fixtures remain
errors; exact phrasing does not establish semantic correctness.

Keep project architecture, paths, commands, thresholds, and stricter schemas in
repository instructions or phase artifacts, not this skill.

Prefer fewer bounded steps, evidence over assumptions, and execution over
documentation. Use process only while it reduces risk.
