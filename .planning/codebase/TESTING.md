# Testing Patterns

**Analysis Date:** 2026-01-24

## Test Framework

**Python Runner:**
- pytest 7.x
- Config: `pyproject.toml` with settings under `[tool.pytest.ini_options]`
- Django integration: `pytest-django` plugin with settings module `shargain.settings.tests`

**Python Supporting Tools:**
- `pytest-sugar` - enhanced terminal output
- `pytest-xdist` - parallel test execution
- `pytest-cov` - coverage reporting
- `factory-boy` - test data factories
- `faker` - fake data generation

**TypeScript/React Runner:**
- Vitest 3.x
- Config: `frontend/vitest.config.ts`
- Environment: jsdom (DOM simulation)
- Setup file: `frontend/src/test/setup.ts`

**TypeScript Supporting Tools:**
- `@testing-library/react` - component testing
- `@testing-library/dom` - DOM queries
- `@testing-library/jest-dom` - custom matchers
- `vitest` - includes expect assertions

**Run Commands:**
```bash
# Python
pytest shargain                       # Run all tests
pytest --cov shargain               # With coverage report
pytest --lf --ff                    # Last failed/failed first

# TypeScript
npm test                            # Run all tests (vitest run)
npm run test                        # Same as above
# Note: Watch mode not present in scripts but available via vitest watch
```

## Test File Organization

**Location:**
- Python: Co-located in `tests/` subdirectory per app: `shargain/accounts/tests/`, `shargain/offers/tests/`
- TypeScript: Co-located next to source: `src/components/dashboard/monitored-websites/OfferFilters.test.tsx`

**Naming:**
- Python: `test_*.py` (e.g., `test_models.py`, `test_batch_create.py`), `tests.py`, or `*_tests.py`
- TypeScript: `*.test.tsx` or `*.spec.tsx` (observed: `.test.tsx`)

**Structure:**
```
shargain/
├── accounts/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── factories.py           # Test data factories
│   │   ├── fixtures.py            # Shared fixtures (often empty)
│   │   ├── test_models.py
│   │   └── conftest.py            # pytest fixtures (some apps only)
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── notifications/
│   ├── tests/
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   │   ├── test_create_notification_config.py
│   │   │   │   ├── test_update_notification_config.py
│   │   │   │   └── test_delete_notification_config.py
│   │   │   ├── queries/
│   │   │   │   ├── test_get_notification_config.py
│   │   │   │   └── test_list_notification_configs.py
│   │   │   └── conftest.py
│   │   ├── factories.py
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── dto.py
│   └── models.py
```

## Test Structure

**Python Suite Organization:**
```python
# Style: Class-based test grouping
class TestCreateNotificationConfig:
    """Test cases for the create_notification_config command."""

    @pytest.mark.django_db
    def test_create_notification_config_success(self, actor: Actor):
        """Test successfully creating a notification config."""
        # Arrange
        name = "Test Config"
        chat_id = "12345"

        # Act
        result = create_notification_config(actor, name, chat_id)

        # Assert
        expected = NotificationConfigDTO(
            id=result.id,
            name=name,
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id=chat_id,
        )
        assert result == expected
```

**Patterns:**
- Test methods start with `test_` prefix
- Class names start with `Test`
- Docstrings document what is being tested
- AAA pattern: Arrange (setup), Act (execute), Assert (verify)
- Comments mark each section: `# Arrange`, `# Act`, `# Then`, `# Given/When/Then`
- Use descriptive test names: `test_create_notification_config_with_none_name_is_converted_to_empty_string`

**TypeScript Suite Organization:**
```typescript
describe('OfferFilters', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    mockMutate.mockClear()
  })

  it('renders collapsed by default', () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )
    expect(screen.getByText('Smart Filters')).toBeInTheDocument()
  })

  it('expands when clicked', async () => {
    renderWithProviders(...)
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)
    await waitFor(() => {
      expect(screen.getByText('Add group')).toBeInTheDocument()
    })
  })
})
```

