# app/path_builder.py
"""
Service to build a structured learning path for a given Knowledge Point.

Changes made:
- Converted to `async` to work with the async Neo4j driver.
- Corrected relative imports for `queries` and `mock_blackboard`.
- Added content ranking to order materials within each KP module.
"""
from typing import List, Dict, Any
from neo4j import AsyncDriver
from . import queries
from .mock import mock_blackboard

# Define a canonical order for content types to ensure a logical flow
CONTENT_TYPE_ORDER = {
    "video": 1,
    "reading": 2,
    "practice": 3,
    "quiz": 4,
    "assessment": 5,
}

async def build_path_for_kp(driver: AsyncDriver, db: str, target_kp_id: int) -> List[Dict[str, Any]]:
    """
    Builds a learning path around a target KP.
    The path consists of prerequisites, the target itself, and follow-up KPs.
    """
    # 1. Fetch all required KPs from the graph
    target_kp = await queries.get_kp_by_id(driver, target_kp_id, db)
    if not target_kp:
        return []

    prereq_kps = await queries.prereqs_for(driver, target_kp_id, db)
    followup_kps = await queries.downstream_kps(driver, target_kp_id, db)

    # 2. Structure the path by ordering the KPs
    path_kps = prereq_kps + [target_kp] + followup_kps

    learning_path = []
    for kp in path_kps:
        # For each KP, get its associated content from the mock blackboard
        content_items = mock_blackboard.get_content_for_kp(kp["id"])
        if not content_items:
            # If no real content, generate some fake content for a better demo
            content_items = mock_blackboard.generate_fake_content(kp["id"], seed=kp["id"])

        # Sort the content within the module based on the canonical order
        sorted_content = sorted(
            content_items,
            key=lambda item: CONTENT_TYPE_ORDER.get(item.get("type", ""), 99)
        )

        learning_path.append({
            "kp_id": kp["id"],
            "kp_name": kp.get("name", f"KP {kp['id']}"),
            "content": sorted_content
        })

    return learning_path
