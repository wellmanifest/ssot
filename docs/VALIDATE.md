# VALIDATE

## Purpose

Fail closed on an invalid interview or decision document.

## Syntax

```bash
PYTHONPATH=src python3 -m ssot validate examples/c2004.ssot.json
PYTHONPATH=src python3 -m ssot validate examples/invalid/missing-reason.ssot.json --format json
```

## Inputs

A JSON or text SSOT document.

## Outputs

`ok` or a list of findings. `--format json` emits
`wellmanifest.ssot/check-result/v1`.

## Errors

| Code | When |
| --- | --- |
| `SSOT-KIND-001` | unknown schema, kind, action, or packaging |
| `SSOT-NOISE-001` | analyzer treated as debt, or noise without questions |
| `SSOT-PIN-001` | missing pin policy or delete-mirror forbid |
| `SSOT-REASON-001` | allowed divergence without reason or question |
| `SSOT-TREE-001` | missing or unsafe tree paths |
| `SSOT-COUPLE-001` | policy allows coupling to a foreign monorepo |
| `SSOT-QUERY-001` | query namespace missing scope or leak forbid |
| `SSOT-SERVE-001` | served artifact missing rebuild or source-as-served forbid |
| `SSOT-FLEET-001` | inventory vs runtime missing dirty-tree or scan forbids |
| `SSOT-POA-001` | capability surface missing operator/admin split |
| `SSOT-I18N-001` | locale catalog missing catalog action or hardcode forbid |
| `SSOT-CONFIG-001` | config binding missing config-source/override action or literal forbid |
| `SSOT-LOCK-001` | standards-lock document invalid or allows automatic merge |
| `SSOT-STALE-001` | standards-lock entry behind the upstream revision, version or digest |

## Examples

`examples/invalid/missing-reason.ssot.json` must fail with `SSOT-REASON-001`.
