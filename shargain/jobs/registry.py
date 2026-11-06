"""Registry for job handlers."""

from collections.abc import Callable

_handlers: dict[str, Callable] = {}


def job_handler(job_type: str):
    """Decorator registering a callable as the handler for a given job type."""

    def decorator(func):
        if job_type in _handlers:
            raise ValueError(f"Handler already registered for job type: {job_type}")
        _handlers[job_type] = func
        return func

    return decorator


def get_handler(job_type: str):
    return _handlers.get(job_type)


def registered_types() -> list[str]:
    return list(_handlers.keys())


def clear_registry() -> None:
    """Mostly useful for tests."""
    _handlers.clear()
