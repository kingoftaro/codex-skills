# TypeScript and JavaScript Toolchain

Infer commands from `package.json`, lockfiles, workspace configuration, CI, and project documentation. Use the detected package manager and existing scripts.

Prefer package scripts such as:

- Focused or project tests: `<manager> test` or the repository's scoped test script
- Type checking: `<manager> run typecheck` or configured `tsc --noEmit`
- Lint: `<manager> run lint`
- Build: `<manager> run build`

Do not substitute npm, pnpm, yarn, or bun when the repository declares another manager. Do not regenerate a lockfile unless dependency changes are part of the request. For browser or service behavior, distinguish unit tests from an actual runtime check.
