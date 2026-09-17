# wellmanifest/ssot

Warstwa do tworzenia SSOT (single source of truth) w dowolnym kontekście:
najpierw wywiad, potem decyzja w DSL.

A generic SSOT creation layer. It interviews the user, classifies duplication,
and emits a propose-only DSL document. It does not edit, delete, or merge code.

This repository is a **domain pack** on [`wellmanifest/dsl`](https://github.com/wellmanifest/dsl).
It does not invent a competing language. Canonical documents are JSON AST
(`wellmanifest.ssot/decision/v1`). The `DOCUMENT SSOT` text form is a
projection.

## Why this exists

Duplication analyzers (code2llm TOON, redup, jscpd) are noisy. Dual git
submodule checkouts look like forks. Vendored copies look like debt. Some
twins must stay identical; others diverge by design. An SSOT process must
**ask** before it treats a report as work.

Lessons encoded here (method, not product-specific code):

1. Dual checkouts of the same package are **generated mirrors**. Edit
   upstream, bump the pin; do not delete either tree.
2. Real SSOT work is the remaining twins: vendored copies that must stay
   identical (parity tests) versus allowed-divergent copies (document
   `KNOWN_DIVERGENT`).
3. Indexes are noisy (CC on constants, docs as god modules). Interview first.
4. Pattern: SSOT package + vendored copy + parity test + documented reasons.
5. Hardware-style facade: re-export the canonical module
   (`oqlos.hardware.client`).
6. Do not couple a standalone product to another monorepo just to import
   SSOT; vendor and gate drift instead.
7. Query keys belong to one module (`query_namespace`). Leftover
   `COMMAND`/`ADDRESS` must not fail a foreign page.
8. Served `dist` is the live SSOT when there is no HMR.
9. LAN discovery, connected agents, and applied revision are three truths.
10. Visible Edit is not a write grant. Locale catalog owns operator copy.

## Interview → DSL

```text
questions/interview.json
        │  typed answers (wellmanifest.ssot/interview/v1)
        ▼
   ssot classify          ← deterministic, not an LLM
        │  JSON AST (wellmanifest.ssot/decision/v1)
        ▼
   ssot suggest           ← DOCUMENT SSOT projection
        │
        ▼
   ssot validate          ← fail closed
```

`wellmanifest/dsl` owns the kernel (`dsl-manifest.json` contract,
`dsl_check`, effect/LLM rules). This pack owns SSOT kinds, the
questionnaire, and the classifier. Effect model: **propose-only**.

## CLI

```bash
PYTHONPATH=src python3 -m ssot questions
PYTHONPATH=src python3 -m ssot interview --answers examples/c2004-backend-shared-py.interview.json --format dsl
PYTHONPATH=src python3 -m ssot classify examples/c2004-frontend-services.interview.json
PYTHONPATH=src python3 -m ssot suggest examples/c2004.ssot.json
PYTHONPATH=src python3 -m ssot validate examples/c2004.ssot.json
PYTHONPATH=src python3 -m ssot standards examples/standards-lock.adopter.json
PYTHONPATH=src python3 -m ssot standards examples/standards-lock.adopter.json --upstream dsl-manifest.json
PYTHONPATH=src python3 -m unittest discover -s tests
```

Interactive interview (no `--answers`) reads stdin.

## Kinds

| Kind | Meaning | Default next action |
| --- | --- | --- |
| `generated_mirror` | Same upstream, two checkouts | Edit upstream, bump pin, keep both trees |
| `vendored_copy` | Copy that must stay identical | Parity test; vendor + gate if import would couple repos |
| `facade` | Thin re-export of the canonical module | Keep the facade; do not fork logic |
| `allowed_divergence` | Different protocol or API by design | Document `KNOWN_DIVERGENT` |
| `real_fork` | Independent evolution | Choose a canonical owner |
| `same_file_noise` | Analyzer hit, relationship unknown | Ask clarifying questions |
| `query_namespace` | URL/URI keys owned by one module | Scope keys; strip on navigate and arrival |
| `served_artifact` | Live UI is a built artifact | Rebuild, reload, hard refresh |
| `inventory_vs_runtime` | Scan ≠ agent ≠ applied pin | Refuse dirty overwrite |
| `capability_surface` | Chrome ≠ POA grant | Test operator and admin separately |
| `locale_catalog` | Operator copy lives in catalog | Do not hardcode UI locale |
| `pin_policy` | Document-level pin rule | Always present on the decision document |

## Example: c2004

`examples/c2004.ssot.json` records decisions from the c2004 / oqlos /
maskservice review:

- `packages/backend-shared-py` vs `extern/oqlos/packages/backend-shared-py`
  → `generated_mirror`
- frontend-services twins gated by
  `tests/test_frontend_services_oqlos_parity.py` → `vendored_copy`
- `parentUrlBridge.js` → `allowed_divergence` (different postMessage
  protocols)
- `packages/hardware-client-py` → `facade` over `oqlos.hardware.client`
- coil query leak into process-capabilities → `query_namespace`
- nginx `frontend/dist` vs source → `served_artifact`
- fleet scan vs agent vs dirty tree → `inventory_vs_runtime`
- Connect-ID Edit vs ACL → `capability_surface`
- hardcoded Polish heading → `locale_catalog`

Commercial portals (informative): `plans.json` and brand CSS/token maps are
`facade` (or `locale_catalog`) over product HOMEs `subactor/offer` and
`subactor/brand`. Policy sales profiles are not a second price SSOT. See
`docs/CLASSIFY.md` and standards pointers `wellmanifest/offer`,
`wellmanifest/brand`.

See `docs/MASKSERVICE.md`. Interview fixtures that regenerate each kind live
next to that file.

## Layout

```text
questions/     questionnaire catalog
schemas/       interview, decision, and standards-lock JSON Schemas
docs/          command, error, and critical pages
examples/      c2004 sample + standards-lock adopter/stale fixtures
src/ssot.py    interview, classify, suggest, validate, standards
tests/         deterministic checks
dsl-manifest.json   wellmanifest.dsl/manifest/v1 for this pack
docs/MASKSERVICE.md live mapping from maskservice lessons
```

## Related

- [`wellmanifest/dsl`](https://github.com/wellmanifest/dsl) — kernel and
  conformance
- [`wellmanifest/modularity`](https://github.com/wellmanifest/modularity) —
  composing independently owned modules
- [`wellmanifest/new-project`](https://github.com/wellmanifest/new-project) —
  repository governance (optional later adoption)
