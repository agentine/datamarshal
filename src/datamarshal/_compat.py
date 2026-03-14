"""Python version compatibility utilities."""

from __future__ import annotations

import sys
import typing
from typing import Any, get_type_hints

PYTHON_310 = sys.version_info >= (3, 10)
PYTHON_311 = sys.version_info >= (3, 11)
PYTHON_312 = sys.version_info >= (3, 12)


def get_resolved_hints(cls: type) -> dict[str, Any]:
    """Get fully resolved type hints for a class."""
    return get_type_hints(cls, include_extras=True)


def get_origin(tp: Any) -> Any | None:
    """Get the origin of a generic type (e.g., list for list[int])."""
    return typing.get_origin(tp)


def get_args(tp: Any) -> tuple[Any, ...]:
    """Get the type arguments of a generic type (e.g., (int,) for list[int])."""
    return typing.get_args(tp)
