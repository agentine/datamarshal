"""Built-in type encoders for serialization (Python objects -> JSON-compatible values)."""

from __future__ import annotations

import datetime
import enum
import uuid
from decimal import Decimal
from pathlib import Path, PurePath
from typing import Any


def encode_datetime(val: datetime.datetime) -> str:
    """Encode datetime to ISO 8601 string."""
    return val.isoformat()


def encode_date(val: datetime.date) -> str:
    """Encode date to ISO 8601 string."""
    return val.isoformat()


def encode_time(val: datetime.time) -> str:
    """Encode time to ISO 8601 string."""
    return val.isoformat()


def encode_uuid(val: uuid.UUID) -> str:
    """Encode UUID to string."""
    return str(val)


def encode_decimal(val: Decimal) -> str:
    """Encode Decimal to string."""
    return str(val)


def encode_enum(val: enum.Enum) -> Any:
    """Encode Enum to its value."""
    return val.value


def encode_path(val: PurePath) -> str:
    """Encode Path to string."""
    return str(val)


def encode_set(val: set[Any]) -> list[Any]:
    """Encode set to sorted list."""
    return sorted(val, key=_sort_key)


def encode_frozenset(val: frozenset[Any]) -> list[Any]:
    """Encode frozenset to sorted list."""
    return sorted(val, key=_sort_key)


def encode_bytes(val: bytes) -> str:
    """Encode bytes to base64 string."""
    import base64

    return base64.b64encode(val).decode("ascii")


_ENCODER_MAP: dict[type, Any] = {
    datetime.datetime: encode_datetime,
    datetime.date: encode_date,
    datetime.time: encode_time,
    uuid.UUID: encode_uuid,
    Decimal: encode_decimal,
    Path: encode_path,
    PurePath: encode_path,
    bytes: encode_bytes,
    set: encode_set,
    frozenset: encode_frozenset,
}


def get_encoder(tp: type) -> Any | None:
    """Get a built-in encoder for the given type, or None."""
    if issubclass(tp, enum.Enum):
        return encode_enum
    return _ENCODER_MAP.get(tp)


def _sort_key(val: Any) -> Any:
    """Sort key that handles mixed types."""
    return (type(val).__name__, val)
