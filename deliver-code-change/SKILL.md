---
name: deliver-code-change
description: Implement, verify, and hand off one bounded code change in an existing repository, either as a standalone task or as the current verified step from phase-step-planner. Use for a scoped bug fix, feature adjustment, refactor, interface change, or migration step after its execution boundary is clear. Route work by uncertainty and operational risk, preserve user changes, use native toolchains, and require authority for consequential side effects. Do not use to decompose or manage a multi-stage phase.
---

# Deliver Code Change

Deliver one bounded change and produce evidence proportional to its risk. Let phase planning own phase state; let this Skill own implementation of the current change.

## Core contract

1. Read repository instructions and inspect the current state before editing.
2. Preserve user-owned and unrelated changes.
3. Establish whether the change is standalone or governed by a verified phase handoff.
4. Classify the bounded change as Fast, Standard, or High-risk before implementation.
5. Plan only to the depth needed for the selected route without redesigning a governing phase.
6. Implement the narrowest coherent diff that preserves existing conventions.
7. Verify behavior with the project's existing tools and report exact evidence.
8. Perform commits, pushes, deployments, installations, deletions, migrations, or other consequential actions only when authorized.

Treat source diffs, command output, test results, and inspected runtime behavior as proof. Do not treat generated reports as proof.

## Execution boundary

- **Standalone change**: derive one outcome, explicit non-goals, file scope, and acceptance evidence from the request and repository.
- **Phase-managed change**: when the user supplies or the repository identifies an applicable `STATUS.md` and current `STEP_*.md`, read [references/phase-handoff.md](references/phase-handoff.md). Treat the verified STEP as the implementation boundary after higher-priority user and repository instructions.
- **Not yet bounded**: when the request spans multiple independent acceptance gates or needs phase decomposition, stop before implementation and use or recommend `phase-step-planner`. Do not create phase README, STATUS, or STEP artifacts from this Skill.

## Workflow

### 1. Establish scope and authority

- Read applicable `AGENTS.md`, repository instructions, manifests, CI configuration, and nearby code.
- Inspect version-control status before editing when the project uses version control.
- Identify the requested outcome, acceptance evidence, affected interfaces, and actions that require additional authorization.
- Detect an applicable phase handoff before creating a standalone plan. Validate it before editing and stop if it is stale, contradictory, terminal, or outside the requested scope.
- Diagnose without editing when the user asked only for analysis, review, explanation, or status.
- Ask only when a missing choice would materially change the result or authorize a new side effect. Otherwise make a narrow, reversible assumption and state it.

Run `scripts/detect_project.py <project-root>` when project shape or available toolchains are not already obvious. Treat its JSON as discovery evidence, not as permission to install or execute tools.

### 2. Select a route

Read [references/routing.md](references/routing.md) and choose exactly one route for the bounded change or current phase step:

| Route | Typical use | Required depth |
|---|---|---|
| Fast | Localized, clear, low-risk correction | Inspect, edit, focused verification |
| Standard | Cross-file behavior, interface change, or meaningful uncertainty | Concise plan, dependency-aware implementation, static checks and tests |
| High-risk | Security, money, migration, state transitions, concurrency, destructive data behavior, external side effects, or operations | Explicit contract and recovery thinking, staged implementation, risk-specific verification |

Risk overrides size. A one-line authorization or money change is High-risk. Explain the route in one sentence before substantial work when it affects execution depth.

### 3. Plan proportionally

Read [references/planning.md](references/planning.md).

- Phase-managed: use the verified STEP as the plan authority. Maintain only a small execution checklist; do not redefine its outcome, file boundary, side-effect policy, or acceptance gate.
- Fast: keep a short internal checklist unless the user requests a written plan.
- Standard: maintain a concise ordered plan with verification steps.
- High-risk: record invariants, failure modes, rollback or recovery approach, and acceptance evidence before editing.
- Use an existing OpenSpec or comparable specification workflow when the repository already uses it or the user requests it. Do not initialize a specification system automatically.

### 4. Implement the change

