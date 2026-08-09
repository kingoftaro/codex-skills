# High-risk Controls

Apply every matching section. Repository-specific rules may add stricter controls.

## Authentication and authorization

- Test allowed and denied paths separately.
- Verify authorization at the resource boundary, not only in the UI or route layer.
- Avoid logging secrets, tokens, credentials, or sensitive payloads.
- Check privilege escalation, tenant isolation, expiry, revocation, and replay behavior when relevant.

## Money and irreversible transactions

- Use decimal or fixed-point representations appropriate to the domain; do not use binary floating point for monetary values.
- Define currency, scale, rounding mode, and boundary behavior.
- Test zero, negative, maximum, rounding, duplicate, and partial-failure cases.
- Verify idempotency and reconciliation for external transactions.

## Migrations and destructive data behavior

- Identify backup, rollback, forward-fix, and compatibility requirements.
- Prefer expand-and-contract changes when multiple application versions may coexist.
- Test on representative data and check restartability.
- Require explicit authorization before applying a migration or deleting data.

## State, retries, and concurrency

- Enumerate legal and illegal transitions.
- Test duplicate delivery, reordering, cancellation, timeout, and concurrent execution.
- Make retries bounded and safe; persist idempotency where the side effect requires it.

## External systems

- Define timeout, retry, rate-limit, authentication, and response-validation behavior.
- Test malformed, partial, delayed, duplicate, and unavailable responses.
- Separate mocked contract evidence from a real integration result.

## Operations and deployment

- Validate configuration, startup, readiness, shutdown, and rollback behavior.
- Do not start persistent services, deploy, or change remote infrastructure without authority.
- Treat dry runs and configuration inspection as alternative evidence, not successful deployment.
