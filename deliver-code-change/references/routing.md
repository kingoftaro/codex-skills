# Routing

Choose a route from evidence, not from a predicted file count alone.

Route only one bounded change. When a request needs multiple independently accepted steps, phase-wide status management, or re-detailing of later work, hand it to `phase-step-planner` before implementation. A phase STEP may still be Fast, Standard, or High-risk; phase size and implementation risk are separate decisions.

## Decision order

1. Select High-risk when any High-risk trigger applies.
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

Use High-risk for:

- Authentication, authorization, secrets, cryptography, or trust boundaries.
- Prices, balances, billing, financial calculations, or irreversible transactions.
- Schema migrations, backfills, data deletion, destructive transformations, or rollback-sensitive changes.
- State machines, idempotency, retries, concurrency, ordering, locking, or distributed consistency.
- External APIs, webhooks, queues, payment providers, or effects outside the repository.
- Service startup, process management, infrastructure, deployment, or production configuration.
- Privacy, regulated data, safety-critical behavior, or compatibility contracts with unknown consumers.

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

Missing tools or credentials affect verification status, not route selection.
