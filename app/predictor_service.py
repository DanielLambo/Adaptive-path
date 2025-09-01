# app/predictor_service.py
"""
Service layer that glues the student history to the prediction model.

Changes made:
- Updated `get_pred_for_student` to take history as a parameter.
- Handles the case of empty history gracefully by returning a default structure.
- Formats the output from the model service into a structured dictionary.
"""
from typing import List, Dict, Any

# The actual prediction logic is in model_service.
# This allows us to easily swap out the model or add other data sources.
from .model_service import predict_weakest_kp
from .model_service import DEFAULT_KP_ID


async def get_pred_for_student(student_id: str, history: List[Dict]) -> Dict[str, Any]:
    """
    Gets a prediction for a student based on their history.

    Args:
        student_id: The ID of the student.
        history: A list of the student's historical interactions.

    Returns:
        A dictionary containing the prediction details.
    """
    if not history:
        # No history, so no prediction can be made.
        # Return a structure indicating this. The endpoint can then decide
        # to serve a default introductory path.
        return {
            "student_id": student_id,
            "top_kp": DEFAULT_KP_ID, # Suggest a default starting point
            "confidence": 1.0,
            "top3": [(DEFAULT_KP_ID, 1.0)],
            "message": "No history provided for prediction.",
        }

    # Call the model service to get the prediction
    top_kp, confidence, top3 = predict_weakest_kp(history)

    return {
        "student_id": student_id,
        "top_kp": top_kp,
        "confidence": confidence,
        "top3": top3,
        "message": "Prediction successful.",
    }
