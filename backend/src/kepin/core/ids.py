from __future__ import annotations
import uuid


def new_uuid() -> str:
    """Generate a new UUID v4 as string."""
    return str(uuid.uuid4())


def parse_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)
