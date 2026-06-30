"""JSON schemas for local Codex provider outputs."""

VISUAL_INVENTORY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "visuals": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "asset_id": {"type": "string"},
                    "kind": {
                        "type": "string",
                        "enum": ["figure", "table", "diagram", "chart", "equation", "page", "region"],
                    },
                    "source_page": {"type": "integer", "minimum": 1},
                    "bbox": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "x0": {"type": "number", "minimum": 0, "maximum": 1},
                            "y0": {"type": "number", "minimum": 0, "maximum": 1},
                            "x1": {"type": "number", "minimum": 0, "maximum": 1},
                            "y1": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["x0", "y0", "x1", "y1"],
                    },
                    "caption": {"type": "string"},
                    "role": {"type": "string"},
                    "importance": {"type": "string", "enum": ["low", "medium", "high"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "extraction_status": {
                        "type": "string",
                        "enum": ["model_selected", "fallback_full_page", "uncertain_region"],
                    },
                    "notes": {"type": "string"},
                },
                "required": [
                    "asset_id",
                    "kind",
                    "source_page",
                    "bbox",
                    "caption",
                    "role",
                    "importance",
                    "confidence",
                    "extraction_status",
                    "notes",
                ],
            },
        }
    },
    "required": ["visuals"],
}

