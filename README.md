# Codex Skills

[简体中文](README.zh-CN.md)

A curated collection of Codex skills for evidence-backed software delivery. The repository separates phase-level planning from bounded implementation so large work can be decomposed, executed, and accepted without relying on chat history.

## Skills

| Skill | Responsibility | Use it when |
|---|---|---|
| [`phase-step-planner`](phase-step-planner/) | Audit a large phase, split it into independently verifiable steps, maintain one status snapshot, and prepare safe handoffs | Work spans multiple acceptance gates, sessions, or implementation models |
| [`deliver-code-change`](deliver-code-change/) | Implement, verify, and hand off one bounded code change | Behavior, consumers, uncertainty, or verification justify a dedicated workflow, or a current phase STEP is ready to execute |

## How they work together

```text
trivial local low-risk edit
  -> follow repository instructions directly

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

Handle trivial, local, low-risk edits directly under applicable repository
instructions without loading a skill or creating process artifacts. Use
`deliver-code-change` for one bounded change that benefits from a dedicated
implementation workflow. For a multi-stage phase, start with
`phase-step-planner` and execute one accepted step at a time.

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

Implement one non-trivial bounded change:

```text
Use $deliver-code-change for this non-trivial bounded code change; implement and verify it without expanding scope.
```

Plan or resume a large phase:

```text
Use $phase-step-planner to audit this multi-stage phase and prepare one bounded executable step.
```

## Validation

Select an explicit Python interpreter instead of relying on `PATH`:

```powershell
$SkillsPython = 'C:\absolute\path\to\python.exe'
```

Validate both skill packages with the Python standard library:

```powershell
& $SkillsPython .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
& $SkillsPython .\deliver-code-change\scripts\validate_skill.py .\phase-step-planner
```

Run the isolated validator and recovery-state tests:

```powershell
Push-Location .\phase-step-planner\scripts
& $SkillsPython -B -m unittest -v test_validate_phase_artifacts.py
Pop-Location
Push-Location .\deliver-code-change\scripts
& $SkillsPython -B -m unittest -v test_manage_state.py test_validate_skill.py
Pop-Location
```

Validate generated phase artifacts:

```powershell
& $SkillsPython .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

Validate the cross-skill routing/handoff declarations and adversarial fixtures:

```powershell
& $SkillsPython .\phase-step-planner\scripts\validate_handoff_contract.py
```

The validation and unit-test paths use only local files and do not require network access.
A bundled phase-validator PASS proves structural and internal consistency; it
does not replace semantic review or a repository-local live-state validator.

## Design principles

- Repository evidence outranks model summaries and stale reports.
- Use the smallest workflow that matches uncertainty and risk; trivial edits do not require a skill.
- One bounded outcome is implemented at a time.
- Repeated repair regressions trigger root-cause review, not automatic STEP multiplication.
- File scope and external side effects are explicit.
- Tests must isolate browser, process, notification, network, and real-user-data effects.
- Verification is reported as `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE` without upgrading weaker evidence.
- Commits, pushes, deployments, installations, migrations, deletions, and remote changes require appropriate authority.
