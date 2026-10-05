# SSOT-CONFIG-001

## Meaning

A `config_binding` decision is missing `bind_to_config_source` or
`declare_env_override`, or does not forbid `hardcode_deployment_value`.

## Cause

A deployment value — host, port, URL, LAN address, absolute path, model id,
probe interval — was written as a literal in code, grammar, UI or tests in
addition to (or instead of) its configuration source. Every copy is a second
SSOT: moving the service, renaming a node or running on another machine
silently breaks the copies that were not edited.

Observed in `paxlet-com/willmux`: the FakturApp address `127.0.0.1:8085` was
declared in `catalog.yaml` and copied 23 times into `grammar.json` (two
copies), `willmux.html` and tests; a LAN address of one Ollama host was
written into self-improvement pipelines while a neighbouring function read
the same value from the environment.

## Resolution

1. Name the one configuration source (`CANONICAL`) — a catalog, a config
   module, an env-dsl document.
2. Make every consumer refer to the value by name (an app id, a config key)
   and resolve it at run time. Generated artefacts may embed it only when the
   build reads it from the source.
3. Declare exactly one override name per value and document it next to the
   value (for example `WILLMUX_APP_<ID>_URL`). This is an explicit last layer,
   consistent with `wellmanifest.env-dsl`; consumers do not scan ambient
   variables.
4. Add a regression gate that fails when the source's literal appears
   elsewhere.

Secrets are not deployment values: keep them out of literals and out of
config defaults entirely (`wellmanifest.secrets`, `SECRET-LEAK-001`).
Loopback defaults for a local developer service are allowed in the
configuration source only.
