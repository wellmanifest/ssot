# SSOT-SERVE-001

## Meaning

A `served_artifact` decision is missing `rebuild_served_artifact` or does not
forbid `treat_source_as_served`.

## Cause

Editor source was treated as the live UI. A static `dist` behind nginx has
no HMR, so TestQL and operators still see the previous bundle.

## Resolution

Rebuild and reload the served artifact. Hard-refresh the browser. Wait for
selectors against the new bundle before claiming the fix.
