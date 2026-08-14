# SSOT-REASON-001

## Meaning

An `allowed_divergence` decision has no `KNOWN_DIVERGENT` reason and no
pending question.

## Cause

Copies differ, but the reason was not written down. The next editor cannot
tell accident from design.

## Resolution

Add `REASON "..."` or a `QUESTION` that asks for the reason. The c2004
parentUrlBridge pair is the reference: different postMessage protocols by
design.
