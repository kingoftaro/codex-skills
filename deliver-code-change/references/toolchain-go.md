# Go Toolchain

Infer package boundaries and commands from `go.mod`, workspaces, CI, Makefiles, and project documentation.

Typical evidence:

- Focused test: `go test ./path/to/package -run <TestName>`
- Relevant packages: `go test ./path/to/...`
- Static analysis: `go vet ./path/to/...`
- Formatting check: inspect `gofmt -l <paths>` output

Use broader `go test ./...` when repository policy or change impact requires it.
For concurrency changes, run the repository's race-testing approach when
available. Select High-risk when races can materially violate shared-state
correctness, data integrity, or consequential effects; classify other changes
by their demonstrated impact.
