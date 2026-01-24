# Coding Conventions

**Analysis Date:** 2026-01-24

## Naming Patterns

**Files:**
- Python modules use snake_case: `filter_service.py`, `batch_create.py`, `setup_scraping_target_handler.py`
- Python test files follow pattern `test_*.py`, `*_tests.py`, or `tests.py`: `test_models.py`, `test_batch_create.py`, `test_create_notification_config.py`
- TypeScript/React files use kebab-case for components: `login-form.tsx`, `offer-filters.tsx`, `monitored-websites.tsx`
- Exported components use PascalCase: `function OfferFilters()`, `export { Button }`

**Functions:**
- Python functions use snake_case: `create_notification_config()`, `apply_filters()`, `_evaluate_offer()` (private with underscore prefix)
- TypeScript functions use camelCase: `handleSubmit()`, `getFieldError()`, `validateFilters()`, `renderWithProviders()`

**Variables:**
- Python constants and class attributes use UPPER_SNAKE_CASE: `DEFAULT_CHANNEL = "TELEGRAM"`, `DJANGO_SETTINGS_MODULE`
- Python instance variables use snake_case: `self.filters`, `notification_config`, `rule_groups`
- TypeScript variables use camelCase: `isOpen`, `validationErrors`, `mockMutate`, `initialFilters`
- React hooks use camelCase starting with `use`: `useTranslation()`, `useAuth()`, `useUpdateFiltersMutation()`

**Types:**
- Python dataclasses and DTOs use PascalCase: `NotificationConfigDTO`, `LoginRequest`, `SignupRequest`
- TypeScript interfaces use PascalCase: `OfferFiltersProps`, `FiltersConfigSchema`, `RuleGroupSchema`
- Python model classes use PascalCase: `CustomUser`, `NotificationConfig`, `ScrappingTarget`

## Code Style

**Formatting:**
- Python: Ruff formatter with 120 character line length (configured in `pyproject.toml`)
- TypeScript/React: ESLint with TanStack config, no explicit line length enforced but following modern standards
- Imports organized by type in both languages

**Linting:**
- Python: Ruff with comprehensive ruleset including flake8 plugins (S, DJ, PT, B, E, W, F, N, UP, I, C9)
- TypeScript: ESLint with TanStack preset, React plugin, React Hooks plugin
- Both enforce strict type checking (mypy for Python, TSC for TypeScript)

**Pre-commit hooks (Python):**
- `ruff format` - code formatting
- `ruff check --fix` - linting with autofix
- `migrations-check` - verify Django migrations created
- `mypy-check` - type checking
- `django-upgrade` - upgrade Django syntax to 5.1

## Import Organization

**Python:**
1. Standard library imports: `import secrets`, `from datetime import timedelta`
2. Django imports: `from django.db import models`, `from django.utils.translation import gettext_lazy as _`
3. Third-party imports: `from rest_framework import serializers`, `from pydantic import AfterValidator`
4. Local app imports: `from shargain.accounts.models import CustomUser`
5. Type hints: Use `from typing import Annotated` for complex annotations

**TypeScript:**
1. React and React ecosystem: `import React from "react"`, `import { useTranslation } from "react-i18next"`
2. Third-party UI/utilities: `import { Button } from "@/components/ui/button"`, `import { z } from "zod"`
3. Local imports: `import cn from "@/lib/utils"`, `from ./useMonitors`
4. Path aliases: `@/*` maps to `./src/*` (configured in `tsconfig.json`)

**Django-specific:**
- Settings file uses wildcard imports with exemptions: `**/settings/**` allows `F405` and `F403` per-file-ignore

## Error Handling

**Python:**
- Custom exception hierarchy with base class `ApplicationException` in `shargain/commons/application/exceptions.py`
- Exceptions define `code` and `message` class attributes: `code: str = "application_error"`
- Exceptions raise with `super().__init__(self.message)` pattern
- Application layer raises custom exceptions, handlers convert to HTTP responses
- No bare `except:` clauses; use specific exception types

**TypeScript:**
- Error handling in async operations using try-catch blocks
- Form validation using Zod: `result = schema.safeParse(data)`
- API errors captured in state: `const [apiError, setApiError] = useState("")`
- Mock errors in tests: `isError: false, error: null` properties on hook returns
- Validation errors stored as array: `validationErrors: z.ZodError | null`

## Logging

