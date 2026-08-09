# Implementation Discipline

## Inspect before editing

- Read the target definition, nearby tests, callers, data models, configuration, and error paths.
- Search by symbol and behavior, not only by guessed filenames.
- Identify generated files and their source generators before editing them.
- Check version-control status and distinguish baseline changes from task changes.

## Make the smallest coherent change

Apply this order:

1. Reuse an existing implementation.
2. Extend an established local abstraction.
3. Use the language or platform standard library.
4. Use an already-installed dependency.
5. Add minimal new code.
6. Propose a new dependency only when its lifecycle cost is justified.

Smallest does not mean shortest at the expense of validation, security, readability, accessibility, observability, or data safety.

## Preserve contracts

When changing a function, type, endpoint, event, configuration key, or persisted structure:

- Find all known producers and consumers.
- Preserve compatibility unless the request permits a breaking change.
- Update tests and documentation that encode the changed contract.
- Avoid compatibility aliases without an exit condition.

## Handle failures explicitly

- Follow established error types and propagation patterns.
- Define timeout, retry, cancellation, and partial-failure behavior where applicable.
- Keep retries bounded and idempotent.
- Avoid broad exception swallowing and fallback values that hide corruption.

## Keep the diff clean

- Avoid unrelated renames, formatting churn, dependency upgrades, and architecture rewrites.
- Do not edit lockfiles manually.
- Do not weaken tests or linters to accommodate the change.
- Reinspect the diff before declaring completion.
