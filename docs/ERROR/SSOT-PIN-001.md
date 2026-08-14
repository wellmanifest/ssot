# SSOT-PIN-001

## Meaning

A generated mirror is missing pin policy, or the policy does not forbid
deleting a mirror tree.

## Cause

Someone proposed "deduping" by deleting `packages/X` or `extern/.../X` when
both are the same pinned checkout.

## Resolution

Set `POLICY pin`, `EDIT upstream`, `ON_CHANGE bump_pin`, and
`FORBID delete_either_tree`. Keep both trees.
