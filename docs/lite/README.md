# PaperPresenter Lite Foundation

This folder defines the baseline for the next PaperPresenter development cycle.

The goal is to replace the current process-heavy Claude-era pipeline with a
smaller GPT-5 vision-first workflow:

1. Render PDF pages.
2. Let a vision-capable model identify important figures, tables, and page
   regions.
3. Produce a reviewable slide plan.
4. Generate a presentation deck from structured slide data.

The existing repository remains useful as a reference source, but new
development should treat this folder as the product and architecture baseline.

## Documents

- [Requirements](requirements.md): target behavior, scope, non-goals, and
  acceptance criteria.
- [Harness Design](harness_design.md): boundary between the thin harness and
  Codex/GPT model capability.
- [Reuse Inventory](reuse_inventory.md): what to keep, adapt, freeze, or remove
  from the current codebase.
