"""Visual inventory providers for PaperPresenter Lite."""

from __future__ import annotations

from pathlib import Path
from typing import List, Protocol

from PIL import Image

from src.lite.local_codex import LocalCodexRunner
from src.lite.models import BoundingBox, RenderedPage, VisualAsset, visual_asset_draft_from_dict
from src.lite.schemas import VISUAL_INVENTORY_SCHEMA


class VisualInventoryProvider(Protocol):
    """Provider interface for page-level visual discovery."""

    def inventory(self, pages: List[RenderedPage]) -> List[VisualAsset]:
        """Return visual assets selected from rendered pages."""


class FullPageFallbackInventory:
    """
    Deterministic fallback inventory.

    This keeps the Lite pipeline runnable before the GPT-5 vision provider is
    connected. It intentionally marks assets as uncertain full-page fallbacks.
    """

    def __init__(self, max_pages: int = 6):
        self.max_pages = max_pages

    def inventory(self, pages: List[RenderedPage]) -> List[VisualAsset]:
        selected_pages = pages[: self.max_pages]
        assets: List[VisualAsset] = []

        for page in selected_pages:
            assets.append(
                VisualAsset(
                    asset_id=f"page_{page.page_num:03d}",
                    kind="page",
                    image_path=str(Path(page.image_path)),
                    source_page=page.page_num,
                    bbox=BoundingBox.full_page(),
                    caption=f"Full-page fallback from page {page.page_num}",
                    role="source inspection",
                    importance="medium",
                    confidence=0.25,
                    extraction_status="fallback_full_page",
                    notes="Replace with GPT-5 vision-selected figure/table crop.",
                )
            )

        return assets


class LocalCodexVisionInventory:
    """Use local `codex exec` to select visual assets from rendered pages."""

    def __init__(self, runner: LocalCodexRunner, max_pages: int = 12, min_confidence_for_crop: float = 0.65):
        self.runner = runner
        self.max_pages = max_pages
        self.min_confidence_for_crop = min_confidence_for_crop

    def inventory(self, pages: List[RenderedPage]) -> List[VisualAsset]:
        selected_pages = pages[: self.max_pages]
        prompt = self._build_prompt(selected_pages)
        response = self.runner.run_json(
            prompt=prompt,
            images=[page.image_path for page in selected_pages],
            output_schema=VISUAL_INVENTORY_SCHEMA,
        )
        drafts = [visual_asset_draft_from_dict(item) for item in response.get("visuals", [])]
        page_map = {page.page_num: page for page in pages}
        assets: List[VisualAsset] = []

        for draft in drafts:
            page = page_map.get(draft.source_page)
            if page is None:
                continue
            image_path = page.image_path
            status = draft.extraction_status
            if draft.confidence >= self.min_confidence_for_crop and draft.bbox != BoundingBox.full_page():
                image_path = self._crop_page(page, draft.asset_id, draft.bbox)
            else:
                status = "fallback_full_page"

            assets.append(
                VisualAsset(
                    asset_id=draft.asset_id,
                    kind=draft.kind,
                    image_path=image_path,
                    source_page=draft.source_page,
                    bbox=draft.bbox,
                    caption=draft.caption,
                    role=draft.role,
                    importance=draft.importance,
                    confidence=draft.confidence,
                    extraction_status=status,
                    notes=draft.notes,
                )
            )

        return assets

    def _build_prompt(self, pages: List[RenderedPage]) -> str:
        page_lines = "\n".join(
            f"- image {index}: page {page.page_num}, {page.width}x{page.height}px"
            for index, page in enumerate(pages, start=1)
        )
        return f"""You are selecting visual evidence from an academic paper for a PhD/postdoc group meeting deck.

Inspect the attached rendered PDF pages and return STRICT JSON matching the schema.

Pages:
{page_lines}

Rules:
- Select only figures, tables, charts, diagrams, equations, or result-heavy regions that are useful for slides.
- Prefer complete visual regions over tight crops.
- Use normalized bbox coordinates in page image space: x0,y0 top-left and x1,y1 bottom-right, all in [0,1].
- If a crop is uncertain, use bbox full page and extraction_status "uncertain_region".
- Use stable asset IDs like "fig_001", "table_002", or "region_003".
- Do not include body-text-only regions unless they are necessary context.
- Return at most 12 visuals.
"""

    def _crop_page(self, page: RenderedPage, asset_id: str, bbox: BoundingBox) -> str:
        page_path = Path(page.image_path)
        crop_dir = page_path.parent.parent / "visuals"
        crop_dir.mkdir(parents=True, exist_ok=True)
        output_path = crop_dir / f"{asset_id}.png"

        with Image.open(page_path) as image:
            left = int(bbox.x0 * image.width)
            upper = int(bbox.y0 * image.height)
            right = int(bbox.x1 * image.width)
            lower = int(bbox.y1 * image.height)
            image.crop((left, upper, right, lower)).save(output_path)

        return str(output_path)