**Patterns:**
- Use `describe()` blocks for test grouping
- Use `it()` or `test()` for individual tests
- `beforeEach()` and `afterEach()` for setup/cleanup
- Test names describe behavior: "renders collapsed by default", "expands when clicked"
- Use `@testing-library` query patterns: `screen.getByRole()`, `screen.getByText()`, `screen.getByPlaceholderText()`
- Async tests use `waitFor()` for assertions on async updates

## Mocking

**Python Framework:** unittest.mock

**Patterns:**
```python
from unittest.mock import patch, Mock

# Patch at import location
with patch('shargain.offers.services.batch_create.NewOfferNotificationService') as mock_notification_service_class:
    # Mock the instance
    mock_instance = mock_notification_service_class.return_value
    mock_instance.run.return_value = None

    # Use the mocked service
    service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
    service.notification_service_class = mock_notification_service_class
    service.run()

    # Assert on calls
    mock_notification_service_class.assert_called_once()
    filtered_offers = mock_notification_service_class.call_args[0][0]
    assert len(filtered_offers) == 1
```

**TypeScript Framework:** vitest built-in vi

**Patterns:**
```typescript
import { vi } from 'vitest'

// Mock module
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      const translations: Record<string, string> = {
        'filters.title': 'Smart Filters',
        // ... translations
      }
      return translations[key] || key
    },
  }),
}))

// Mock function
const mockMutate = vi.fn()
vi.mock('./useMonitors', () => ({
  useUpdateFiltersMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    isError: false,
    error: null,
  }),
}))

// In tests
mockMutate.mockClear()
// assertions
expect(mockMutate).toHaveBeenCalled()
```

**What to Mock:**
- External services (NewOfferNotificationService, API calls)
- i18n hooks and translations
- Mutation/query hooks (useUpdateFiltersMutation)
- Context providers (AuthProvider, QueryClientProvider)

**What NOT to Mock:**
- Core business logic (filter evaluation, validation)
- Model factories (use actual factories)
- Database operations (use `@pytest.mark.django_db` for real DB access)
- React hooks like `useState`, `useEffect` (test behavior through UI)

## Fixtures and Factories

**Python Test Data:**

Factories use `factory-boy` pattern:
```python
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = CustomUser
        django_get_or_create = ("username",)

    username = LazyAttribute(lambda _: fake.user_name())
    email = LazyAttribute(lambda _: fake.email())
    password = LazyFunction(lambda: make_password("testpass123"))
    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    is_active = True
    is_staff = False
    is_superuser = False
```

Fixtures in conftest.py:
```python
@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory.create()

@pytest.fixture
def actor(user):
    return Actor(user_id=user.id)

@pytest.fixture
def scraping_target(user) -> ScrappingTarget:
    return ScrappingTargetFactory(owner=user)
```

**Location:**
- Factories: `shargain/*/tests/factories.py` per app
- Shared fixtures: `shargain/*/tests/conftest.py` per app
- Global fixtures: Add to root `conftest.py` if created

**TypeScript Test Data:**

Render wrapper pattern:
```typescript
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

// Usage in tests
renderWithProviders(
  <OfferFilters
    targetId={1}
    urlId={1}
    initialFilters={null}
  />
)
```

Test objects inline:
```typescript
const initialFilters: FiltersConfigSchema = {
  ruleGroups: [
    {
      logic: 'and',
      rules: [
        {
          field: 'title',
          operator: 'contains',
          value: 'apartment',
          caseSensitive: false,
        },
      ],
    },
  ],
}
```

## Coverage

**Requirements:** Not enforced by CI/CD but tracked

**View Coverage:**
```bash
# Python
pytest --cov=shargain --cov-report=html shargain
# Coverage report in htmlcov/index.html

# TypeScript
vitest run --coverage
```

