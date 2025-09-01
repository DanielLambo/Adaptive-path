# app/main.py
"""
FastAPI Application Entry Point

This module defines the main FastAPI application, its endpoints, and lifecycle events.

Changes made:
- Replaced the old `/predict` endpoint with a new `/generate-path` endpoint.
- Integrated the new Pydantic models for strongly-typed requests/responses.
- Added dependency injection for security (`check_bearer_token`).
- Implemented robust error handling to return appropriate HTTP status codes.
- Integrated the refactored `predictor_service` and `path_builder` services.
- Kept the lifespan manager for Neo4j driver lifecycle.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager

from app.db.neo4j_client import get_driver, close_driver, NEO4J_DATABASE
from app.models import (
    GeneratePathRequest,
    GeneratePathResponse,
    PredictionInfo,
)
from app.security import check_bearer_token
from app.predictor_service import get_pred_for_student
from app.path_builder import build_path_for_kp
import logging

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Application Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager to handle Neo4j driver connection.
    """
    logger.info("Application startup...")
    get_driver()  # Initialize driver singleton
    yield
    logger.info("Application shutdown...")
    await close_driver()


app = FastAPI(
    title="Adaptive Learning Path Generator",
    description="An API to generate personalized learning paths based on student history.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- API Endpoints ---


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok"}


@app.post(
    "/generate-path",
    response_model=GeneratePathResponse,
    tags=["Learning Paths"],
    dependencies=[Depends(check_bearer_token)],
)
async def generate_path(req: GeneratePathRequest) -> GeneratePathResponse:
    """
    Generates a personalized learning path for a student.

    - If `force_kp_id` is provided, it generates a path for that specific KP.
    - Otherwise, it predicts the student's weakest KP based on their `history`.
    - If no history is provided, it suggests a default starting path.
    """
    target_kp_id = req.force_kp_id
    prediction_info = None
    message = ""

    try:
        # 1. Determine the target Knowledge Point (KP)
        if not target_kp_id:
            if req.history:
                logger.info(f"Predicting weakest KP for student: {req.student_id}")
                pred = await get_pred_for_student(req.student_id, req.history)
                target_kp_id = pred["top_kp"]
                prediction_info = PredictionInfo(
                    kp_id=target_kp_id,
                    confidence=pred["confidence"],
                    top3=[{"kp_id": p[0], "confidence": p[1]} for p in pred["top3"]],
                )
                message = "Path generated for predicted weakest KP."
            else:
                # No history and no forced KP, suggest a default
                from app.model_service import DEFAULT_KP_ID

                target_kp_id = DEFAULT_KP_ID
                message = "No history provided. Generating default introductory path."
        else:
            message = "Path generated for manually specified KP."

        if not target_kp_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Could not determine a target KP."
            )

        # 2. Build the learning path for the target KP
        logger.info(f"Building learning path for KP ID: {target_kp_id}")
        driver = get_driver()
        db_name = NEO4J_DATABASE
        path_components = await build_path_for_kp(driver, db_name, target_kp_id)

        if not path_components:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Could not build a path for KP ID: {target_kp_id}. It may not exist.",
            )

        return GeneratePathResponse(
            student_id=req.student_id,
            prediction_info=prediction_info,
            learning_path=path_components,
            message=message,
        )

    except HTTPException as http_exc:
        # Re-raise HTTPException to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error(
            f"An unexpected error occurred for student {req.student_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating the path.",
        )
