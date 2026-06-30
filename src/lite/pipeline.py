"""Minimal end-to-end Lite harness."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Optional

from src.lite.deck_writer import LitePPTXWriter
from src.lite.pdf_render import LitePDFReader
from src.lite.planner import DeckPlanner, LitePlanner
from src.lite.visual_inventory import FullPageFallbackInventory, VisualInventoryProvider


class LitePipeline:
    """Run the lightweight PDF-to-deck harness."""

    def __init__(
        self,
        pdf_reader: Optional[LitePDFReader] = None,
        inventory_provider: Optional[VisualInventoryProvider] = None,
        planner: Optional[DeckPlanner] = None,
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
        manifest_path = run_dir / "harness_manifest.json"
        self._write_manifest(
            manifest_path=manifest_path,
            pdf_path=pdf_path,
            rendered_pages=rendered_pages,
            deck_path=plan_path,
            pptx_path=pptx_path,
            visuals=visuals,
        )

        return {
            "run_dir": str(run_dir),
            "manifest": str(manifest_path),
            "plan": str(plan_path),
            "pptx": str(pptx_path),
        }

    def _write_manifest(
        self,
        manifest_path: Path,
        pdf_path: Path,
        rendered_pages,
        deck_path: Path,
        pptx_path: Path,
        visuals,
    ) -> None:
        manifest = {
            "source_pdf": str(pdf_path),
            "providers": {
                "pdf_reader": type(self.pdf_reader).__name__,
                "visual_inventory": type(self.inventory_provider).__name__,
                "deck_planner": type(self.planner).__name__,
                "deck_writer": type(self.writer).__name__,
            },
            "artifacts": {
                "rendered_pages": [page.__dict__ for page in rendered_pages],
                "visual_assets": [visual.asset_id for visual in visuals],
                "deck_spec": str(deck_path),
                "pptx": str(pptx_path),
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
