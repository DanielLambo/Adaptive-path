import json, os
from typing import Optional, Dict, Any

PRED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "predictions.json")

def get_pred_for_student(student_id: int) -> Optional[Dict[str,Any]]:
    if not os.path.exists(PRED_PATH):
        return None
    with open(PRED_PATH) as f:
        preds = json.load(f)
    return preds.get(str(student_id))
