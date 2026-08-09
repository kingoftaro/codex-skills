# Proportional Planning

Plan to remove uncertainty, coordinate dependencies, and define proof. Do not create planning artifacts merely to demonstrate process.

## Phase-managed execution

When a verified phase STEP governs the change:

- Treat its outcome, non-goals, file boundary, contracts, side-effect policy, acceptance gate, and stop conditions as authoritative.
- Produce only the implementation checklist needed to execute that STEP.
- Reclassify risk upward when repository evidence demands it, but do not expand scope or redesign later steps.
- Stop and report when the repository contradicts the STEP or required work crosses its boundary.
- Return implementation and verification evidence to the phase planner; do not update phase status or acceptance artifacts.

## Fast

Confirm three facts before editing:

1. Exact defect or requested delta.
2. Target definition and relevant consumer.
3. Focused command or observation that will prove the result.

## Standard

Maintain a short ordered plan containing:

- Scope and explicit non-goals.
- Definitions and consumers to inspect.
- Contract or behavior changes.
- Implementation order.
- Static checks and behavior tests.

Keep at most one step actively in progress. Update the plan when evidence changes the approach.

## High-risk

Before editing, state:

- Invariants that must remain true.
- Inputs, outputs, errors, side effects, and compatibility expectations.
- Failure modes and how each is detected.
- Rollback, recovery, or forward-fix strategy.
- Required test levels and unavailable environments.
- Consequential actions that need authorization.

For migrations, separate expand, migrate or backfill, switch, and contract phases when multiple application versions may coexist.

## Existing specifications

When the repository already contains OpenSpec, ADRs, RFCs, issue templates, or another specification system:

- Treat current artifacts as inputs, not unquestionable truth.
- Reconcile contradictions before implementation when they affect behavior.
- Update specifications only when the requested behavior changes and repository practice expects synchronization.
- Do not initialize, archive, or publish specification systems automatically.
