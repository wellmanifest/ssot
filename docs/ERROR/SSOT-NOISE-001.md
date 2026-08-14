# SSOT-NOISE-001

## Meaning

Analyzer output was treated as debt, or a `same_file_noise` decision has no
clarifying questions.

## Cause

code2llm TOON, redup, or jscpd flagged constants, docs, generated files, or
same-file fuzzy matches. The process skipped the interview.

## Resolution

Run `ssot interview`. Confirm with a human which pairs are real debt. Dual
submodule checkouts are usually `generated_mirror`, not debt.
