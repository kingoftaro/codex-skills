# Recovery and Persistent State

Use persistent state only for a standalone bounded change when interruption is likely and the host does not already preserve a reliable plan. Do not use this mechanism when an applicable phase `STATUS.md` exists; the phase planner owns that state, and a second state file would create conflicting authority.

## State contents

Keep one JSON file with:

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

## Script usage

Initialize:

```text
python scripts/manage_state.py init --file <state.json> --task-id <id> --route Standard --step inspect
```

Update after a meaningful checkpoint:

```text
python scripts/manage_state.py update --file <state.json> --step implement --complete inspect --changed <path>
```

Inspect:

```text
python scripts/manage_state.py show --file <state.json>
```

Complete without deleting evidence:

```text
python scripts/manage_state.py complete --file <state.json>
```

Read current repository state again before resuming. Never assume the filesystem still matches the checkpoint. Re-run the last relevant verification when its inputs may have changed.

See [state-example.json](state-example.json) for the completed shape produced by the commands above.
