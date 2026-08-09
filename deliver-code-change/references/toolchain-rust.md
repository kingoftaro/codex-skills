# Rust Toolchain

Infer workspace members, features, targets, and commands from `Cargo.toml`, CI, task runners, and project documentation.

Typical evidence:

- Focused test: `cargo test <test-name>` with required package or feature flags
- Package tests: `cargo test -p <package>`
- Compile check: `cargo check -p <package>`
- Lint: `cargo clippy -p <package> -- -D warnings` when consistent with repository policy
- Format check: `cargo fmt --check`

Preserve the repository's feature matrix. A default-feature build does not prove optional or production feature combinations.