**Framework:** Standard Python `print()` for quick feedback (e.g., line 77 in `shargain/public_api/auth.py`)

**Patterns:**
- Limited logging observed in codebase
- Debug output via `print()` statements in endpoints
- Test output via pytest fixture setup/teardown

**Recommendations for future:**
- Use Python's `logging` module with configured loggers per module
- Structured logging with context (user_id, request_id)
- Log levels: DEBUG for development, INFO for business events, WARNING for recoverable issues, ERROR for failures

## Comments

**When to Comment:**
- Complex logic explained with docstrings: `"""Service to filter offers based on rule groups with configurable logic."""`
- Algorithm explanation: See `OfferFilterService._evaluate_offer()` which documents the logic flow
- Non-obvious business rules: `# Default: OR` inline comments for implicit defaults

**Docstring/Documentation:**
- Functions use docstring format:
  ```python
  def create_notification_config(actor, name, chat_id, channel=...):
      """Create a new notification configuration.

      Args:
          actor: The actor performing the command
          name: The display name
          chat_id: The Telegram chat ID
          channel: The notification channel (defaults to Telegram)

      Returns:
          A NotificationConfigDTO containing the created configuration data
      """
  ```
- Classes document purpose and behavior: `"""Service to filter offers based on rule groups with configurable logic."""`
- React components define Props interface: `interface OfferFiltersProps { targetId: number; urlId: number; initialFilters: FiltersConfigSchema | null; }`

## Function Design

**Size:** Most functions 10-50 lines; larger services decomposed into private methods (e.g., `_evaluate_offer()`, `_evaluate_group()`, `_evaluate_rule()`)

**Parameters:**
- Python: Use descriptive names, type hints enforced by mypy
  ```python
  def apply_filters(self, offers: list[Offer]) -> list[Offer]:
  ```
- TypeScript: Use interfaces for component props, destructure in parameters
  ```typescript
  function OfferFilters({ targetId, urlId, initialFilters }: OfferFiltersProps)
  ```

**Return Values:**
- Python: Return DTOs or model instances, use `None` explicitly for optional returns
  ```python
  def create_notification_config(...) -> NotificationConfigDTO:
  ```
- TypeScript: Use union types for conditional returns
  ```typescript
  result: NotificationConfigDTO | null
  ```

## Module Design

**Exports:**
- Python: Functions and classes exported directly from modules; `__all__` not consistently used
- TypeScript: Named exports preferred; barrel exports in `index.tsx` files for component directories
  ```typescript
  export { Button, buttonVariants }
  export { Input }
  ```

**Barrel Files:** Used in `frontend/src/components/ui/` for re-exporting UI components; allows `import { Button } from "@/components/ui/button"`

**Cohesion:**
- Features organized by domain: `notifications/`, `offers/`, `accounts/`, `telegram/`
- Each feature contains: models, views/endpoints, serializers, services, tests
- Application layer separated: `shargain/*/application/commands/`, `shargain/*/application/queries/`
- Shared utilities in `commons/application/`

## Class/Object Structure

**Django Models:**
- Inherit from `models.Model` or mixin classes like `TimeStampedModel`
- Use `verbose_name` and translation with `gettext_lazy as _`
- Define `__str__()` for readable representation
- Meta class defines verbose names and constraints

**Django Serializers:**
- Inherit from `serializers.ModelSerializer`
- Inner `Meta` class defines model and fields
- Use `by_alias=True` for camelCase conversion via `alias_generator = to_camel`

**Factory Classes (Testing):**
- Inherit from `factory.django.DjangoModelFactory`
- Use `LazyAttribute` and `LazyFunction` for dynamic values
- Set `Meta.django_get_or_create` to prevent duplicate creation
- Include docstring: `"""Factory for creating test users."""`

**DTOs (Data Transfer Objects):**
- Use frozen dataclasses: `@dataclass(frozen=True)`
- Define all fields with type hints and optional markers
- No methods beyond `__init__` and built-in dunder methods

## Type Annotations

**Python:**
- Strict mypy config: `check_untyped_defs = true`
- Union syntax: `str | None` (Python 3.13+ style)
- Type hints on function parameters and return values
- Ignore mypy for migrations, settings, and some third-party packages

**TypeScript:**
- Strict tsconfig: `"strict": true`, `"noUnusedLocals": true`, `"noUnusedParameters": true`
- Type narrowing with discriminated unions
- Generic types for reusable components

---

*Convention analysis: 2026-01-24*
