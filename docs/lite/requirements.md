# PaperPresenter Lite Requirements

## Objective

Build a lightweight tool that takes one academic paper PDF and produces a
presentation suitable for a PhD/postdoc group meeting.

The new system should prioritize faithful visual use, clear research narrative,
and simple maintainability over broad workflow automation.

## Primary User

The primary user is a researcher preparing a 10-15 slide internal group meeting
presentation from a single paper.

The expected audience is technically strong: PhD students, postdocs, and PIs.
Slides should support discussion, critique, and method/result inspection rather
than only high-level summary.

## Core Output

The tool should generate:

1. A reviewable slide plan in JSON or Markdown.
2. Extracted or rendered visual assets used by the deck.
3. A PowerPoint deck.
4. Optional speaker notes.

The slide plan is a required intermediate artifact. The deck should be
reproducible from the plan and assets.

## Target Slide Structure

Default deck length: 10-15 slides.

Expected flow:

1. Title and paper metadata.
2. Research context and motivation.
3. Problem statement.
4. Key idea or hypothesis.
5. Method or system overview.
6. Important design details.
7. Experimental setup.
8. Main quantitative results.
9. Ablation or deeper result analysis.
10. Qualitative examples or case studies, if available.
11. Strengths.
12. Limitations and threats to validity.
13. Discussion questions.
14. Conclusion.

The exact slide count may vary by paper, but the generated deck must preserve a
coherent academic narrative.

## Visual Requirements

Visual handling is the main quality target.

The system must:

- Identify figures and tables before slide planning.
- Use the model's visual understanding to select essential visuals.
- Preserve complete figures and tables whenever possible.
- Avoid half-cropped figures, missing panels, and accidental surrounding body
  text.
- Keep image crops linked to page number and source region.
- Support full-page fallback when precise cropping is uncertain.
- Prefer reviewable uncertainty over silent bad crops.

The system should not depend on a large hand-written set of caption and bounding
box heuristics as the primary visual extraction strategy.

## Proposed Lightweight Pipeline

1. PDF ingestion
   - Validate that the file exists and can be opened.
   - Extract basic metadata where available.

2. Page rendering
   - Render each page to a PNG or JPEG at a predictable DPI.
   - Store page images in a run-specific asset directory.

3. Vision inventory
   - Ask GPT-5 vision to inspect page images.
   - Return a structured inventory of figures, tables, diagrams, equations, and
     result-heavy regions.
   - Include page number, approximate bounding box, caption, importance, and
     suggested slide role.

4. Crop or region materialization
   - Crop only when the region is confident.
   - Otherwise keep a full-page or wide-region fallback.
   - Save all selected assets with stable IDs.

5. Paper understanding
   - Combine extracted text, metadata, and visual inventory.
   - Produce a concise research analysis aimed at group meeting discussion.

6. Slide planning
   - Produce structured slide JSON.
   - Assign visuals by asset ID.
   - Include layout intent and speaker intent for each slide.

7. Deck generation
   - Generate PPTX from structured slide JSON.
   - Keep layout rules simple and deterministic.

8. Review loop
   - Allow the user to edit the slide plan before final deck generation.

## Data Contracts

The implementation should define small stable schemas for:

- `PaperMetadata`
- `RenderedPage`
- `VisualAsset`
- `PaperAnalysis`
- `SlideSpec`
- `DeckSpec`

These schemas should be plain Python dataclasses or Pydantic models. Avoid
large inheritance hierarchies.

## Non-Goals

The first Lite version should not include:

- Citation analysis.
- Multi-paper comparison.
- Batch processing.
- Complex cache invalidation.
- Multiple presentation personas.
- A large prompt versioning framework.
- Automatic publication-quality graphic redesign.
- Full UI or web app.

These can be revisited after the vision-first deck path is reliable.

## Acceptance Criteria

For a small benchmark set of 3-5 papers:

1. The system produces a PPTX without manual code changes.
2. The slide plan includes at least 8 and at most 15 slides.
3. Essential figures and tables are selected before slide generation.
4. No selected visual is obviously half-cropped.
5. Every visual in the deck has a source page reference.
6. The deck includes method, experiments, results, limitations, and discussion.
7. A failed or uncertain crop is surfaced in the intermediate plan.

## Engineering Constraints

- Keep the main pipeline readable in one file or a small set of modules.
- Prefer structured model outputs over parsing free-form prose.
- Keep intermediate artifacts by default during development.
- Add tests around schemas, asset paths, and deck generation.
- Avoid adding heavy dependencies unless they replace meaningful complexity.