Read [references/implementation.md](references/implementation.md). Also read [references/risk-controls.md](references/risk-controls.md) for every High-risk task.

- Locate definitions and consumers before changing a contract.
- Reuse established abstractions and installed dependencies before introducing new ones.
- Keep the diff scoped; avoid speculative frameworks, unrelated cleanup, and generated process files.
- Follow repository style and error-handling conventions unless they conflict with safety or the user request.
- Check the working tree after editing so unrelated changes are not accidentally included.

### 5. Verify with evidence

Read [references/verification.md](references/verification.md), then read only the matching toolchain reference:

- Python: [references/toolchain-python.md](references/toolchain-python.md)
- TypeScript or JavaScript: [references/toolchain-typescript.md](references/toolchain-typescript.md)
- Go: [references/toolchain-go.md](references/toolchain-go.md)
- Rust: [references/toolchain-rust.md](references/toolchain-rust.md)

Prefer commands declared by the repository, CI, task runner, or package manager. Do not install missing tools automatically. Distinguish clearly between:

- `PASS`: executed and satisfied the stated criterion.
- `FAIL`: executed and found a defect.
- `BLOCKED`: could not execute because a dependency, credential, service, or permission was unavailable.
- `NOT_APPLICABLE`: the check does not apply to the changed behavior.

Never convert `BLOCKED` into `PASS`. Use a weaker alternative check when useful, but label it as alternative evidence.

For a Python project with an explicit structured contract, read [references/contract-format.md](references/contract-format.md) and use `scripts/check_python_contracts.py` for a deterministic signature check. Do not claim contract verification when the contract contains no supported symbols.

### 6. Hand off

Report:

1. The outcome and important files changed.
2. Verification commands and their results.
3. Assumptions, skipped or blocked checks, and remaining risks.
4. Any user action still required.

For a phase-managed change, also report boundary compliance, deviations or contradictions, and evidence suitable for the phase planner's acceptance review. Do not mark the STEP accepted, edit `STATUS.md`, or detail the next step while acting as the executor.

Commit only when the user explicitly requested a commit or the active workflow clearly includes it. Push, deploy, publish, open pull requests, modify remote services, or install dependencies only with corresponding authority.

## Persistent state

Default to no pipeline artifacts. Never create a second task-state file when an applicable phase `STATUS.md` exists. Use persistent state only for a standalone, long or interruption-prone change when the surrounding product does not already provide reliable task state.

When persistence is justified, read [references/recovery.md](references/recovery.md) and use `scripts/manage_state.py` with an explicit state-file path. Mark completion by writing a completed state; completed state is immutable, so initialize a new state file for later work rather than reopening it. Do not delete state automatically.

## Non-negotiable rules

- Never overwrite or revert unrelated user changes.
- Never weaken tests, validation, authorization, or error handling merely to make checks pass.
- Never report a check as executed when it was inferred, simulated, skipped, or blocked.
- Never assume that a clean unit test proves an external integration, migration, deployment, or runtime environment works.
- Never add a dependency when the repository or standard library already provides a suitable solution without documenting the tradeoff.
- Never present placeholder-filled deliverables as completed work.
- Never widen, replace, or silently repair a governing phase STEP while acting as its executor.
- Never update phase acceptance state from implementation claims alone.
- Follow the user's deletion policy and list exact targets before any deletion when approval is required.

## Resource map

Read references only when their condition applies:

| Resource | Read when |
|---|---|
| `routing.md` | Every implementation task |
| `phase-handoff.md` | An applicable phase STATUS and STEP govern the change |
| `planning.md` | Standard or High-risk tasks, or when the user requests a plan |
| `implementation.md` | Every implementation task |
| `verification.md` | Every implementation task |
| `risk-controls.md` | Any High-risk trigger is present |
| `recovery.md` | Persistent cross-session state is justified |
| `contract-format.md` | A Python interface contract can be expressed structurally |
| `toolchain-*.md` | The corresponding language is present |

If repository instructions conflict with this skill, follow the higher-priority instruction and state the practical consequence.
