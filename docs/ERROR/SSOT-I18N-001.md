# SSOT-I18N-001

## Meaning

A `locale_catalog` decision is missing `use_locale_catalog` or does not
forbid `hardcode_ui_locale`.

## Cause

Page-local strings (hardcoded headings, `getContent()` fallbacks) shipped as
the UI copy. `lang=en` still showed Polish.

## Resolution

Treat the locale catalog as SSOT for operator-facing copy. Replace
page-local headings with catalog keys.
