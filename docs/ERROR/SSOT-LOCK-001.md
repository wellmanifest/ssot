# SSOT-LOCK-001

## Meaning

A standards-lock document is structurally invalid, or its update policy would
permit automatic merge.

## Cause

The lock is missing `schema`/`entries`, an entry has an invalid standard id,
version, repository, revision, or contract digest, or `updatePolicy.merge` is
not `trusted-validator`/`manual`.

## Resolution

Rewrite the lock to conform to `schemas/ssot-standards-lock.schema.json`. Keep
`updatePolicy.merge` as `trusted-validator` or `manual`; automatic merge is
forbidden without a trusted validator.
