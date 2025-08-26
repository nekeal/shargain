from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    """Represents a user in the application layer."""

    user_id: int
