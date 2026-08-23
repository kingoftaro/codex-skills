---
name: deliver-code-change
description: Implement and verify one bounded code change whose behavior, consumers, or verification justify a dedicated workflow. Do not use for trivial documentation, formatting, comment-only, or similarly obvious low-risk edits; do not use to plan a multi-stage phase.
---

# Deliver Code Change

Implement and verify one bounded outcome. This skill owns execution, not
multi-stage planning, architecture decisions, or unfamiliar-codebase
exploration.

## Entry and exit gates

Handle an edit directly under repository instructions, without this skill or
process artifacts, only when every condition holds:

- no current phase handoff governs it;
- it is local, obvious, reversible, and its consumers are known;
- it changes no shared contract, dependency, configuration, persisted data, or
  schema;
- it involves no security, authorization, privacy, money, concurrency,
  destructive behavior, or external side effect;
- one focused check gives proportionate confidence.

If this skill was already selected for such an edit, use the Fast route, load
no supporting reference without a concrete uncertainty, and create no planning
or persistent-state artifacts.

Use `phase-step-planner` before implementation for multiple independently
accepted outcomes or persistent phase state. If product or architecture
decisions remain unresolved, stop and return the required decision, viable
options and tradeoffs, affected contracts, and smallest safe temporary
boundary.

## Execution contract

Before editing:

1. Read applicable repository instructions, inspect Git/current changes and
   relevant implementation, and preserve unrelated work.
2. Confirm one outcome, its consumers, expected behavior, file or module
   boundary, and acceptance evidence.
3. Choose Fast, Standard, or High-risk; risk overrides diff size.
4. Plan only to that route's depth.
5. Implement the smallest coherent change.
6. Verify with repository-native evidence.
7. Perform consequential actions only with explicit authorization.

Source diffs, raw command output, test results, and inspected runtime behavior
are evidence. Generated reports and assumptions are not.

This skill may edit code and required tests and validate the result. It must
not define requirements, redesign unrelated components, create engineering
processes, or silently widen scope.

## Phase-managed work

When an applicable phase handoff exists:

- read [references/phase-handoff.md](references/phase-handoff.md);
- run the validator named by repository instructions;
- treat the verified STEP as the complete implementation boundary;
- implement only its approved outcome.

The repository-named validator is authoritative. Do not bypass a failure using
a bundled validator, manual digest, inferred compatibility, or silent artifact
repair. Stop before editing when the handoff is not executable.

The executor must not modify phase status, create STEP files, expand file or
side-effect boundaries, redefine acceptance, approve its work, or define the
successor. Return evidence to the planner.

## Route selection

Choose exactly one route after the direct-edit gate:

| Route | Use | Required depth |
|---|---|---|
| Fast | Localized, obvious, low-risk correction | Inspect, edit, focused check |
| Standard | Cross-file behavior, interface change, or moderate uncertainty | Concise dependency-aware plan and verification |
| High-risk | Security, data migration, concurrency, authorization, destructive behavior, or external effects | Explicit invariants, failure modes, recovery, and stronger evidence |

A one-line authentication or permission change is High-risk.

- Fast: keep only a short internal checklist and normally load no reference.
- Standard: track implementation steps, affected areas, and verification.
- High-risk: identify invariants, failure modes, recovery strategy, and
  acceptance evidence before editing.

## Implementation

For Standard and High-risk work, read
[references/implementation.md](references/implementation.md). For High-risk
work, also read [references/risk-controls.md](references/risk-controls.md).

Inspect definitions and consumers, follow repository conventions, reuse
existing abstractions, and prefer minimal compatible diffs. Avoid unrelated
cleanup, speculative refactoring, new dependencies, frameworks, or
abstractions. After editing, inspect the changed files and exclude unrelated
changes.

Implement established decisions; do not introduce new system boundaries,
replace architecture, redesign data models, generalize a framework, or migrate
technologies without the required decision and authority.

## Verification

For Standard and High-risk work, read
[references/verification.md](references/verification.md), then only a matching
`references/toolchain-*.md` when it adds useful repository-specific commands.
Fast work normally runs its focused repository-native check directly.

Prefer existing scripts, CI commands, and test frameworks. Do not install
missing tools automatically. Classify every relevant check:

- `PASS`: executed and satisfied its criterion;
- `FAIL`: executed and found a defect;
- `BLOCKED`: could not execute because a dependency, credential, service, or
  permission was unavailable;
- `NOT_APPLICABLE`: does not apply.

Never convert skipped, assumed, or blocked checks into `PASS`, and do not claim
unit tests prove external integration behavior.

## Persistent state and handoff

Do not create persistent task state by default. It is justified only for
cross-session work or interruption recovery when no project mechanism exists.
Then read [references/recovery.md](references/recovery.md), use one explicit
path, and never create a second state file beside an applicable phase
`STATUS.md`.

The final handoff reports:

1. outcome and files changed;
2. verification commands and classified results;
3. assumptions and skipped or blocked checks;
4. remaining risks and required user actions.

For phase-managed work, also report boundary compliance, deviations, and
evidence for planner review. Do not mark phase acceptance, update STATUS, or
define next steps.

## Authority and resources

Never commit, push, deploy, publish, open a pull request, modify a remote,
install dependencies, or perform a destructive operation without explicit
authorization.

Read supporting material only when its condition applies:

| Resource | Condition |
|---|---|
| `references/phase-handoff.md` | An applicable phase STATUS and STEP govern |
| `references/routing.md` | Route or risk escalation is unclear |
| `references/planning.md` | Standard or High-risk planning needs detail |
| `references/implementation.md` | Standard or High-risk implementation |
| `references/verification.md` | Standard or High-risk verification |
| `references/risk-controls.md` | Any High-risk trigger is present |
| `references/recovery.md` | Persistent standalone state is justified |
| `references/contract-format.md` | A supported Python interface contract can be structural |
| `references/toolchain-*.md` | Matching language exists and the file adds useful commands |

Use `scripts/detect_project.py` only when repository shape or toolchains remain
unclear. Use `scripts/check_python_contracts.py` only for an explicit supported
Python contract. Scripts supply evidence, never permission or wider scope.

Higher-priority repository instructions win. Never overwrite unrelated work,
weaken validation or security, report unexecuted checks as complete, add an
unjustified dependency, or expand scope silently. Prefer the smallest correct
change.
