# STANDARDS-LOCK

## Purpose

A standards lock is the single source of truth for which Wellmanifest
standards this pack depends on: each pin records the standard id, version,
repository, git revision, and the digests of the contracts the pack relies
on. Drift is never silent, and merge is never automatic.

## Syntax

```bash
PYTHONPATH=src python3 -m ssot standards examples/standards-lock.adopter.json
PYTHONPATH=src python3 -m ssot standards examples/standards-lock.adopter.json --upstream dsl-manifest.json
PYTHONPATH=src python3 -m ssot standards examples/standards-lock.stale.json --upstream dsl-manifest.json --format json
```

## Inputs

A `wellmanifest.standards-lock/v1` document, either standalone (an adopter's
`standards-lock.json`) or embedded as the `standardsLock` block of a
`dsl-manifest.json`. `--upstream` supplies the current authoritative pin set
for drift detection.

## Outputs

`ok`, or a list of findings. Structural problems are `SSOT-LOCK-001`; a pin
that no longer matches upstream is `SSOT-STALE-001`.

## The lock is the SSOT

A pack's `standardsLock` is the canonical statement of its standard
dependencies. Do not keep a second registry of pins: the manifest
`standardsLock` block and an adopter's `standards-lock.json` describe the same
`wellmanifest.standards-lock/v1` document type, and the validator reads either
shape.

## Migration path for adopters

When an upstream standard releases a compatible (or breaking) version:

1. **Detect.** Run `ssot standards <lock> --upstream <upstream>`; a stale
   revision, version, or contract digest becomes `SSOT-STALE-001`, so drift is
   never silently ignored.
2. **Review.** Read the upstream changelog and any migration notes recorded in
   the lock's `migrations` array.
3. **Pin.** Bump the entry `version`, `revision`, and each contract `digest`
   to the new published values.
4. **Conform.** Re-run the pack's conformance commands
   (`PYTHONPATH=src python3 -m unittest discover -s tests`, and the upstream
   `dsl_check` gate when `wellmanifest/dsl` is available locally).
5. **Review.** A compatible release may open a pull request; a breaking
   release opens a planfile ticket. Merge only after a trusted validator or a
   human approves. The `updatePolicy.merge` field only ever accepts
   `trusted-validator` or `manual`; automatic merge is forbidden.

## Errors

| Code | When |
| --- | --- |
| `SSOT-LOCK-001` | bad schema, entry, revision, digest, migration, or a merge policy that would allow automatic merge |
| `SSOT-STALE-001` | an entry's revision, version, or contract digest no longer matches upstream |

## Examples

`examples/standards-lock.adopter.json` is a current, valid adopter lock.
`examples/standards-lock.stale.json` pins an outdated revision and digest and
is flagged by drift detection against `dsl-manifest.json`.
