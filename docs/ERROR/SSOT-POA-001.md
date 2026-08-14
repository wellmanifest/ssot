# SSOT-POA-001

## Meaning

A `capability_surface` decision is missing
`test_operator_and_admin_separately` or does not forbid
`treat_visible_edit_as_authorized`.

## Cause

Visible chrome (Edit, list, scanner) was treated as a write grant. Operator
sessions then failed API writes with 403/429 while admin/system succeeded.

## Resolution

Test operator and admin as separate POA capabilities. A visible control is
not authority. Record expected 403/429 for the role that lacks the write
capability.
