from src.lite.schemas import VISUAL_INVENTORY_SCHEMA


def _validate_required(schema, data):
    missing = set(schema.get("required", [])) - set(data)
    assert not missing, f"Missing required keys: {missing}"


def test_visual_inventory_schema_accepts_expected_payload_shape():
    payload = {
        "visuals": [
            {
                "asset_id": "fig_001",
                "kind": "figure",
                "source_page": 1,
                "bbox": {"x0": 0.1, "y0": 0.2, "x1": 0.8, "y1": 0.9},
                "caption": "Overview",
                "role": "method",
                "importance": "high",
                "confidence": 0.9,
                "extraction_status": "model_selected",
                "notes": "Use on method slide",
            }
        ]
    }

    _validate_required(VISUAL_INVENTORY_SCHEMA, payload)
    item_schema = VISUAL_INVENTORY_SCHEMA["properties"]["visuals"]["items"]
    _validate_required(item_schema, payload["visuals"][0])
    assert payload["visuals"][0]["kind"] in item_schema["properties"]["kind"]["enum"]


def test_visual_inventory_schema_requires_bbox_coordinates():
    bbox_schema = (
        VISUAL_INVENTORY_SCHEMA["properties"]["visuals"]["items"]["properties"]["bbox"]
    )

    _validate_required(bbox_schema, {"x0": 0, "y0": 0, "x1": 1, "y1": 1})

