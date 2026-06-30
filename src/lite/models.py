"""Small stable schemas for PaperPresenter Lite."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class BoundingBox:
    """A normalized page-space bounding box."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        values = (self.x0, self.y0, self.x1, self.y1)
        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError("BoundingBox coordinates must be normalized to [0, 1]")
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("BoundingBox must have positive width and height")

    @classmethod
    def full_page(cls) -> "BoundingBox":
        return cls(0.0, 0.0, 1.0, 1.0)


@dataclass
class PaperMetadata:
    title: str = "Untitled Paper"
    authors: List[str] = field(default_factory=list)
    year: Optional[str] = None
    page_count: int = 0
    source_pdf: str = ""


@dataclass
class RenderedPage:
    page_num: int
    image_path: str
    width: int
    height: int
    dpi: int


@dataclass
class VisualAssetDraft:
    """Model-produced visual asset metadata before image materialization."""

    asset_id: str
    kind: str
    source_page: int
    bbox: BoundingBox = field(default_factory=BoundingBox.full_page)
    caption: str = ""
    role: str = ""
    importance: str = "medium"
    confidence: float = 0.0
    extraction_status: str = "model_selected"
    notes: str = ""


@dataclass
class VisualAsset:
    asset_id: str
    kind: str
    image_path: str
    source_page: int
    bbox: BoundingBox = field(default_factory=BoundingBox.full_page)
    caption: str = ""
    role: str = ""
    importance: str = "medium"
    confidence: float = 0.0
    extraction_status: str = "fallback_full_page"
    notes: str = ""


@dataclass
class PaperAnalysis:
    summary: str = ""
    problem: List[str] = field(default_factory=list)
    method: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    discussion_questions: List[str] = field(default_factory=list)


@dataclass
class SlideSpec:
    title: str
    bullets: List[str] = field(default_factory=list)
    layout: str = "text_only"
    visual_asset_ids: List[str] = field(default_factory=list)
    speaker_intent: str = ""
    notes: str = ""


@dataclass
class DeckSpec:
    metadata: PaperMetadata
    analysis: PaperAnalysis
    slides: List[SlideSpec]
    visuals: List[VisualAsset] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeckSpec":
        metadata = PaperMetadata(**data.get("metadata", {}))
        analysis = PaperAnalysis(**data.get("analysis", {}))
        visuals = [
            VisualAsset(
                **{
                    **item,
                    "bbox": BoundingBox(**item["bbox"])
                    if isinstance(item.get("bbox"), dict)
                    else item.get("bbox", BoundingBox.full_page()),
                }
            )
            for item in data.get("visuals", [])
        ]
        slides = [SlideSpec(**item) for item in data.get("slides", [])]
        return cls(metadata=metadata, analysis=analysis, slides=slides, visuals=visuals)

    def visual_map(self) -> Dict[str, VisualAsset]:
        return {visual.asset_id: visual for visual in self.visuals}

    def save_json(self, path: str | Path) -> None:
        import json

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load_json(cls, path: str | Path) -> "DeckSpec":
        import json

        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def visual_asset_draft_from_dict(data: Dict[str, Any]) -> VisualAssetDraft:
    bbox_data = data.get("bbox")
    bbox = BoundingBox(**bbox_data) if isinstance(bbox_data, dict) else BoundingBox.full_page()
    return VisualAssetDraft(
        asset_id=str(data.get("asset_id", "")),
        kind=str(data.get("kind", "region")),
        source_page=int(data.get("source_page", 1)),
        bbox=bbox,
        caption=str(data.get("caption", "")),
        role=str(data.get("role", "")),
        importance=str(data.get("importance", "medium")),
        confidence=float(data.get("confidence", 0.0)),
        extraction_status=str(data.get("extraction_status", "model_selected")),
        notes=str(data.get("notes", "")),
    )

