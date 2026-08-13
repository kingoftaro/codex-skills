# Codex Skills

English | [简体中文](./README.zh-CN.md)

A focused collection of Codex skills for planning and delivering software changes with explicit scope, repository evidence, and verifiable handoffs.

This repository contains two complementary skills:

| Skill | Responsibility | Use it when |
|---|---|---|
| [`phase-step-planner`](./phase-step-planner/) | Audit a large software phase and split it into bounded, independently verifiable implementation steps | Work spans multiple acceptance gates, sessions, or implementation models |
| [`deliver-code-change`](./deliver-code-change/) | Implement and verify one bounded code change without silently expanding scope | A bug fix, feature, refactor, interface change, migration step, or accepted phase step is ready to execute |

## How the skills work together

```text
phase-step-planner
  -> audit repository evidence
  -> reconcile plans, code, migrations, tests, and retained evidence
  -> define one current executable step

deliver-code-change
  -> validate the handoff
  -> rehearse side-effect and test boundaries
  -> implement only the bounded change
  -> return code and verification evidence

phase-step-planner
  -> accept or reject from repository evidence
  -> update phase status
  -> prepare the next step
```

Use `deliver-code-change` directly for a standalone, well-bounded change. Use `phase-step-planner` first when the work contains multiple independently accepted outcomes or must survive handoffs between sessions or models.

## Design principles

- Repository evidence outranks model summaries and stale reports.
- One bounded outcome is implemented at a time.
- File scope, contracts, state transitions, and external side effects are explicit.
- Automated tests isolate browsers, processes, notifications, networks, and real user data.
- Factories and read-only constructors do not trigger hidden startup effects.
- Validation is reported as `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE` without overstating weaker evidence.
- Commits, pushes, deployments, migrations, deletions, and other consequential actions require appropriate authority.

## Repository layout

```text
codex-skills/
+-- deliver-code-change/
|   +-- SKILL.md
|   +-- README.md
|   +-- agents/
|   +-- references/
|   `-- scripts/
`-- phase-step-planner/
    +-- SKILL.md
    +-- agents/
    +-- assets/
    +-- references/
    `-- scripts/
```

Each skill is self-contained. `SKILL.md` is the entry point; supporting references are loaded only when their conditions apply.

## Installation

Clone the repository:

```powershell
git clone https://github.com/kingoftaro/codex-skills.git
cd codex-skills
```

Copy either or both skill directories into your personal Codex skills directory on Windows:

```powershell
Copy-Item -Recurse .\deliver-code-change "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\phase-step-planner "$env:USERPROFILE\.codex\skills\"
```

Review the diff before replacing an existing installation. Restart Codex or open a new task if the updated skill is not picked up immediately.

## Usage

Implement one bounded change:

```text
Use $deliver-code-change to implement and verify this bounded code change without expanding its approved scope.
```

Plan or resume a large phase:

```text
Use $phase-step-planner to audit this phase and prepare the next bounded implementation step.
```

For a phase handoff, provide the implementation model with the applicable project instructions, the phase `STATUS.md`, the current `STEP_*.md`, and explicitly named read-only references.

## Local validation

Validate the structure of `deliver-code-change`:

```powershell
python .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
```

Validate a generated phase handoff:

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

Validate the planner/executor handoff contract:

```powershell
python .\phase-step-planner\scripts\validate_handoff_contract.py
```

These scripts use the Python standard library and do not install dependencies or access the network.

## Maintaining the repository

The repository is intentionally initialized at the directory that contains both skill folders. This keeps both skills under one history and makes future updates straightforward:

```powershell
git status
git diff
git add README.md deliver-code-change phase-step-planner
git commit -m "Update Codex skills"
git push
```

Before publishing, review the staged file list, keep generated caches and local configuration out of Git, and record any blocked validation honestly.

## License

No license has been added yet. Unless a license is added, copyright remains with the repository owner and reuse is not automatically granted.
