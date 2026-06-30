# PaperPresenter

AI-powered academic paper analysis and presentation generation.

PaperPresenter reads a PDF paper, analyzes its content, plans a presentation structure, generates slide markdown, exports a PPTX, and can optionally attach citation analysis.

## Quick Links

- [Quick Start](#quick-start)
- [Documentation Center](docs/README.md)
- [Developer Guide](CLAUDE.md)

## Core Capabilities

- Parse PDF text, metadata, and structured sections
- Run AI analysis to extract problem, method, results, pros/cons, and conclusions
- Generate a structured slide plan and narrative
- Export the final presentation as `.pptx`
- Preserve or clean intermediate artifacts for debugging
- Optionally include citation analysis in the generated presentation

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Then set your API key in `.env`:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

Or export it in your shell:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

## Quick Start

### Recommended: full pipeline

```bash
python -m src.cli.main pipeline --paper papers/example.pdf
```

`src/cli/main.py` is the canonical CLI implementation.

Useful variants:

```bash
# Keep intermediate files for debugging
python -m src.cli.main pipeline --paper papers/example.pdf --no-clean

# Include citation analysis
python -m src.cli.main pipeline --paper papers/example.pdf --include-citations
```

### Other useful commands

```bash
# Cache statistics
python -m src.cli.main stats

# Clean expired cache
python -m src.cli.main cleanup
```

## Pipeline Overview

The recommended `pipeline` command runs the current end-to-end flow in `src/core/pipeline.py` through `src/cli/main.py`:

1. Parse PDF
2. Extract structured sections
3. Run AI analysis
4. Optional citation analysis
5. Generate slide plan
6. Generate narrative
7. Generate slides markdown
8. Export PPTX
9. Generate presentation script

Implementation note: the pipeline displays citation analysis as stage `3.5`, so the visible stage sequence is `1, 2, 3, 3.5, 4, 5, 6, 7, 8`.

## Output Structure

```text
outputs/
├── slides/
│   └── {paper_name}.pptx
└── intermediates/
    ├── markdown/
    │   └── {paper_name}.md
    ├── plans/
    │   └── {paper_name}_plan.json
    ├── scripts/
    │   └── {paper_name}_presentation_script.md
    ├── images/
    └── citations/
```

Notes:

- Final deliverables are stored in `outputs/slides/`
- Intermediate artifacts are stored in `outputs/intermediates/`
- Successful pipeline runs clean intermediates by default; use `--no-clean` to keep them

## Default Presentation Structure

`src/planning/slide_planner.py` currently uses a structured 10-slide template by default:

1. Title
2. Why Human-in-the-Loop?
3. Research Questions
4. HULA Framework Overview
5. Workflow: Human Feedback Integration
6. Three-Stage Evaluation
7. Offline & Online Results
8. User Survey Results
9. Discussion: Pros & Cons
10. Conclusions & Future Work

## Legacy `process` Command

`python -m src.cli.main process ...` still exists for the older lightweight flow. For complete presentation generation, use `pipeline`.

## Documentation

See the active docs under `docs/`:

- [Documentation Center](docs/README.md)
- [Pipeline Implementation](docs/architecture/PIPELINE_IMPLEMENTATION.md)
- [Data Flow](docs/architecture/DATA_FLOW.md)
- [Quick Reference](docs/architecture/DATA_FLOW_QUICK_REFERENCE.md)

## Testing

```bash
pytest
```
