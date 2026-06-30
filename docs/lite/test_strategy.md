# Lite Test Strategy

This plan defines how to test PaperPresenter Lite without immediately running
expensive or slow real PPT generation through local Codex.

The purpose is to validate the harness contract first:

- stable PDF inputs
- page rendering metadata
- model-facing artifacts
- JSON schemas
- manifest structure
- deterministic renderer behavior in small unit tests

Real Codex-backed deck generation should come after these checks are stable.

## Test PDF Set

Local candidate PDFs in `papers/`:

| PDF | Pages | Size | Current role |
| --- | ---: | ---: | --- |
| `Human-In-the-Loop.pdf` | 11 | 2.84 MB | Tracked baseline PDF |
| `ChangeGuard.pdf` | 21 | 0.79 MB | Local candidate |
| `EquiBench.pdf` | 16 | 0.36 MB | Local candidate |
| `FeatBench.pdf` | 29 | 2.22 MB | Local candidate |
| `LLMs Love Python.pdf` | 12 | 0.79 MB | Local candidate |
| `Test_Intention_Guided_LLM-Based_Unit_Test_Generation.pdf` | 13 | 0.59 MB | Local candidate |
| `When Prompts Go Wrong.pdf` | 13 | 1.60 MB | Local candidate |
| `actual or the expected program behaviour.pdf` | 12 | 0.39 MB | Local candidate |

Only `Human-In-the-Loop.pdf` is currently tracked by Git. The other PDFs are
useful local benchmark candidates but should not be committed until we decide
which fixtures belong in the repository.

## Test Levels

### Level 0: Unit Tests

Goal: verify pure Python harness behavior without reading real PDFs or calling
Codex.

Covered now:

- `DeckSpec` JSON roundtrip
- bounding box validation
- fallback planner contract
- pipeline manifest creation with fake PDF reader/writer
- local Codex command construction with mocked subprocess
- Codex visual inventory materialization with mocked model output

Command:

```bash
python -m pytest tests/test_lite_models.py tests/test_lite_planner.py tests/test_lite_pipeline.py tests/test_local_codex.py tests/test_lite_codex_inventory.py
```

### Level 1: PDF Intake Smoke Tests

Goal: verify that selected PDFs can be opened and basic metadata can be read.

No PPTX generation. No Codex call.

Checks:

- file exists
- PyMuPDF can open it
- page count is greater than zero
- metadata extraction does not crash
- rendered output directory can be planned

Suggested future test file:

- `tests/test_lite_pdf_fixtures.py`

### Level 2: Page Rendering Smoke Tests

Goal: verify page rendering for the benchmark set without generating a deck.

No PPTX generation. No Codex call.

Checks:

- first page renders to PNG
- rendered dimensions are non-zero
- path handling works for filenames with spaces
- output paths remain under `outputs/lite/`

This level is useful for Windows compatibility because several candidate PDFs
have spaces or long filenames.

### Level 3: Manifest Contract Tests

Goal: verify that the harness produces model-facing artifacts.

Use fallback providers only.

Checks:

- `harness_manifest.json` exists
- manifest lists provider names
- manifest lists rendered page images
- manifest lists `deck_spec.json`
- manifest uses relative or workspace-local paths consistently

This can run in CI without Codex credentials.

### Level 4: Local Codex Visual Inventory Tests

Goal: evaluate Codex visual selection only.

Runs `--provider codex`, but does not evaluate full PPT quality.

Checks:

- Codex returns valid JSON matching `VISUAL_INVENTORY_SCHEMA`
- every returned visual references an existing source page
- every bbox is normalized and valid
- high-confidence visual crops are materialized
- uncertain visuals become full-page fallbacks

This level should be opt-in because it depends on local Codex auth, model
availability, and runtime cost.

Suggested marker:

```bash
python -m pytest -m codex
```

### Level 5: Full Deck Review Runs

Goal: inspect real generated decks.

This is intentionally not the first test level. Run it only after the visual
inventory and deck planner providers are stable.

Checks:

- deck opens
- slide count is between 8 and 15
- every visual slide has a source page
- no obvious half-cropped visual
- method, experiments, results, limitations, and discussion are present

This level should produce human-review artifacts, not just pass/fail results.

## Initial Benchmark Recommendation

Start with three PDFs:

1. `Human-In-the-Loop.pdf`: tracked baseline and existing visual tests.
2. `ChangeGuard.pdf`: longer paper, many pages, small file size.
3. `LLMs Love Python.pdf`: filename with spaces and likely familiar structure.

Add `FeatBench.pdf` later as a stress case because it is the longest local
candidate.

## Cross-Platform Concerns

The test set should intentionally include:

- filenames with spaces
- long filenames
- short papers and longer papers
- PDFs with missing metadata

Avoid shell-based test orchestration. Use Python and `pytest` so the same tests
can run on Windows, Linux, and macOS.

