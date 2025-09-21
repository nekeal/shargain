# Data Models and APIs

## Data Models
The source of truth for data models are the Django model files (e.g., `shargain/offers/models.py`, `shargain/accounts/models.py`). These define the schema for the PostgreSQL database.

## API Specifications
The backend exposes an OpenAPI-compliant REST API. The frontend uses `openapi-ts` to generate a typed client from this specification, ensuring type safety between the frontend and backend. The main API definition can be found in `shargain/public_api/api.py`.
