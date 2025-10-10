# 4. Technical Constraints and Integration Requirements

### Existing Technology Stack
| Category | Technology |
| :--- | :--- |
| **Backend** | Django, Django Ninja, Celery, PostgreSQL |
| **Frontend** | React, Vite, TypeScript, TanStack Router & Query |
| **Deployment** | Docker, Docker Compose |
| **Tooling** | pnpm, uv/poetry, ruff, mypy, pytest, vitest |

### Integration Approach
*   **Database Integration**: All schema changes **must** be accompanied by a Django migration file.
*   **API Integration**: The frontend will communicate with the backend exclusively through the established Django Ninja REST API.
*   **Testing Integration**: New backend code must include `pytest` tests. New frontend logic must be covered by `vitest` tests.
