# Harness Design

PaperPresenter Lite should be a thin harness around Codex/GPT capability.

The repository should avoid accumulating custom intelligence that competes with
the model. Instead, it should make local Codex work easier, safer, and more
reproducible.

## Responsibilities

The harness owns:

- PDF validation and page rendering.
- Stable file layout for one run.
- Small schemas for rendered pages, visual assets, analysis, slides, and decks.
- Serialization of intermediate artifacts.
- Deterministic PPTX rendering from `DeckSpec`.
- Validation that model output references real assets.
- Human-editable JSON handoff points.

The model owns:

- Identifying important figures, tables, and regions.
- Deciding whether a crop is safe or whether full-page fallback is better.
- Understanding the paper's contribution.
- Planning the group-meeting narrative.
- Choosing which visual supports each slide.
- Writing slide bullets and speaker intent.

## Provider Boundary

The harness should depend on provider interfaces, not hard-coded model logic.

The primary model entrypoint is the local Codex CLI:

```bash
codex exec --image <page.png> --output-schema <schema.json> <prompt>
```

This keeps the project coupled to Codex capability rather than a direct SDK
implementation. As Codex and the underlying GPT models improve, the harness can
benefit without rewriting its core.

Initial provider boundaries:

- `VisualInventoryProvider`: rendered pages -> `VisualAsset[]`
- `DeckPlanner`: metadata + text + visual assets -> `DeckSpec`

Fallback providers exist only to keep local tests and demos runnable. They must
label their output as fallback or low confidence.

## What To Avoid

Avoid adding:

- large caption regex systems as primary extraction logic
- paper-specific templates
- complex scoring systems for visual importance
- multiple prompt versions before a real failure demands it
- hidden cleanup that removes model-facing artifacts
- silent repairs that mask bad model output

## Desired Failure Mode

When uncertain, the harness should produce a reviewable artifact with explicit
uncertainty rather than a polished but wrong slide.

Good failure:

- `VisualAsset.extraction_status = "fallback_full_page"`
- low confidence
- source page included
- reviewer can inspect the original page

Bad failure:

- half-cropped figure
- no source page
- no warning
- slide looks finished but evidence is wrong
