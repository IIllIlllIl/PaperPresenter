# Reuse Inventory

This document records which parts of the current repository should be reused for
PaperPresenter Lite.

## Keep As Reference

These assets are useful, but should not dictate the new architecture.

- `papers/`
  - Useful benchmark PDFs for regression checks.
  - Keep a small curated set for Lite acceptance testing.

- `src/generation/pptx_exporter.py`
  - Useful examples for `python-pptx` sizing, image insertion, and caption
    rendering.
  - Do not keep the current hard-coded layout system as the only renderer.

- `src/generation/ppt_generator.py`
  - Useful Markdown generation reference.
  - Keep the idea of a reviewable intermediate format.

- `src/planning/models.py`
  - Useful dataclass style and basic concepts such as `Visual`, `SlideTopic`,
    and `SlidePlan`.
  - Replace or simplify schemas for Lite.

- Prompt files under `src/prompts/`
  - Useful wording for PhD/postdoc group meeting expectations.
  - Consolidate into one or two Lite prompts.

- Tests under `tests/`
  - Useful examples of expected behavior.
  - Do not assume current tests represent the production pipeline correctly.

## Adapt

These components contain reusable ideas but need redesign.

- `src/parser/visual_extractor.py`
  - Has a better conceptual model than the older image extractor: figures and
    tables are represented as visual assets.
  - Its caption/region heuristics should become fallback logic, not the primary
    method.

- `src/analysis/multimodal_analyzer.py`
  - The idea is aligned with Lite: analyze visuals and text together.
  - It should be simplified around GPT-5 structured outputs and moved earlier in
    the pipeline.

- `src/planning/visual_slide_planner.py`
  - The planner already accepts visuals.
  - Current production pipeline passes an empty visual list, so this should be
    rebuilt as a first-class path.

- `src/core/pipeline.py`
  - Useful as a list of old stages and failure modes.
  - Do not preserve the current stage order.

## Freeze

These pieces should remain available but should not be extended during Lite
development.

- Citation analysis modules.
- Cache manager and cleanup scripts.
- Multiple legacy prompt versions.
- Manual test scripts under `src/tools/manual_tests/`.
- Phase reports and historical architecture reports under `docs/`.

## Remove Or Archive Later

These should be candidates for removal after the Lite baseline is running.

- Duplicate visual extraction paths:
  - `src/parser/pdf_image_extractor.py`
  - `src/parser/visual_extractor.py`
- Legacy slide planner files already deleted or superseded.
- Stale generated outputs under `outputs/`.
- Agent worktree directories under `.claude/worktrees/`.
- Documentation that describes abandoned pipeline phases.

## Known Current Repository Issues

- `git status` can fail unless nested `.claude/worktrees/` directories are
  ignored, because old agent worktrees contain broken `.git` pointers.
- The main pipeline plans slides before extracting figures.
- The main pipeline calls the visual slide planner with `visuals=[]`.
- The visual extractor covered by tests is not the extractor used in the main
  pipeline.
- PPTX layout is mostly hard-coded and does not fully honor slide layout intent.
- The repository has more process documentation than active product guidance.

## Lite Baseline Decision

The old project should be treated as a source of examples and test material.
PaperPresenter Lite should start with a new minimal pipeline rather than refactoring
the current pipeline in place.
