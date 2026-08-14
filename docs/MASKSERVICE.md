# Maskservice → wellmanifest/ssot

Method mapping from live maskservice work. This pack stays generic: the
c2004 paths below are illustrations, not a second product repository.

| Live lesson | SSOT kind | Maps to |
| --- | --- | --- |
| Dual `backend-shared-py` checkouts | `generated_mirror` | pin + bump; do not delete either tree |
| `packages/frontend-services` vs `extern/oqlos` | `vendored_copy` | parity test; do not couple monorepos |
| `parentUrlBridge` protocols | `allowed_divergence` | `KNOWN_DIVERGENT` reason |
| `hardware-client-py` re-export | `facade` | keep thin import |
| Coil `COMMAND`/`ADDRESS` leaked into process-capabilities; URI DSL rejected unknown keys | `query_namespace` | `wellmanifest.dsl` / POA `unknownPolicy=reject`; strip on navigate and arrival |
| Source edited, nginx still served old `frontend/dist` (no HMR) | `served_artifact` | rebuild, reload, hard refresh; TestQL WAIT follows the bundle |
| LAN scan ≠ connected agent; updater refused dirty BoardNet tree | `inventory_vs_runtime` | `wellmanifest.deployment` `deploy-source-exact`; do not overwrite live hardware work |
| Connect-ID Edit visible; operator API write 403/429 | `capability_surface` | POA capability ≠ chrome; TestQL operator and admin separately |
| Heading `Uprawnienia procesów (POA)` hardcoded; `lang=en` still Polish | `locale_catalog` | catalog is SSOT for operator copy |

## TestQL implications

1. Assert against the **served** artifact, not the editor buffer.
2. After rebuild, increase WAIT until module selectors exist.
3. Do not treat a visible Edit as a passing write for `operator`.
4. Cover `system`/`admin` writes and `operator` list/read as different
   scenarios.
5. A leftover `error_code` or hardware query key on a foreign route is a
   `query_namespace` defect, not a flaky navigation.

## What this pack will not do

It does not authorize deleting BoardNet dirty files, merging `update/main`,
or opening pull requests. Classify, then propose.
