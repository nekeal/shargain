# Quick Reference - Key Files and Entry Points

## Critical Files for Understanding the System

*   **Main Backend Application**: `shargain/`
*   **Core Business Logic**: `shargain/offers/application/` (Contains the command/query handlers)
*   **API Layer**: `shargain/public_api/api.py` (Exposes the business logic to the web)
*   **Authentication**: `shargain/public_api/auth.py` (Handles user login/signup)
*   **Database Models**: `shargain/*/models.py` (Standard Django models)
*   **Frontend Application**: `frontend/`
*   **Main Frontend Entrypoint**: `frontend/src/main.tsx`
