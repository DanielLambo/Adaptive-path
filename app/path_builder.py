from typing import List, Dict, Any
from neo4j import Driver
from . import queries
import mock_blackboard  # local file

def build_path_for_kp(driver: Driver, db: str, target_kp_id: int) -> Dict[str,Any]:
    # 1) Pull KP + prereqs + related KPs
    kp = queries.get_kp_by_id(driver, target_kp_id, db)
    if not kp:
        return {"modules": [], "notes": f"KP {target_kp_id} not found."}

    prereq_kps = queries.prereqs_for(driver, target_kp_id, db)
    followups  = queries.downstream_kps(driver, target_kp_id, db)

    modules: List[Dict[str,Any]] = []

    def pack(kp_row, stage):
        content = mock_blackboard.get_content_for_kp(kp_row["id"])
        # naive ranking: prefer shorter, then lower difficulty
        content_sorted = sorted(content, key=lambda c: (c["est_minutes"], c["difficulty"], c["type"]))
        return {
            "stage": stage,
            "kp": kp_row,
            "items": content_sorted[:3]  # top 3
        }

    # 2) Modules: prerequisites → target → follow-ups
    for p in prereq_kps:
        modules.append(pack(p, stage="prerequisite"))
    modules.append(pack(kp, stage="target"))
    for f in followups[:2]:
        modules.append(pack(f, stage="follow_up"))

    # 3) Basic pacing suggestion
    total_minutes = sum(i["est_minutes"] for m in modules for i in m["items"])
    return {
        "goal_kp": kp,
        "estimated_minutes": total_minutes,
        "modules": modules
    }
