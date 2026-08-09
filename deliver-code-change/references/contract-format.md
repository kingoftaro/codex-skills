# Python Contract Format

Use the checker only when an interface contract can be represented as explicit JSON. Do not scrape arbitrary Markdown signatures.

## Format

```json
{
  "symbols": [
    {
      "qualified_name": "payments.service.PaymentService.charge",
      "kind": "method",
      "parameters": ["amount", "currency"],
      "return_annotation": "Receipt",
      "async": true
    }
  ]
}
```

Fields:

- `qualified_name`: module-qualified symbol relative to the supplied source root.
- `kind`: `function`, `method`, or `class`.
- `parameters`: parameter names in declaration order. Use `*name` and `**name` for variadic parameters. Omit `self` and `cls` from methods.
- `return_annotation`: exact normalized source annotation. Omit when the contract does not constrain it.
- `async`: optional boolean for functions and methods.

Run:

```text
python scripts/check_python_contracts.py --contract contract.json --source-root src
```

Use [contract-example.json](contract-example.json) as a minimal working example. It also provides a self-check fixture for the bundled scripts.

The command fails when the contract is empty, malformed, ambiguous, missing symbols, mismatched, or when a Python source file cannot be parsed. It checks structure only; it does not prove business behavior, side effects, authorization, error semantics, or runtime compatibility.
