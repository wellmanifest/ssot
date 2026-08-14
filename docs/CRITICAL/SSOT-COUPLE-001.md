# SSOT-COUPLE-001

## Risk

A standalone product is coupled to another monorepo only so it can import
an SSOT package. That creates a hidden runtime and release dependency.

## Detection

`consumer_can_import` is false, or policy is missing
`couple_standalone_to_foreign_monorepo`. The validator requires that forbid
on every pin policy.

## Remediation

Vendor the SSOT bytes (or a generated mirror) and gate drift with a parity
or pin test. Do not add a live import from the foreign monorepo.

## Verification

`ssot validate` passes, the decision includes `vendor_and_gate_drift` when
import is impossible, and no consumer build depends on the other monorepo
checkout.
