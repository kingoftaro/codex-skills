# Codex Skills

[简体中文](README.zh-CN.md)

A curated collection of Codex skills for evidence-backed software delivery. The repository separates phase-level planning from bounded implementation so large work can be decomposed, executed, and accepted without relying on chat history.

## Skills

| Skill | Responsibility | Use it when |
|---|---|---|
| [`phase-step-planner`](phase-step-planner/) | Audit a large phase, split it into independently verifiable steps, maintain one status snapshot, and prepare safe handoffs | Work spans multiple acceptance gates, sessions, or implementation models |
| [`deliver-code-change`](deliver-code-change/) | Implement, verify, and hand off one bounded code change | A bug fix, feature adjustment, refactor, interface change, or current phase STEP is ready to execute |

## How they work together

```text
phase-step-planner
  -> audit repository evidence
  -> freeze one current STEP and its checkpoint

deliver-code-change
  -> validate the handoff
  -> implement only that bounded STEP
  -> return code and verification evidence

phase-step-planner
  -> accept or reject from repository evidence
  -> update STATUS and prepare the next STEP
```

For a standalone bounded change, use `deliver-code-change` directly. For a multi-stage phase, start with `phase-step-planner` and execute one accepted step at a time.

## Repository layout

```text
codex-skills/
├── deliver-code-change/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
└── phase-step-planner/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```

Each skill is self-contained. Copy only the skill directories you want to install.

## Installation

Clone the repository:

```powershell
git clone https://github.com/kingoftaro/codex-skills.git
```

Install a skill into your personal Codex skills directory on Windows:

```powershell
Copy-Item -Recurse .\codex-skills\deliver-code-change "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\codex-skills\phase-step-planner "$env:USERPROFILE\.codex\skills\"
```

If a skill with the same name already exists, review the diff before replacing it.

## Usage

Implement one bounded change:

```text
Use $deliver-code-change to implement and verify this bounded code change without expanding its approved scope.
```

Plan or resume a large phase:

```text
Use $phase-step-planner to audit this phase and prepare the next bounded implementation step.
```

## Validation

Validate `deliver-code-change` with the Python standard library:

```powershell
python .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
```

Run the isolated `phase-step-planner` validator tests:

```powershell
Push-Location .\phase-step-planner\scripts
python -m unittest -v test_validate_phase_artifacts.py
Pop-Location
```

Validate generated phase artifacts:

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

The validation and unit-test paths use only local files and do not require network access.

## Design principles

- Repository evidence outranks model summaries and stale reports.
- One bounded outcome is implemented at a time.
- File scope and external side effects are explicit.
- Tests must isolate browser, process, notification, network, and real-user-data effects.
- Verification is reported as `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE` without upgrading weaker evidence.
- Commits, pushes, deployments, installations, migrations, deletions, and remote changes require appropriate authority.
