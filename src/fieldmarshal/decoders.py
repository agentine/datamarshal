"""Built-in type decoders for deserialization (JSON values -> Python objects)."""

from __future__ import annotations

import datetime
import enum
from decimal import Decimal
from pathlib import Path, PurePath
from typing import Any
from uuid import UUID


def decode_datetime(val: Any) -> datetime.datetime:
    """Decode ISO 8601 string to datetime."""
    if isinstance(val, datetime.datetime):
        return val
    return datetime.datetime.fromisoformat(val)


def decode_date(val: Any) -> datetime.date:
    """Decode ISO 8601 string to date."""
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
        return val
    return datetime.date.fromisoformat(val)


def decode_time(val: Any) -> datetime.time:
    """Decode ISO 8601 string to time."""
    if isinstance(val, datetime.time):
        return val
    return datetime.time.fromisoformat(val)


def decode_uuid(val: Any) -> UUID:
    """Decode string to UUID."""
    if isinstance(val, UUID):
        return val
    return UUID(val)


def decode_decimal(val: Any) -> Decimal:
    """Decode string to Decimal."""
    if isinstance(val, Decimal):
        return val
    return Decimal(val)


def decode_path(val: Any) -> Path:
    """Decode string to Path."""
    if isinstance(val, Path):
        return val
    return Path(val)


def decode_bytes(val: Any) -> bytes:
    """Decode base64 string to bytes."""
    if isinstance(val, bytes):
        return val
    import base64

    return base64.b64decode(val)


def _make_enum_decoder(enum_cls: type[enum.Enum]) -> Any:
    """Create a decoder for the given Enum class."""
    return enum_cls


_DECODER_MAP: dict[type, Any] = {
    datetime.datetime: decode_datetime,
    datetime.date: decode_date,
    datetime.time: decode_time,
    UUID: decode_uuid,
    Decimal: decode_decimal,
    Path: decode_path,
    PurePath: decode_path,
    bytes: decode_bytes,
}


def get_decoder(tp: type) -> Any | None:
    """Get a built-in decoder for the given type, or None."""
    if isinstance(tp, type) and issubclass(tp, enum.Enum):
        return tp
    return _DECODER_MAP.get(tp)
