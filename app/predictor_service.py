from .mock_blackboard import get_student_history
from .model_service import predict_weakest_kp

def get_pred_for_student(student_id: int):
    history = get_student_history(student_id)
    if not history:
        return None
    kp_id, confidence = predict_weakest_kp(history)
    return {"student_id": student_id, "top_kp": kp_id, "confidence": confidence}
