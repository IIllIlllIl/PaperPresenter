from pathlib import Path

from PIL import Image

from src.lite.models import RenderedPage
from src.lite.visual_inventory import LocalCodexVisionInventory


class FakeCodexRunner:
    def run_json(self, prompt, images, output_schema):
        return {
            "visuals": [
                {
                    "asset_id": "fig_001",
                    "kind": "figure",
                    "source_page": 1,
                    "bbox": {"x0": 0.1, "y0": 0.1, "x1": 0.9, "y1": 0.9},
                    "caption": "Architecture overview",
                    "role": "method overview",
                    "importance": "high",
                    "confidence": 0.9,
                    "extraction_status": "model_selected",
                    "notes": "Use for method slide",
                }
            ]
        }


def test_local_codex_inventory_materializes_visual_crop(tmp_path: Path):
    page_dir = tmp_path / "pages"
    page_dir.mkdir()
    page_path = page_dir / "page_001.png"
    Image.new("RGB", (100, 100), "white").save(page_path)

    provider = LocalCodexVisionInventory(runner=FakeCodexRunner())
    visuals = provider.inventory(
        [RenderedPage(page_num=1, image_path=str(page_path), width=100, height=100, dpi=100)]
    )

    assert len(visuals) == 1
    assert visuals[0].asset_id == "fig_001"
    assert visuals[0].extraction_status == "model_selected"
    assert Path(visuals[0].image_path).exists()
    assert Path(visuals[0].image_path).parent.name == "visuals"

