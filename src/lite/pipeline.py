"""Minimal end-to-end Lite pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from src.lite.deck_writer import LitePPTXWriter
from src.lite.pdf_render import LitePDFReader
from src.lite.planner import LitePlanner
from src.lite.visual_inventory import FullPageFallbackInventory, VisualInventoryProvider


class LitePipeline:
    """Run the lightweight PDF-to-deck workflow."""

    def __init__(
        self,
        pdf_reader: Optional[LitePDFReader] = None,
        inventory_provider: Optional[VisualInventoryProvider] = None,
        planner: Optional[LitePlanner] = None,
        writer: Optional[LitePPTXWriter] = None,
    ):
        self.pdf_reader = pdf_reader or LitePDFReader()
        self.inventory_provider = inventory_provider or FullPageFallbackInventory()
        self.planner = planner or LitePlanner()
        self.writer = writer or LitePPTXWriter()

    def run(self, pdf_path: str | Path, output_dir: str | Path = "outputs/lite") -> Dict[str, str]:
        pdf_path = Path(pdf_path)
        run_dir = Path(output_dir) / pdf_path.stem
        run_dir.mkdir(parents=True, exist_ok=True)

        metadata, paper_text, rendered_pages = self.pdf_reader.read(pdf_path, run_dir)
        visuals = self.inventory_provider.inventory(rendered_pages)
        deck = self.planner.plan(metadata=metadata, paper_text=paper_text, visuals=visuals)

        plan_path = run_dir / "deck_spec.json"
        pptx_path = run_dir / f"{pdf_path.stem}.pptx"
        deck.save_json(plan_path)
        self.writer.write(deck, pptx_path)

        return {
            "run_dir": str(run_dir),
            "plan": str(plan_path),
            "pptx": str(pptx_path),
        }

