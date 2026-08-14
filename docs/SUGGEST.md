# SUGGEST

## Purpose

Emit the text DSL projection of a validated decision document so agents and
humans can review the same facts without inventing a second language.

## Syntax

```bash
PYTHONPATH=src python3 -m ssot suggest examples/c2004.ssot.json
```

## Inputs

A canonical JSON decision document, or a `.dsl` / `DOCUMENT SSOT` text file.

## Outputs

The line-oriented projection. Canonical JSON remains the source of truth;
text is a projection declared in the DSL manifest.

## Errors

Validation failures are printed and the command exits 1. See `VALIDATE`.

## Examples

```bash
PYTHONPATH=src python3 -m ssot suggest examples/c2004.ssot.json | head
```
