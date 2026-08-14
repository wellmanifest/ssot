DOCUMENT SSOT
ID c2004.ssot
VERSION 0.1.0
SCHEMA wellmanifest.ssot/decision/v1
PURPOSE "Reusable SSOT decisions distilled from the c2004 vs oqlos dual-checkout and frontend-services parity review. Method, not c2004-specific code."

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
