# Pre-step consistency review

Run this review immediately before creating, detailing, or materially rewriting
an executable STEP. Its purpose is to prevent an outdated or contradictory
upstream artifact from becoming a downstream implementation contract.

## Build the evidence set

Inspect the applicable project rules, phase plan, phase index, `STATUS.md`, the
predecessor STEP and acceptance evidence, architectural decisions, current Git
checkpoint and worktree, code definitions and consumers, migrations or schemas,
configuration, relevant tests, and raw validation evidence. Use current files
and command results; do not substitute chat history or a model summary.

## Reconcile in this order

1. **State:** Confirm that accepted, current, outlined, blocked, and deferred
   labels agree across the phase documents and repository evidence.
2. **Predecessor:** Confirm its deliverables exist, its required checks apply to
   the current bytes, and any open defect that affects the successor is visible
   in `STATUS.md`.
3. **Data:** Compare schema and migration versions, persisted shapes, ownership,
   defaults, nullability, indexes or constraints, and compatibility windows.
4. **Interfaces:** Trace authoritative definitions to producers and consumers;
   compare names, types, parameters, return values, errors, events, and version
   rules with every document the proposed STEP relies on.
5. **Behavioral constraints:** Compare invariants, state transitions,
   transaction or concurrency boundaries, authorization, side effects,
   rollback, degraded behavior, and required test isolation.
6. **Evidence:** Confirm validation commands still exist, exercise the claimed
   paths, and were run after the latest relevant behavior change.

Prefer executable evidence when determining what currently exists. Prefer an
explicit accepted decision when determining what was intended. A difference
between them is a contradiction to resolve, not permission to select whichever
source makes the next STEP easier.

## Decide the gate

Mark `PASS` only when every material dependency of the proposed STEP has one
consistent, evidence-backed interpretation. Update stale `STATUS.md` facts from
repository evidence before marking `PASS`, then record the review timestamp,
repository/worktree checkpoint, sources, comparisons, and result.

Mark `STALE` when repository evidence is internally consistent and the intended
contract is clear, but `STATUS.md`, the phase index, predecessor records, or
retained evidence has not been synchronized with it. Update only the stale
planning or status artifacts within the authorized scope, rerun affected
checks, then repeat the full review. `STALE` is not permission to write or hand
off a detailed STEP.

Mark `BLOCKED` and do not write or revise the detailed STEP when a conflict can
change its outcome, dependencies, file boundary, contract, implementation
order, side-effect policy, or acceptance gate. Record:

- the conflicting sources and exact facts;
- whether the problem is stale documentation, defective implementation,
  missing evidence, or an unresolved design decision;
- the upstream artifact or behavior that must be corrected;
- the commands or observations required for re-review.

Do not repair code while performing a planning-only review unless the user has
separately authorized implementation. After any correction, rerun the affected
baseline and the full consistency review before detailing the STEP.
