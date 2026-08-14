DOCUMENT SSOT
ID c2004.ssot
VERSION 0.2.0
SCHEMA wellmanifest.ssot/decision/v1
PURPOSE "Reusable SSOT decisions from maskservice: dual-checkout, vendored parity, query namespaces, served dist, fleet inventory vs runtime, capability chrome, locale catalog."

CONTEXT
  SUBJECT c2004.ssot
  LANGUAGE python
  LANGUAGE javascript
  LANGUAGE typescript
  PACKAGING git-submodule
  PACKAGING npm
  PACKAGING vendored-copy
  PACKAGING facade-reexport
  ANALYZER code2llm-toon present=true treat_as_debt=false

POLICY pin
  EDIT upstream
  ON_CHANGE bump_pin
  FORBID delete_generated_mirror
  FORBID treat_analyzer_as_debt
  FORBID couple_standalone_to_foreign_monorepo
  FORBID fork_logic_into_consumer

DECISION c2004.backend-shared-py
  KIND generated_mirror
  CANONICAL github:oqlos/backend-shared-py
  CANONICAL_PATH packages/backend-shared-py
  TREE packages/backend-shared-py
  TREE extern/oqlos/packages/backend-shared-py
  RATIONALE "Dual git-submodule checkouts of the same package are generated deployment mirrors, not forks. redup/code2llm will report exact copies; that is expected. Edit upstream backend-shared-py and bump the pin. Do not delete either tree without redesigning oqlos packaging."
  ACTION edit_upstream github:oqlos/backend-shared-py
  ACTION bump_pin c2004
  ACTION keep_both_checkouts
  FORBID delete_either_tree
  FORBID delete_generated_mirror

DECISION c2004.frontend-services-parity
  KIND vendored_copy
  CANONICAL packages/frontend-services
  CANONICAL_PATH packages/frontend-services
  TREE packages/frontend-services/src/wsClient.js
  TREE extern/oqlos/frontend/src/api/wsClient.js
  TREE packages/frontend-services/src/designRem.js
  TREE extern/oqlos/frontend/src/utils/designRem.js
  TREE packages/frontend-services/src/hardware-api-retry.js
  TREE extern/oqlos/frontend/src/api/hardware-api-retry.js
  TREE packages/hardware-client-ts/src/index.ts
  TREE extern/oqlos/frontend/vendor/hardware-client/index.ts
  GATE parity_test tests/test_frontend_services_oqlos_parity.py
  RATIONALE "extern/oqlos cannot import across the repository boundary, so it carries vendored copies. Identical pairs must stay byte-identical. A standalone product must vendor and gate drift instead of coupling to another monorepo just to import SSOT."
  ACTION keep_parity_test tests/test_frontend_services_oqlos_parity.py
  ACTION vendor_and_gate_drift
  FORBID couple_standalone_to_foreign_monorepo

DECISION c2004.parent-url-bridge
  KIND allowed_divergence
  CANONICAL packages/frontend-services/src/parentUrlBridge.js
  CANONICAL_PATH packages/frontend-services/src/parentUrlBridge.js
  TREE packages/frontend-services/src/parentUrlBridge.js
  TREE extern/oqlos/frontend/src/utils/parentUrlBridge.js
  REASON "Different postMessage protocols by design; each copy has its own host listener. Sharing one message type would cross-talk."
  RATIONALE "jscpd reports clones; the remaining review work is actionable twins versus allowed-divergent copies. parentUrlBridge is the latter."
  ACTION document_known_divergent

DECISION c2004.hardware-client-facade
  KIND facade
  CANONICAL oqlos.hardware.client
  MODULE oqlos.hardware.client
  TREE packages/hardware-client-py
  TREE oqlos/oqlos/hardware/client
  FACADE packages/hardware-client-py
  RATIONALE "The hardware client facade re-exports the canonical oqlos.hardware.client implementation. Do not copy tic249_* or other client logic into the consumer."
  ACTION keep_facade_reexport_canonical oqlos.hardware.client
  FORBID fork_logic_into_consumer

DECISION c2004.query-namespace
  KIND query_namespace
  CANONICAL frontend/src/services/uri-query-dsl.ts
  CANONICAL_PATH frontend/src/services/uri-query-dsl.ts
  TREE frontend/src/services/shell-routing.service.ts
  TREE frontend/src/services/uri-query-dsl.ts
  TREE connect-config/frontend/src/modules/connect-config/pages/connect-config-process-capabilities.page.ts
  RATIONALE "Hardware COMMAND/ADDRESS keys must not leak into process-capability URI DSL. wellmanifest.dsl unknownPolicy=reject; strip on navigate and on arrival."
  ACTION scope_query_keys frontend/src/services/uri-query-dsl.ts
  FORBID leak_query_across_modules

DECISION c2004.served-artifact
  KIND served_artifact
  CANONICAL frontend/dist
  CANONICAL_PATH frontend/dist
  TREE frontend/src
  TREE frontend/dist
  TREE scripts/build-frontend-if-stale.sh
  RATIONALE "nginx serves frontend/dist with no HMR. Source edits are not live until rebuild, reload, and a hard refresh. TestQL WAIT must follow the served bundle, not the editor buffer."
  ACTION rebuild_served_artifact frontend/dist
  FORBID treat_source_as_served

DECISION c2004.inventory-vs-runtime
  KIND inventory_vs_runtime
  CANONICAL update/fleet_proxy
  CANONICAL_PATH update/fleet_proxy
  TREE update/fleet_proxy/discovery.py
  TREE update/fleet_proxy
  RATIONALE "LAN scan, connected websocket agents, and applied git revision are three truths. Fail-closed deploy must refuse a dirty tree (wellmanifest.deployment deploy-source-exact)."
  ACTION do_not_count_discovery_as_connected
  ACTION refuse_overwrite_dirty_tree
  FORBID count_lan_scan_as_connected_agent
  FORBID overwrite_dirty_working_tree

DECISION c2004.capability-surface
  KIND capability_surface
  CANONICAL testql-testing/scenarios/gui-connect-id.testql.toon.yaml
  CANONICAL_PATH testql-testing/scenarios/gui-connect-id.testql.toon.yaml
  TREE testql-testing/scenarios/gui-connect-id.testql.toon.yaml
  TREE connect-id/frontend
  RATIONALE "Visible Edit is chrome, not a write grant. Operator 403/429 on API writes while admin/system can mutate is expected. TestQL must cover both roles."
  ACTION test_operator_and_admin_separately
  FORBID treat_visible_edit_as_authorized

DECISION c2004.locale-catalog
  KIND locale_catalog
  CANONICAL frontend/src/i18n
  CANONICAL_PATH frontend/src/i18n
  TREE connect-config/frontend/src/modules/connect-config/pages/connect-config-process-capabilities.page.ts
  RATIONALE "Hardcoded Polish headings stay Polish when lang=en. Operator-facing copy belongs in the locale catalog, not page-local getContent() strings."
  ACTION use_locale_catalog frontend/src/i18n
  FORBID hardcode_ui_locale
