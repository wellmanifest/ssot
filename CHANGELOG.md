# Changelog

All notable changes to this project are documented in this file.

## [0.2.0-dev]

- Add `config_binding` kind (`bind_to_config_source`, `declare_env_override`,
  forbid `hardcode_deployment_value`) and `SSOT-CONFIG-001`: closes the gap
  that no pack ruled on hardcoded hosts, ports, URLs or paths in code and
  grammar. Example `examples/willmux-config-binding.interview.json`.
- `docs/VALIDATE.md` and `docs/SSOT.md` now list `SSOT-LOCK-001` and
  `SSOT-STALE-001`, which the validator already emitted.
- Encode maskservice runtime lessons as SSOT kinds: `query_namespace`,
  `served_artifact`, `inventory_vs_runtime`, `capability_surface`,
  `locale_catalog`, with mapping in `docs/MASKSERVICE.md`.

## [0.1.0-dev]

- Bootstrap the SSOT domain pack on wellmanifest/dsl: interview, classifier,
  decision schema, text projection, and the c2004 method example.
