# CLASSIFY

## Purpose

Deterministically map typed interview answers to an SSOT kind and proposed
actions. Classification is ordered: known relationships first, analyzer noise
last.

## Syntax

```bash
PYTHONPATH=src python3 -m ssot classify examples/c2004-backend-shared-py.interview.json
PYTHONPATH=src python3 -m ssot classify examples/c2004-backend-shared-py.interview.json --format dsl
```

## Inputs

A valid `wellmanifest.ssot/interview/v1` document.

## Outputs

One decision document. Kinds:

| Condition | Kind | Default actions |
| --- | --- | --- |
| Same git remote and same pin, or stated mirror | `generated_mirror` | edit upstream, bump pin, keep both trees |
| Facade re-export | `facade` | keep facade, do not fork logic |
| Vendored and must stay identical | `vendored_copy` | parity test; vendor + gate if import would couple repos |
| Different protocol by design | `allowed_divergence` | document `KNOWN_DIVERGENT` reason |
| Independent evolution | `real_fork` | choose a canonical owner |
| Stated query/URI key ownership | `query_namespace` | scope keys; forbid cross-module leak |
| Stated source vs served dist | `served_artifact` | rebuild served artifact; do not treat source as live |
| Stated discovery vs agent vs pin | `inventory_vs_runtime` | do not count scan as connected; refuse dirty overwrite |
| Stated chrome vs grant | `capability_surface` | test operator and admin separately |
| Stated UI copy ownership | `locale_catalog` | use locale catalog; forbid hardcoded copy |
| Analyzer noise, relationship unknown | `same_file_noise` | ask questions; do not treat as debt |

Document-level `POLICY pin` is always emitted.

## Errors

Interview schema or path errors: `SSOT-KIND-001`, `SSOT-TREE-001`.

## Examples

`examples/c2004-frontend-services.interview.json` classifies as
`vendored_copy` with `vendor_and_gate_drift` because the consumer cannot
import the SSOT package.

Stated `query_namespace`, `served_artifact`, `inventory_vs_runtime`,
`capability_surface`, and `locale_catalog` win over an inferred
`generated_mirror`.
