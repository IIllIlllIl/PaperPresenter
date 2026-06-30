"""Visual inventory providers for PaperPresenter Lite."""

from __future__ import annotations

from pathlib import Path
from typing import List, Protocol

from src.lite.models import BoundingBox, RenderedPage, VisualAsset


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

