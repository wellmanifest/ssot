# SSOT-STALE-001

## Meaning

A standards-lock entry no longer matches the current upstream standard: its
revision, version, or contract digest is out of date.

## Cause

An upstream standard released a new compatible or breaking version, and the
adopter's pin was not bumped. Drift was about to become silent.

## Resolution

Follow the migration path in `docs/STANDARDS-LOCK.md`: review the upstream
changelog, bump `version`/`revision`/`digest`, re-run conformance, and merge
only after trusted-validator review. A compatible release may open a PR; a
breaking release opens a planfile ticket.
