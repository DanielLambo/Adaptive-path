# Development Verification Checklist

This checklist provides a set of steps to verify that all components of the application are correctly configured and functioning after a fresh setup or after making significant changes.

### 1. Environment and Dependencies

- [ ] `.env` file exists and is populated with `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `API_STATIC_TOKEN`.
- [ ] All dependencies from `requirements.txt` and `requirements-dev.txt` are installed in the active virtual environment.

### 2. Neo4j Connection

- **Goal**: Verify that the application can connect to the Neo4j database.
- **Action**: Run the Neo4j connection integration test.
- **Command**:
  ```bash
  PYTHONPATH=. pytest tests/test_neo4j_connection.py
  ```
- **Expected Result**: The test should pass (not be skipped). If it is skipped, ensure your `.env` variables are correctly set and loaded.

### 3. Model Service Fallback Mechanism

- **Goal**: Verify that the application does not crash and uses the fallback predictor if the ML model is missing.
- **Action**: Temporarily rename the `models/best_model.h5` file (e.g., to `best_model.h5.bak`).
- **Command**: Run the model service fallback test.
  ```bash
  PYTHONPATH=. pytest tests/test_model_service_fallback.py
  ```
- **Expected Result**: All tests in this file should pass, confirming the fallback logic is working.
- **Cleanup**: Rename the model file back to `best_model.h5`.

### 4. API Health and Authentication

- **Goal**: Verify that the API server is running and security is active.
- **Action**: Start the FastAPI server.
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- **Commands**:
  1.  **Health Check**:
      ```bash
      curl -X GET "http://localhost:8000/health"
      ```
      - **Expected Result**: `{"status":"ok"}`

  2.  **Auth Check (No Token)**:
      ```bash
      curl -X POST "http://localhost:8000/generate-path" -H "Content-Type: application/json" -d '{}'
      ```
      - **Expected Result**: `{"detail":"Authorization header is missing"}` (or similar 401 error).

  3.  **Auth Check (Invalid Token)**:
      ```bash
      curl -X POST "http://localhost:8000/generate-path" -H "Content-Type: application/json" -H "Authorization: Bearer invalid" -d '{}'
      ```
      - **Expected Result**: `{"detail":"Invalid or expired token"}` (or similar 403 error).

### 5. End-to-End Path Generation

- **Goal**: Verify the entire request pipeline works correctly.
- **Action**: With the server running, send a valid request.
- **Command**:
  ```bash
  curl -X POST "http://localhost:8000/generate-path" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-api-token" \
  -d '{
    "student_id": "verify-student",
    "history": [{"kp_id": 1, "score": 0.3, "type": "quiz"}]
  }'
  ```
- **Expected Result**: A JSON response with a `200 OK` status code, containing a `student_id`, `prediction_info`, and a `learning_path` array. The exact content will depend on your model and data, but the structure should be valid.
