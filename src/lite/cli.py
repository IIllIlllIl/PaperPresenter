"""Command line entrypoint for PaperPresenter Lite."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.lite.pipeline import LitePipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Lite presentation from one paper PDF.")
    parser.add_argument("pdf", type=Path, help="Path to the input paper PDF")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/lite"), help="Output directory")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = LitePipeline().run(args.pdf, args.output_dir)
    print(f"Plan: {result['plan']}")
    print(f"PPTX: {result['pptx']}")


if __name__ == "__main__":
    main()

