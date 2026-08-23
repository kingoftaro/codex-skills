# Recovery and Persistent State

Use persistent state only for a standalone bounded change when interruption is likely and the host does not already preserve a reliable plan. Do not use this mechanism when an applicable phase `STATUS.md` exists; the phase planner owns that state, and a second state file would create conflicting authority.

## State contents

Keep one JSON file with:

- `schema_version`
- `task_id`
- `route`
- `status`
- `current_step`
- `completed_steps`
- `changed_files`
- `verification`
- `resume_hint`
- timestamps

Do not store credentials, tokens, full source contents, or sensitive user data.
The script rejects unknown schemas, missing or extra fields, invalid field
types, illegal status/current-step combinations, non-UTC timestamps, and
updates to completed state. Do not repair rejected state by guessing; inspect
the file and establish an explicit migration or a new state file.

## Script usage

Resolve `<python>` to an explicit interpreter and `<skill-root>` to the absolute
directory containing this Skill's `SKILL.md`. Keep the target repository as the
working directory; do not assume that the Skill directory is the current
directory.

Initialize:

```text
<python> <skill-root>/scripts/manage_state.py init --file <state.json> --task-id <id> --route Standard --step inspect
```

Update after a meaningful checkpoint:

```text
<python> <skill-root>/scripts/manage_state.py update --file <state.json> --step implement --complete inspect --changed <path>
```

Inspect:

```text
<python> <skill-root>/scripts/manage_state.py show --file <state.json>
```

Complete without deleting evidence:

```text
<python> <skill-root>/scripts/manage_state.py complete --file <state.json>
```

Read current repository state again before resuming. Never assume the filesystem still matches the checkpoint. Re-run the last relevant verification when its inputs may have changed.

See [state-example.json](state-example.json) for the completed shape produced by the commands above.
