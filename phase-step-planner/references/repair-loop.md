# Repair-loop management

Read this reference on the first qualifying repair-introduced regression,
whenever STATUS records a non-`inactive` `Repair loop`, or before recovering a
blocked repair handoff. The matching signal and typical cause are documented in
[Symptom patch creates an adjacent regression](FAILURE_PATTERNS.md#symptom-patch-creates-an-adjacent-regression).

## Qualification gate

Increment `consecutive_regressions` only for a `CONFIRMED` or `STRONG`,
material, `repair-introduced` finding under the same current STEP and invariant
that represents a newly evidenced root-cause event, not a duplicate. The first
qualifying finding establishes the sequence. `TENTATIVE`, P3, pre-existing,
style-only, and ordinary documentation findings do not change the snapshot.

## Classify and record the finding

Classify each finding as one of:

- a latent defect that predates the current repair;
- a repair-introduced regression;
- an environment or evidence contradiction.

Record the original reproduction, governing invariant, suspected fault locus,
affected neighboring paths, repair round, and required closure evidence in the
existing STATUS risk entry. Do not create a second issue tracker. The
machine-readable `Repair loop` snapshot tracks the consecutive
repair-introduced sequence; the risk entry carries the detailed classification
and evidence.

## First qualifying regression

Keep the repair in the current STEP only while its governing invariant, file
and side-effect boundaries, and acceptance gate remain valid. Set `Repair loop`
to `observing` with one consecutive regression, a stable invariant ID, and a
current evidence reference.

Verify both the original reproduction and affected adjacent paths. Add checks
for defaults, optional values, overrides, validation, failure handling,
cleanup, and compatibility when those paths may share the invariant.

If the current STEP boundary or acceptance gate no longer covers the repair,
stop and reconcile the handoff instead of creating a successor repair STEP.

## Second consecutive qualifying regression

When the same current STEP produces a second consecutive finding that passes
the qualification gate under the same governing invariant:

1. Set `Review result` and the handoff to `BLOCKED`.
2. Set `Repair loop` to `blocked` with the invariant ID, a count of at least
   two, and current evidence.
3. Stop implementation patches and new STEP creation.
4. Do not edit acceptance claims. Update only the existing STATUS risk entry
   with the blocker and observed evidence.
5. Review the original reproduction, governing invariant, fault locus,
   neighboring paths, and evidence required for closure.

Resume implementation only after the planner establishes one corrected
executable boundary.

## Root-cause reconciliation

- When findings share one invariant and acceptance or rollback boundary,
  replace or rewrite the current STEP around one root-cause repair.
- Split only when independent acceptance or rollback boundaries are proven.
- If architecture, authority, or fault locus remains unresolved, keep the
  handoff `BLOCKED`.
- Set `Repair loop` to `reset` only after root-cause evidence establishes the
  corrected boundary; then revalidate the handoff before execution.

Symptom count never determines STEP count. Keep at most one executable repair
STEP for the same governing invariant.

## Machine-readable state

The STATUS `Repair loop` field is a JSON object with exactly these keys:

```json
{
  "state": "inactive",
  "invariant_id": "none",
  "consecutive_regressions": 0,
  "last_classification": "none",
  "evidence": "none"
}
```

State requirements:

- `inactive`: use `none` for invariant, classification, and evidence, with zero
  consecutive regressions.
- `observing`: use exactly one consecutive regression,
  `last_classification` = `repair-introduced`, plus a non-`none` invariant ID
  and evidence reference.
- `blocked`: use at least two consecutive regressions,
  `last_classification` = `repair-introduced`, a non-`none` invariant ID and
  evidence reference, and `Review result` = `BLOCKED`.
- `reset`: use zero consecutive regressions,
  `last_classification` = `repair-introduced`, retain the invariant ID, and
  record root-cause evidence for the corrected boundary.

The authoritative phase validator must reject malformed JSON, duplicate keys
(even with identical values), unknown fields or states, and illegal field
combinations. Risk-table prose supplies context
but does not override the machine-readable snapshot. Structural validation
cannot prove confidence, causality, materiality, STEP/invariant identity, or
root-cause uniqueness; the planner must establish those from evidence before
incrementing the count. A repository-local validator or schema may impose
stricter rules.
