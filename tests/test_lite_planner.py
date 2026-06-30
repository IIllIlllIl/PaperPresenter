from src.lite.models import PaperMetadata, VisualAsset
from src.lite.planner import LitePlanner


def test_lite_planner_produces_reviewable_deck():
    visuals = [
        VisualAsset(
            asset_id="page_001",
            kind="page",
            image_path="page_001.png",
            source_page=1,
        )
    ]

    deck = LitePlanner().plan(
        metadata=PaperMetadata(title="A Paper", page_count=8),
        paper_text="This paper proposes a method and evaluates results.",
        visuals=visuals,
    )

    assert 8 <= len(deck.slides) <= 15
    assert deck.slides[0].title == "A Paper"
    assert "page_001" in deck.visual_map()
    assert any(slide.title == "Limitations" for slide in deck.slides)

