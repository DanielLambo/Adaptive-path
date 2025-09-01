# app/predictor_stub.py
from typing import List, Dict, Tuple
import random

def predict_weakest_kp_stub(
    history: List[Dict],
) -> Tuple[int, float, List[Tuple[int, float]]]:
    """
    A deterministic stub for prediction.
    Uses student_id to seed a random choice.
    """
    if not history:
        return 1, 0.9, [(1, 0.9)]

    # Use a characteristic from the history to seed the choice
    seed_val = len(history) + history[0].get("kp_id", 0)
    random.seed(seed_val)

    # Mock a prediction
    kps = list(range(1, 9))  # Assume 8 KPs
    random.shuffle(kps)

    top_kp = kps[0]
    confidence = 0.5 + (top_kp / 16) # Some deterministic confidence

    top3 = [(kp, 0.0) for kp in kps[:3]]
    top3[0] = (top_kp, confidence)

    return top_kp, confidence, top3
