"""Core decorator and serialization logic."""

from __future__ import annotations

import dataclasses
import json
from typing import Any, TypeVar

from fieldmarshal._compat import get_args, get_origin, get_resolved_hints
from fieldmarshal.config import (
    _MISSING,
    FieldConfig,
    GlobalConfig,
    convert_case,
    get_field_config,
)
from fieldmarshal.encoders import get_encoder
from fieldmarshal.types import (
    get_union_args,
    is_dataclass_type,
    is_generic_dict,
    is_generic_list,
    is_generic_set,
    is_generic_tuple,
    is_optional,
    is_union,
    unwrap_optional,
)

T = TypeVar("T")

# Per-class cache: cls -> (field_name -> (json_key, type_hint, field_config))
_CLASS_META: dict[type, dict[str, tuple[str, Any, FieldConfig | None]]] = {}


def _build_class_meta(
    cls: type, config: GlobalConfig
) -> dict[str, tuple[str, Any, FieldConfig | None]]:
    """Build and cache field metadata for a decorated class."""
    if cls in _CLASS_META:
        return _CLASS_META[cls]

    hints = get_resolved_hints(cls)
    fields = dataclasses.fields(cls)
    meta: dict[str, tuple[str, Any, FieldConfig | None]] = {}

    for f in fields:
        fc = get_field_config(f)
        # Determine JSON key name
        json_key = f.name
        if fc and fc.field_name is not None:
            json_key = fc.field_name
        elif config.letter_case is not None:
            json_key = convert_case(f.name, config.letter_case)
        meta[f.name] = (json_key, hints.get(f.name, Any), fc)

    _CLASS_META[cls] = meta
    return meta


def _encode_value(val: Any, type_hint: Any, fc: FieldConfig | None) -> Any:
    """Encode a single value to a JSON-compatible representation."""
    if val is None:
        return None

    # Per-field custom encoder takes priority
    if fc and fc.encoder is not None:
        return fc.encoder(val)

    # Dataclass -> recurse
    if dataclasses.is_dataclass(val) and not isinstance(val, type):
        return _to_dict_inner(val)

    # Generic collections
    if is_generic_list(type_hint) or is_generic_set(type_hint):
        args = get_args(type_hint)
        elem_type = args[0] if args else Any
        items = list(val)
        if is_generic_set(type_hint):
            # Sort sets for deterministic output
            try:
                items = sorted(items)
            except TypeError:
                items = sorted(items, key=lambda x: (type(x).__name__, str(x)))
        return [_encode_value(item, elem_type, None) for item in items]

    if is_generic_tuple(type_hint):
        args = get_args(type_hint)
        if args and args[-1] is Ellipsis:
            elem_type = args[0]
            return [_encode_value(item, elem_type, None) for item in val]
        return [
            _encode_value(item, args[i] if i < len(args) else Any, None)
            for i, item in enumerate(val)
        ]

    if is_generic_dict(type_hint):
        args = get_args(type_hint)
        key_type = args[0] if args else Any
        val_type = args[1] if len(args) > 1 else Any
        return {
            _encode_value(k, key_type, None): _encode_value(v, val_type, None)
            for k, v in val.items()
        }

    # Optional/Union: encode the actual value with its unwrapped type
    if is_optional(type_hint):
        inner = unwrap_optional(type_hint)
        return _encode_value(val, inner, None)
    if is_union(type_hint):
        # Encode as the value's actual type
        return _encode_value(val, type(val), None)

    # Bare collection types (without generic params)
    origin = get_origin(type_hint)
    actual_type = origin if origin is not None else type_hint

    if isinstance(actual_type, type):
        encoder = get_encoder(actual_type)
        if encoder is not None:
            return encoder(val)

    # Also check the value's actual type for encoder lookup
    encoder = get_encoder(type(val))
    if encoder is not None:
        return encoder(val)

    return val


def _to_dict_inner(obj: Any) -> dict[str, Any]:
    """Convert a dataclass instance to a dict (inner recursive call)."""
    cls = type(obj)
    config = getattr(cls, "__fieldmarshal_config__", GlobalConfig())
    meta = _build_class_meta(cls, config)
    result: dict[str, Any] = {}

    for field_name, (json_key, type_hint, fc) in meta.items():
        if fc and fc.exclude:
            continue
        val = getattr(obj, field_name)
        result[json_key] = _encode_value(val, type_hint, fc)

    return result


