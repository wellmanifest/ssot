# SSOT-FLEET-001

## Meaning

An `inventory_vs_runtime` decision does not forbid overwriting a dirty tree
or counting a LAN scan as a connected agent.

## Cause

Discovery, websocket presence, and applied git revision were collapsed into
one "online" bit. A fail-closed updater then tried to wipe live hardware
work to match a pin.

## Resolution

Keep three truths: scan, connected agent, applied revision. Refuse apply on
a dirty working tree (`wellmanifest.deployment` `deploy-source-exact`).
