# SSOT

## Purpose

Declare a single source of truth for duplicated or mirrored code. The document
classifies each pair and proposes next actions. It does not authorize edits.

## Syntax

Canonical form is UTF-8 JSON conforming to
`schemas/ssot-decision.schema.json`. The text projection starts with
`DOCUMENT SSOT` and is emitted by `ssot suggest`.

```text
DOCUMENT SSOT
ID <identifier>
VERSION <semver>
SCHEMA wellmanifest.ssot/decision/v1
CONTEXT
  SUBJECT <identifier>
  LANGUAGE <name>
  PACKAGING <kind>
  ANALYZER <kind> present=<bool> treat_as_debt=false
POLICY pin
  EDIT upstream
  ON_CHANGE bump_pin
  FORBID delete_generated_mirror
DECISION <identifier>
  KIND generated_mirror|vendored_copy|facade|allowed_divergence|real_fork|same_file_noise|query_namespace|served_artifact|inventory_vs_runtime|capability_surface|locale_catalog
  CANONICAL <ref>
  TREE <path>
  ACTION <name>
  FORBID <name>
```

## Inputs

A decision document or typed interview answers. Analyzer reports (code2llm
TOON, redup, jscpd) are evidence, not classifications.

## Outputs

A propose-only SSOT decision document and optional text DSL projection.

## Errors

See `docs/ERROR/` for `SSOT-KIND-001`, `SSOT-NOISE-001`, `SSOT-PIN-001`,
`SSOT-REASON-001`, `SSOT-TREE-001`, `SSOT-QUERY-001`, `SSOT-SERVE-001`,
`SSOT-FLEET-001`, `SSOT-POA-001`, and `SSOT-I18N-001`. Coupling a standalone
product to a foreign monorepo is `docs/CRITICAL/SSOT-COUPLE-001.md`.

## Examples

`examples/c2004.ssot.json` encodes the c2004 dual-checkout, vendored parity,
allowed-divergence, facade, query-namespace, served-artifact, fleet,
capability-surface, and locale-catalog patterns. Live mapping:
`docs/MASKSERVICE.md`.
