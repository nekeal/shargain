# Testing Strategy

## The Testing Pyramid

Our strategy emphasizes having a large base of fast, inexpensive unit tests and a smaller layer of integration tests to verify that components work together correctly. End-to-end testing is currently out of scope.

```plaintext
    /----------\
   / Integration\
  /--------------\
 /   Unit Tests   \
/------------------\
```

## Test Organization

-   **Frontend Tests (Vitest):**
    -   Unit and integration tests for React components are written with Vitest and React Testing Library.
    -   Test files are co-located with the components they are testing.
    -   **Structure:** `src/components/dashboard/MyComponent.test.tsx`

-   **Backend Tests (Pytest):**
    -   Unit and integration tests for Django models, services, and APIs are written with Pytest.
    -   Tests are located in a `tests` subdirectory within each Django app.
    -   **Structure:** `shargain/offers/tests/test_models.py`

## Test Examples

### Frontend Component Test (Vitest)

```typescript
// src/components/Header.test.tsx
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Header from './Header';

test('renders the header with the application name', () => {
  render(<Header />);
  // Assert that the main heading is visible in the document.
  const headingElement = screen.getByRole('heading', { name: /Shargain/i });
  expect(headingElement).toBeInTheDocument();
});
```

### Backend API Test (Pytest)

```python
# shargain/offers/tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_get_targets_unauthenticated(client: APIClient):
    """
    Tests that an unauthenticated user cannot access the targets endpoint.
    """
    url = reverse('api:get_my_target')  # Assuming a URL name
    response = client.get(url)
    assert response.status_code == 403  # Or 401, depending on auth setup
```