**Configuration (Python):**
- `pyproject.toml` defines coverage rules:
  ```
  [tool.coverage.run]
  branch = true

  [tool.coverage.report]
  exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
  omit = [
      "manage.py",
      "**/wsgi.py",
      "**/asgi.py",
      "**/settings/*.py",
      "**/migrations/*.py",
  ]
  ```

## Test Types

**Python Unit Tests:**
- Scope: Individual functions and methods in isolation
- Location: `shargain/*/tests/test_*.py`
- Approach: Mock external dependencies, test logic in isolation
- Example: Testing `OfferFilterService._evaluate_rule()` with various operators

**Python Integration Tests:**
- Scope: Multiple components working together
- Location: `shargain/*/tests/application/commands/test_*.py`, `shargain/*/tests/application/queries/test_*.py`
- Approach: Use real database with `@pytest.mark.django_db`, create factories for related models
- Example: `test_offer_batch_create_with_filters()` tests service with actual database models

**Python Application Layer Tests:**
- Scope: Commands and queries with business logic
- Location: `shargain/notifications/tests/application/commands/`, `shargain/notifications/tests/application/queries/`
- Pattern: Test command/query functions return expected DTO
- Use fixtures from conftest.py with `@pytest.fixture`

**TypeScript Component Tests:**
- Scope: React component rendering and user interaction
- Location: `frontend/src/components/**/*.test.tsx`
- Approach: Render with providers, query DOM, fire events, assert on rendered output
- Example: `OfferFilters.test.tsx` tests UI interactions and state changes

**E2E Tests:**
- Not detected in codebase
- Would typically use Playwright or Cypress

## Common Patterns

**Python Async Testing:**
```python
# Not explicitly used; Django ORM handles async transparently
# Mark tests with @pytest.mark.django_db for database access
@pytest.mark.django_db
def test_something():
    user = UserFactory.create()  # Direct database access
```

**Python Error Testing:**
```python
# Test that exceptions are raised
def test_invalid_operator_raises_value_error(self):
    service = OfferFilterService({...})
    with pytest.raises(ValueError, match="Unknown operator"):
        service._evaluate_rule(offer, {"operator": "invalid", ...})
```

**TypeScript Async Testing:**
```typescript
// Test async state updates with waitFor
it('expands when clicked', async () => {
  renderWithProviders(...)
  fireEvent.click(trigger)

  await waitFor(() => {
    expect(screen.getByText('Add group')).toBeInTheDocument()
  })
})
```

**TypeScript Form Validation Testing:**
```typescript
// Test validation errors
const result = schema.safeParse(data)
if (!result.success) {
  const fieldErrors = result.error.flatten().fieldErrors
  setErrors({
    email: fieldErrors.email?.[0],
    password: fieldErrors.password?.[0]
  })
}
// Assert on errors object
expect(errors.email).toEqual("Username or email is required")
```

**Python Fixture Inheritance Pattern:**
```python
# Fixtures can depend on other fixtures
@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory.create()

@pytest.fixture
def actor(user):  # Depends on user fixture
    return Actor(user_id=user.id)

# Tests use both implicitly
def test_something(actor: Actor):  # Gets user and actor
    result = create_notification_config(actor, ...)
```

**TypeScript Provider Pattern:**
```typescript
// Mock providers for tests
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

// Use consistently in all component tests
renderWithProviders(<OfferFilters ... />)
```

## Pytest Markers and Configuration

**Django-specific:**
- `@pytest.mark.django_db` - enables database access for test
- `--nomigrations` - skip running migrations (configured in pyproject.toml)
- `DJANGO_SETTINGS_MODULE = "shargain.settings.tests"` - use test settings

**Test discovery:**
- Files: `test_*.py`, `*_tests.py`, `tests.py`
- Skip: `.git/*`, `.mypy_cache/*`, `.pytest_cache/*`, `migrations/*`, `settings/*`

---

*Testing analysis: 2026-01-24*
