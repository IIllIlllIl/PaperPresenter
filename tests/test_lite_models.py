from pathlib import Path

from src.lite.models import BoundingBox, DeckSpec, PaperAnalysis, PaperMetadata, SlideSpec, VisualAsset


def test_deck_spec_json_roundtrip(tmp_path: Path):
    deck = DeckSpec(
        metadata=PaperMetadata(title="Example", page_count=3, source_pdf="paper.pdf"),
        analysis=PaperAnalysis(summary="Summary"),
        slides=[
            SlideSpec(
                title="Main Results",
                bullets=["Result one"],
                visual_asset_ids=["page_001"],
            )
        ],
        visuals=[
            VisualAsset(
                asset_id="page_001",
                kind="page",
                image_path="page_001.png",
                source_page=1,
                bbox=BoundingBox.full_page(),
            )
        ],
    )

    path = tmp_path / "deck.json"
    deck.save_json(path)
    loaded = DeckSpec.load_json(path)

    assert loaded.metadata.title == "Example"
    assert loaded.slides[0].visual_asset_ids == ["page_001"]
    assert loaded.visuals[0].bbox == BoundingBox.full_page()


def test_bounding_box_rejects_invalid_coordinates():
    try:
        BoundingBox(0.5, 0.0, 0.4, 1.0)
    except ValueError as exc:
        assert "positive width" in str(exc)
    else:
        raise AssertionError("Expected invalid bounding box to raise ValueError")

