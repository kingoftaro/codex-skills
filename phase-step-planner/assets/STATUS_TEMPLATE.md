# Phase {{PHASE_ID}} current status

> This is the phase's single machine-readable handoff state. Edit the review
> result and human evidence; let `--prepare` generate digests and Git facts
> after a successful `--dry-run` preflight.

```json phase-handoff
{
  "handoff_schema": 2,
  "phase_state": "{{PHASE_STATE}}",
  "current_step": "{{CURRENT_STEP_DOCUMENT}}",
  "step_sha256": "AUTO",
  "contract_registry": "README.md",
  "contract_registry_sha256": "AUTO",
  "review_result": "{{PASS_STALE_OR_BLOCKED}}",
  "repository": {
    "mode": "git",
    "head": "AUTO",
    "worktree_sha256": "AUTO"
  }
}
```

Only `PASS` is executable. For a non-Git project, replace `repository` with
`{"mode": "manual", "checkpoint": "<exact immutable description>"}` and
perform the repository comparison outside the bundled validator.

## Position

- Last accepted step: `{{LAST_ACCEPTED_STEP_OR_NONE}}`
- Next outlined step: `{{NEXT_STEP_OR_NONE}}`

## Verified evidence

Delete unused rows or sections instead of filling them with `N/A`.

| Claim | Authority or current evidence | State |
|---|---|---|
<!-- Add only current evidence rows. -->

## Open items

| Item | Evidence | Required gate |
|---|---|---|
<!-- Add a row only for an open item. -->

Do not copy stable contracts, interfaces, or file boundaries into this file.
Keep them in the phase contract registry or current STEP and reference them by ID.
