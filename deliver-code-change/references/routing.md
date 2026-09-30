# Routing

Choose a route from evidence, not from a predicted file count alone.

Route only one bounded change. When a request needs multiple independently accepted steps, phase-wide status management, or re-detailing of later work, hand it to `phase-step-planner` before implementation. A phase STEP may still be Fast, Standard, or High-risk; phase size and implementation risk are separate decisions.

## Direct-edit gate

Keep ordinary exploration, review, and trivial edits direct. Also keep a
localized, understood, reversible correction direct when one focused check is
proportionate and no applicable phase handoff governs it. A risk keyword or
file category is context for judgment, not sufficient evidence to enter this
Skill.

If the Skill is already active for such work, use Fast without process
artifacts or additional references.

## Decision order

1. Select High-risk when evidence establishes a material consequence below.
2. Otherwise select Standard when uncertainty or coordination is material.
3. Select Fast only when the change is localized, understood, reversible, and low-risk.

## Fast

Use Fast only when all of these are true:

- The requested behavior and acceptance condition are clear.
- The affected implementation is localized and its consumers are known.
- No public contract, persisted data shape, authorization boundary, or operational behavior changes.
- Failure is easy to detect and reverse.
- No High-risk trigger applies.

Examples: typo, local formatting defect, narrow null guard, incorrect constant, or a small test correction that does not weaken coverage.

## Standard

Use Standard when any of these apply and no High-risk trigger applies:

- Multiple modules or consumers must change together.
- A public or internal interface changes.
- A new dependency, configuration value, scheduled job, or feature flag is considered.
- Existing behavior is unclear enough to require investigation.
- The change affects persistence without a schema migration.
- Regression risk requires broader tests than the immediate function.

## High-risk

Use High-risk when the change materially affects:

- Authentication, authorization, secret handling, cryptography, or trust boundaries.
- Monetary correctness or irreversible transactions.
- Persisted data through migrations, backfills, deletion, destructive transformations, or difficult rollback.
- Shared-state correctness or duplicate, reordered, retried, or cancelled actions whose failure can corrupt data or repeat consequential effects.
- External effects, including which real operations are issued, their authorization, or their recovery after failure.
- Operational availability or failure scope through startup, shutdown, infrastructure, deployment, or production configuration.
- Privacy, regulated data, safety-critical behavior, or compatibility with unknown consumers where failure has material impact.

Inspect state machines, retries, concurrency, processes, and external clients
for these consequences. Their presence alone is insufficient. A reversible
local display state or a mocked read-only client can stay Fast or Standard;
cancellation deciding whether a real device continues acting is High-risk.

High-risk remains High-risk even for a one-line diff.

## Escalation during work

Reclassify upward when inspection reveals broader impact. Do not downgrade merely because tools or environments are unavailable. Preserve the route and report blocked verification.

Record the reason compactly:

```text
Route: Standard — changes a shared response type and three known consumers; no High-risk trigger found.
```

## Calibration examples

| Request | Route | Reason |
|---|---|---|
| Correct a misspelled local label | Fast | Local, reversible, no contract or risk change |
| Add a field to a shared response type and update consumers | Standard | Coordinated contract change |
| Change one authorization condition | High-risk | Authorization overrides diff size |
| Add payment retry handling | High-risk | Money, external side effects, and idempotency |
| Refactor a private helper across two files | Standard | Cross-file regression surface without a High-risk trigger |
| Update loading/retry display behavior across components | Standard | Coordinated UI behavior with known consumers |
| Change cancellation of real device actions | High-risk | Cancellation governs consequential external effects |

Missing tools or credentials affect verification status, not route selection.
