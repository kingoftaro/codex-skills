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
- Stable phase facts have one documented authority; STEP files reference contract IDs and describe only their delta.
- Documentation depth expands through conditional risk packs instead of mandatory fields for every possible failure mode.
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

Each skill is self-contained for its primary responsibility. `deliver-code-change` can execute a standalone bounded change without the planner, and `phase-step-planner` can plan and review phases without the executor. When both directories are adjacent, the planner's handoff validator also checks their shared schema contract. `SKILL.md` is each skill's entry point; supporting references are loaded only when their conditions apply.

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

The scripts require Python 3.10 or newer and use only the standard library. The examples below assume `python` resolves to the selected interpreter; otherwise replace it with that interpreter's absolute path.

Validate the structure of both skills:

```powershell
python .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
python .\deliver-code-change\scripts\validate_skill.py .\phase-step-planner
```

Prepare a new schema 2 Git handoff after its semantic consistency review. This
single command writes the STEP digest and live Git snapshot into `STATUS.md`,
then validates the result:

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py --prepare <phase-directory>
```

Revalidate an existing handoff without changing it:

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

Schema 2 keeps machine facts once in a JSON block in `STATUS.md`, binds the
phase contract registry and current STEP by digest, rejects STEP contract IDs
that are absent from the registry, and compares recorded HEAD and worktree
fingerprints with live Git. The worktree fingerprint excludes STATUS and the
digested STEP to avoid a self-referential snapshot. Manual repository mode is available for
non-Git projects and requires an independent repository comparison. Existing
schema 1 handoffs remain valid but retain their legacy cross-document checks
and do not gain live Git validation.

Run both regression test suites:

```powershell
python -m unittest discover .\deliver-code-change\scripts -p "test_*.py"
python -m unittest discover .\phase-step-planner\scripts -p "test_*.py"
```

Validate the planner/executor handoff contract:

```powershell
python .\phase-step-planner\scripts\validate_handoff_contract.py
```

When `deliver-code-change` is installed next to the planner, this command validates both sides of the integration. Otherwise it validates the planner contract and reports the executor check as `NOT_APPLICABLE`. The GitHub Actions workflow runs the same gates on Python 3.10 and 3.13. None of the validation scripts installs dependencies or accesses the network.

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
