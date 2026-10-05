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
| Stated deployment value (host, port, URL, path, model id) with one config source | `config_binding` | bind consumers to the source; declare one env override; forbid literal copies |
| Portal commercial sheet mirrors product offer | `facade` (or `generated_mirror`) | keep facade; bump `subactor/offer` binding first; forbid second price SSOT |
| Portal brand tokens/copy mirror product brand | `facade` / `locale_catalog` | keep facade; bump `subactor/brand` first; forbid second brand SSOT |
| Analyzer noise, relationship unknown | `same_file_noise` | ask questions; do not treat as debt |

Document-level `POLICY pin` is always emitted.

### Commercial and brand product packs

When classifying Subactor (or similar) portal files:

- `plans.json` / checkout price tables → facade of `subactor/offer` (not of
  `wellmanifest/policy-dsl`, which owns promo decisions only).
- Brand CSS tokens, prefer/forbid vocabulary, public plan names → facade or
  locale projection of `subactor/brand`.
- Do not classify a portal ticket rewrite as `real_fork` of prices or brand;
  require an integration bump of the product HOME pack first.

## Errors

Interview schema or path errors: `SSOT-KIND-001`, `SSOT-TREE-001`.

## Examples

`examples/c2004-frontend-services.interview.json` classifies as
`vendored_copy` with `vendor_and_gate_drift` because the consumer cannot
import the SSOT package.

Stated `query_namespace`, `served_artifact`, `inventory_vs_runtime`,
`capability_surface`, and `locale_catalog` win over an inferred
`generated_mirror`.
