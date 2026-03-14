"""Type resolution and generic type handling."""

from __future__ import annotations

import dataclasses
import types
from typing import Any, Union

from datamarshal._compat import get_args, get_origin


def is_dataclass_type(tp: Any) -> bool:
    """Check if a type is a dataclass (not an instance)."""
    return isinstance(tp, type) and dataclasses.is_dataclass(tp)


def is_optional(tp: Any) -> bool:
    """Check if a type is Optional[X] (i.e., Union[X, None])."""
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        args = get_args(tp)
        return type(None) in args
    return False


def unwrap_optional(tp: Any) -> Any:
    """Unwrap Optional[X] to X. Returns tp unchanged if not Optional."""
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        args = get_args(tp)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return tp


def is_union(tp: Any) -> bool:
    """Check if a type is a Union (including Optional)."""
    origin = get_origin(tp)
    return origin is Union or origin is types.UnionType


def get_union_args(tp: Any) -> tuple[Any, ...]:
    """Get the type arguments of a Union type."""
    return get_args(tp)


def is_generic_list(tp: Any) -> bool:
    """Check if type is list[X] or List[X]."""
    return get_origin(tp) is list


def is_generic_dict(tp: Any) -> bool:
    """Check if type is dict[K, V] or Dict[K, V]."""
    return get_origin(tp) is dict


def is_generic_set(tp: Any) -> bool:
    """Check if type is set[X] or Set[X]."""
    return get_origin(tp) is set


def is_generic_tuple(tp: Any) -> bool:
    """Check if type is tuple[X, ...] or Tuple[X, ...]."""
    return get_origin(tp) is tuple
