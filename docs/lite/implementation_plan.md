# Lite Implementation Plan

This implementation starts with a local, deterministic skeleton. The first goal
is to make the new architecture runnable and reviewable before connecting a
vision model.

## Package Boundary

New code lives under `src/lite/` and does not modify the legacy pipeline.

Initial modules:

- `models.py`: small dataclass schemas for metadata, pages, visual assets,
  paper analysis, slides, and decks.
- `pdf_render.py`: PDF validation, metadata extraction, text extraction, and
  page rendering with PyMuPDF.
- `visual_inventory.py`: provider interface plus full-page fallback inventory.
- `planner.py`: deterministic initial deck planner.
- `deck_writer.py`: deterministic PPTX writer using `python-pptx`.
- `pipeline.py`: minimal orchestration from PDF to `deck_spec.json` and PPTX.
- `cli.py`: `python -m src.lite.cli <paper.pdf>`.

## Current Behavior

The first version renders pages and creates uncertain full-page visual assets.
This is intentional. It makes the pipeline usable without pretending that
heuristic crops are reliable.

Every fallback visual is marked with:

- `extraction_status = "fallback_full_page"`
- low confidence
- source page number
- a note that it should be replaced by GPT-5 vision-selected crops

## Next GPT-5 Integration Point

The first model-backed component should replace `FullPageFallbackInventory` with
a provider that:

1. Sends rendered page images to a vision-capable model.
2. Receives structured figure/table/page-region inventory.
3. Crops high-confidence regions.
4. Keeps full-page fallback regions when confidence is low.

The rest of the pipeline should continue to consume `VisualAsset` objects.

## Run Command

```bash
python -m src.lite.cli papers/ChangeGuard.pdf --output-dir outputs/lite
```

Expected artifacts:

- `outputs/lite/<paper>/pages/page_001.png`
- `outputs/lite/<paper>/deck_spec.json`
- `outputs/lite/<paper>/<paper>.pptx`