def _decode_value(val: Any, type_hint: Any, fc: FieldConfig | None, strict: bool) -> Any:
    """Decode a JSON value to the target type."""
    if val is None:
        return None

    # Per-field custom decoder
    if fc and fc.decoder is not None:
        return fc.decoder(val)

    # Optional: unwrap and decode inner
    if is_optional(type_hint):
        inner = unwrap_optional(type_hint)
        return _decode_value(val, inner, None, strict)

    # Union (non-Optional): try each type
    if is_union(type_hint):
        for arg in get_union_args(type_hint):
            if arg is type(None):
                continue
            try:
                return _decode_value(val, arg, None, strict)
            except (TypeError, ValueError, KeyError):
                continue
        if strict:
            raise TypeError(f"Cannot decode {val!r} as {type_hint}")
        return val

    # Nested dataclass
    if is_dataclass_type(type_hint) and isinstance(val, dict):
        return _from_dict_inner(type_hint, val)

    # Generic list
    if is_generic_list(type_hint):
        args = get_args(type_hint)
        elem_type = args[0] if args else Any
        return [_decode_value(item, elem_type, None, strict) for item in val]

    # Generic set
    if is_generic_set(type_hint):
        args = get_args(type_hint)
        elem_type = args[0] if args else Any
        return {_decode_value(item, elem_type, None, strict) for item in val}

    # Generic tuple
    if is_generic_tuple(type_hint):
        args = get_args(type_hint)
        if args and args[-1] is Ellipsis:
            elem_type = args[0]
            return tuple(_decode_value(item, elem_type, None, strict) for item in val)
        return tuple(
            _decode_value(val[i], args[i] if i < len(args) else Any, None, strict)
            for i in range(len(val))
        )

    # Generic dict
    if is_generic_dict(type_hint):
        args = get_args(type_hint)
        key_type = args[0] if args else Any
        val_type = args[1] if len(args) > 1 else Any
        return {
            _decode_value(k, key_type, None, strict): _decode_value(
                v, val_type, None, strict
            )
            for k, v in val.items()
        }

    # Built-in type decoders
    from fieldmarshal.decoders import get_decoder

    if isinstance(type_hint, type):
        decoder = get_decoder(type_hint)
        if decoder is not None:
            return decoder(val)

    # Lenient mode: try basic coercion for primitive types
    if isinstance(type_hint, type) and type_hint in (str, int, float, bool):
        if not isinstance(val, type_hint):
            if strict:
                raise TypeError(
                    f"Expected {type_hint.__name__}, got {type(val).__name__}: {val!r}"
                )
            try:
                return type_hint(val)
            except (TypeError, ValueError):
                return val

    return val


def _from_dict_inner(cls: type, data: dict[str, Any]) -> Any:
    """Reconstruct a dataclass instance from a dict (inner recursive call)."""
    config = getattr(cls, "__fieldmarshal_config__", GlobalConfig())
    meta = _build_class_meta(cls, config)
    strict = config.strict

    # Build reverse map: json_key -> (field_name, type_hint, fc)
    key_map: dict[str, tuple[str, Any, FieldConfig | None]] = {}
    for field_name, (json_key, type_hint, fc) in meta.items():
        key_map[json_key] = (field_name, type_hint, fc)

    kwargs: dict[str, Any] = {}
    used_keys: set[str] = set()

    for json_key, (field_name, type_hint, fc) in key_map.items():
        if fc and fc.exclude:
            # Use FieldConfig default or dataclass default
            if fc.default is not _MISSING:
                kwargs[field_name] = fc.default
            continue

        if json_key in data:
            kwargs[field_name] = _decode_value(data[json_key], type_hint, fc, strict)
            used_keys.add(json_key)
        elif fc and fc.default is not _MISSING:
            kwargs[field_name] = fc.default

    # Strict mode: reject unknown keys
    if strict:
        unknown = set(data.keys()) - used_keys
        if unknown:
            raise ValueError(
                f"Unknown fields for {cls.__name__}: {unknown}"
            )

    return cls(**kwargs)


def dataclass_json(
    cls: type[T] | None = None,
    *,
    letter_case: Any | None = None,
    strict: bool = True,
) -> Any:
    """Decorator that adds JSON serialization methods to a dataclass.

    Can be used with or without arguments:
        @dataclass_json
        class Foo: ...

        @dataclass_json(letter_case=LetterCase.CAMEL)
        class Bar: ...
    """

    def wrap(cls: type[T]) -> type[T]:
        if not dataclasses.is_dataclass(cls):
            raise TypeError(
                f"@dataclass_json can only be applied to dataclasses, got {cls!r}"
            )

        config = GlobalConfig(letter_case=letter_case, strict=strict)
        cls.__fieldmarshal_config__ = config  # type: ignore[attr-defined]

        # Pre-build metadata cache
        _build_class_meta(cls, config)

        # Add instance methods
        def to_dict(self: Any) -> dict[str, Any]:
            return _to_dict_inner(self)

        def to_json(self: Any, **kw: Any) -> str:
            return json.dumps(_to_dict_inner(self), **kw)

        @classmethod  # type: ignore[misc]
        def from_dict(klass: type[T], data: dict[str, Any]) -> T:
            return _from_dict_inner(klass, data)  # type: ignore[no-any-return]

        @classmethod  # type: ignore[misc]
        def from_json(klass: type[T], s: str, **kw: Any) -> T:
            return _from_dict_inner(klass, json.loads(s, **kw))  # type: ignore[no-any-return]

        cls.to_dict = to_dict  # type: ignore[attr-defined]
        cls.to_json = to_json  # type: ignore[attr-defined]
        cls.from_dict = from_dict  # type: ignore[attr-defined]
        cls.from_json = from_json  # type: ignore[attr-defined]

        return cls

    if cls is not None:
        return wrap(cls)
    return wrap
