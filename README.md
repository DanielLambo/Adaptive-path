# Adaptive Learning Path Generator

This project is a FastAPI application that generates personalized learning paths for students based on their historical performance. It uses a trained LSTM model to predict a student's weakest knowledge point (KP) and a Neo4j graph database to construct a learning path around that KP.

## Core Features

- **Personalized Path Generation**: Predicts weakest KP and builds a relevant learning path.
- **ML Model Serving**: Serves a Keras/TensorFlow model with a robust fallback mechanism.
- **Graph-Based Learning Structure**: Uses Neo4j to model dependencies between knowledge points.
- **Mockable Services**: Includes a mock Blackboard service for content and history, allowing for development without a live LMS.
- **Secure API**: Endpoints are protected by bearer token authentication.

## Project Structure

```
project_root/
├─ models/              # Trained models, scalers, and metadata
├─ app/                 # Main application source code
│  ├─ db/                # Neo4j driver and client
│  ├─ mock/              # Mock Blackboard service
│  ├─ main.py            # FastAPI app entry point
│  ├─ model_service.py   # Loads model, preprocesses, predicts
│  ├─ predictor_service.py # Glue logic for prediction
│  ├─ path_builder.py    # Builds learning path from graph
│  ├─ queries.py         # Cypher queries
│  ├─ models.py          # Pydantic models
│  └─ security.py        # Bearer token auth
├─ tests/               # Pytest test suite
└─ README.md
```

## Getting Started

### 1. Prerequisites

- Python 3.11+
- A running Neo4j Aura instance (or local Neo4j database)

### 2. Installation

Clone the repository and create a virtual environment:

```bash
git clone <repository_url>
cd <repository_name>
python -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development and optional dependencies (including tensorflow)
pip install -r requirements-dev.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root by copying the example below. This file will store your database credentials and API token.

```env
# .env file

# Neo4j Aura Credentials
NEO4J_URI="neo4j+s://your-aura-instance.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-aura-password"
NEO4J_DATABASE="neo4j" # Usually 'neo4j' for AuraDB

# API Security Token
# This is the static token clients must provide in the Authorization header.
API_STATIC_TOKEN="your-secret-api-token"
```

### 4. Data Loading

*(Note: A data loading script for the Neo4j database, `neo4j_loader.py`, is mentioned in the project but not fully implemented in this refactoring. You would need to run a script to populate your Neo4j instance with KP nodes and relationships.)*

### 5. Running the Application

To run the FastAPI server, use `uvicorn`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Note for macOS users**: It is recommended to run `uvicorn` without the `--reload` flag, as the auto-reloader can cause issues with TensorFlow's multi-threading model.

The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

### 6. Running Tests

To run the test suite, use `pytest` from the project root:

```bash
PYTHONPATH=. pytest
```
The `PYTHONPATH=.` prefix is required for `pytest` to correctly discover the `app` module.

## Colab → Serving Workflow

To update the machine learning model served by this application:

1.  **Export Artifacts from Colab**: After training your model in Google Colab (or any other environment), save the following three files:
    - `best_model.h5`: The trained Keras model.
    - `feature_scaler.pkl`: The `StandardScaler` object from `scikit-learn` used to scale numeric features.
    - `metadata.json`: A JSON file containing model parameters like `max_seq_len`, feature names, and the label encoder mapping for KPs. See `models/metadata.json` for an example structure.

2.  **Place Artifacts in `/models`**: Copy these three files into the `/models` directory of this project. The application will automatically use them on the next startup/request. The contents of the `/models` directory are ignored by Git, so you will not commit them.

3.  **Validate**: Restart the application and use the sample `curl` request below to test the new model.

## API Usage Examples

Replace `your-secret-api-token` with the value you set for `API_STATIC_TOKEN` in your `.env` file.

### Health Check

```bash
curl -X GET "http://localhost:8000/health"
```
**Expected Response:** `{"status":"ok"}`

### Generate a Learning Path

This request will use the model to predict the weakest KP based on the provided history and then generate a learning path for it.

```bash
curl -X POST "http://localhost:8000/generate-path" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your-secret-api-token" \
-d '{
  "student_id": "student-123",
  "history": [
    {"kp_id": 1, "score": 0.9, "type": "quiz"},
    {"kp_id": 2, "score": 0.7, "type": "quiz"},
    {"kp_id": 3, "score": 0.5, "type": "quiz"}
  ]
}'
```

**Example Response:**
```json
{
  "student_id": "student-123",
  "prediction_info": {
    "kp_id": 3,
    "confidence": 0.85,
    "top3": [
      { "kp_id": 3, "confidence": 0.85 },
      { "kp_id": 4, "confidence": 0.10 }
    ]
  },
  "learning_path": [
    {
      "kp_id": 2,
      "kp_name": "Control Structures",
      "content": [
        {
          "id": "vid-201",
          "type": "video",
          "title": "If/Else Explained",
          "url": "https://example.com/vid-201",
          "est_minutes": 7,
          "difficulty": 1,
          "metadata": { "source": "youtube" }
        }
      ]
    },
    {
      "kp_id": 3,
      "kp_name": "Loops",
      "content": [
        {
          "id": "vid-301",
          "type": "video",
          "title": "Loops Deep Dive",
          "url": "https://example.com/vid-301",
          "est_minutes": 12,
          "difficulty": 2,
          "metadata": { "source": "vimeo" }
        }
      ]
    }
  ],
  "message": "Path generated for predicted weakest KP."
}
```

## Security & Production Notes

- **Secrets Management**: Never commit your `.env` file to version control. In a production environment, use a secrets management service like AWS Secrets Manager, Google Secret Manager, or HashiCorp Vault to inject these environment variables.
- **Authentication**: The current bearer token is for basic security. For a production system, switch to an OAuth2 or LTI 1.3 flow for authenticating users and systems.
- **HTTPS**: Always run a production application behind a reverse proxy (like Nginx or Traefik) that terminates TLS/SSL traffic.
- **Rate Limiting**: To prevent abuse, implement rate limiting on public-facing API endpoints.
