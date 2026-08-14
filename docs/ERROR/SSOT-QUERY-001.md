# SSOT-QUERY-001

## Meaning

A `query_namespace` decision is missing `scope_query_keys` or does not forbid
`leak_query_across_modules`.

## Cause

Shell, hardware, or result keys from one module were treated as global URL
state. A later page compiled them as URI-DSL extensions and rejected the
whole request (`unknownPolicy=reject`).

## Resolution

Namespace keys to the owning module. Strip foreign keys on navigate and on
arrival. Keep `COMMAND`/`ADDRESS` on hardware routes only.
