"""Command line entrypoint for PaperPresenter Lite."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.lite.local_codex import LocalCodexRunner
from src.lite.pipeline import LitePipeline
from src.lite.visual_inventory import LocalCodexVisionInventory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Lite presentation from one paper PDF.")
    parser.add_argument("pdf", type=Path, help="Path to the input paper PDF")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/lite"), help="Output directory")
    parser.add_argument("--provider", choices=["fallback", "codex"], default="fallback", help="Model provider")
    parser.add_argument("--model", default=None, help="Optional Codex model override")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    inventory_provider = None
    if args.provider == "codex":
        runner = LocalCodexRunner(model=args.model, cwd=Path.cwd())
        inventory_provider = LocalCodexVisionInventory(runner=runner)
    result = LitePipeline(inventory_provider=inventory_provider).run(args.pdf, args.output_dir)
    print(f"Manifest: {result['manifest']}")
    print(f"Plan: {result['plan']}")
    print(f"PPTX: {result['pptx']}")


if __name__ == "__main__":
    main()
