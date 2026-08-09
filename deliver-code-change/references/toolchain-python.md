# Python Toolchain

Infer commands from `pyproject.toml`, lockfiles, CI, tox or nox configuration, Makefiles, and project documentation. Prefer the repository's environment manager.

Typical evidence, only when configured or already available:

- Focused tests: `pytest path/to/test_file.py -q`
- Test selection: `pytest -k <expression> -q`
- Type checking: `mypy <package>` or `pyright <package>`
- Lint: `ruff check <paths>`
- Format check: `ruff format --check <paths>` or the configured formatter
- Compile smoke check: `python -m compileall <package>`

Do not assume a `src/` layout. Do not import production modules when importing triggers irreversible side effects. Use the interpreter and commands selected by the project rather than a global `python` when possible.
