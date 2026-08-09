# Verification

Verification must answer two questions: did the requested behavior work, and did the change damage nearby behavior?

## Evidence order

Use the strongest available evidence in this order:

1. Repository-defined CI or task-runner command scoped to the change.
2. Focused behavior test reproducing the request or defect.
3. Relevant package or module test suite.
4. Static type, compile, lint, and formatting checks.
5. Runtime smoke test in a representative environment.
6. Manual inspection or simulation, clearly labeled as weaker evidence.

Do not run an expensive full suite when focused checks provide sufficient confidence unless repository policy or risk requires it.

## Minimum by route

### Fast

- Run the narrowest behavior check that would fail before the change and pass after it.
- Run a cheap syntax, compile, or type check when available.

### Standard

- Run focused tests for changed behavior.
- Run relevant module or package tests.
- Run repository-configured static checks for affected code.
- Check known consumers when a contract changes.

### High-risk

- Perform all Standard checks.
- Execute the matching controls in `risk-controls.md`.
- Exercise failure and recovery paths, not only the happy path.
- Verify against a representative integration or environment when available.
- Report any unavailable integration as `BLOCKED`, with alternative evidence separated.

## Result vocabulary

Use only:

- `PASS`: command or observation executed and met its criterion.
- `FAIL`: command or observation executed and found a defect.
- `BLOCKED`: execution prevented by environment, dependency, credential, service, or permission.
- `NOT_APPLICABLE`: check is irrelevant to the change.

Include the exact command and concise result. If a command was not run, do not imply that it passed.

## Missing tools

- Do not install tools automatically.
- Prefer an existing equivalent declared by the repository.
- If installation is necessary, explain why and request authorization.
- When blocked, perform safe alternative inspection or tests and label their limits.
