# Reusable implementation failure patterns

Read only the patterns relevant to the current phase or step. Convert each selected lesson into a concrete contract, test guard, or stop condition.

## Hidden factory side effects

**Signal:** Creating a query, helper, or fixture changes later execution behavior.

**Typical cause:** A factory registers real handlers, starts a thread, creates persistent state, or mutates a module-level registry while assembling dependencies.

**Required guards:** Keep read-only construction side-effect free; move startup registration to an explicit composition-root function; test that existing fakes remain registered after creating unrelated services.

## False-green external effects

**Signal:** Tests pass but open a browser or folder, launch a process, send a notification, use the network, or write to real user storage.

**Typical cause:** Test data reaches a real adapter after a fake is overwritten or patched at the wrong import path.

**Required guards:** Install default-deny external-effect fixtures; inject recording fakes; assert effect counts; treat any unintended real effect as a failed run regardless of test-framework status.

## Oversized phase handoff

**Signal:** An implementation model skips older requirements, changes unrelated files, or completes later UI work before foundational contracts are accepted.

**Typical cause:** The whole phase is assigned as one task and correctness depends on long chat memory.

**Required guards:** Split by independently accepted outcome; give one step at a time; maintain one evidence-backed status snapshot; detail later steps only after predecessor interfaces stabilize.

## Stale plan treated as repository truth

**Signal:** A model reimplements existing work, targets obsolete interfaces, or reports completion for scaffold-only files.

**Typical cause:** The phase document is read without auditing code, migrations, tests, untracked files, and retained evidence.

**Required guards:** Audit before status generation; distinguish scaffolded, implemented, tested, accepted, and release-ready; stop when code reality contradicts the step.

## Shared state and test-order dependence

**Signal:** Tests pass alone but fail or perform different actions in another order.

**Typical cause:** Registries, singletons, caches, environment variables, or fixtures are not restored to their previous state.

**Required guards:** Document all write points; restore prior state in fixtures; run targeted order-independence checks; avoid relying on another fixture to have registered a fake.

## Report written before evidence

**Signal:** An acceptance document says “passed” while required tests, resource measurements, privacy checks, or raw evidence are absent or stale.

**Typical cause:** Documentation is treated as an implementation deliverable rather than the final result of verification.

**Required guards:** Generate claims from the current run; record exact commands and results; update status and reports only after all required evidence exists; distinguish development complete, accepted, and release-ready.
