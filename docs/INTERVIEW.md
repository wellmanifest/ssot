# INTERVIEW

## Purpose

Ask the questions that classify a duplication pair before any delete, merge,
or "fix debt" action.

## Syntax

```bash
PYTHONPATH=src python3 -m ssot interview
PYTHONPATH=src python3 -m ssot interview --answers examples/c2004-backend-shared-py.interview.json --format dsl
PYTHONPATH=src python3 -m ssot questions
```

## Inputs

Interactive stdin answers, or a JSON document conforming to
`schemas/ssot-interview.schema.json`. The question catalog is
`questions/interview.json`.

## Outputs

A canonical `wellmanifest.ssot/decision/v1` document (`--format json`) or its
text projection (`--format dsl`).

## Errors

Invalid answers fail with `SSOT-KIND-001` or `SSOT-TREE-001`. The command
does not treat analyzer output as debt.

## Examples

```bash
PYTHONPATH=src python3 -m ssot interview --answers examples/analyzer-noise.interview.json --format dsl
```

That interview must emit `KIND same_file_noise` and a clarifying `QUESTION`.

Runtime interviews (`query_namespace`, `served_artifact`,
`inventory_vs_runtime`, `capability_surface`, `locale_catalog`) live next
to the c2004 fixtures.
