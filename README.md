# fieldmarshal

[![PyPI](https://img.shields.io/pypi/v/fieldmarshal)](https://pypi.org/project/fieldmarshal/)
[![Python](https://img.shields.io/pypi/pyversions/fieldmarshal)](https://pypi.org/project/fieldmarshal/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, lightweight dataclass serialization library for Python — the better alternative to dataclasses-json.

Zero dependencies. Python 3.10+.

## Why fieldmarshal?

[dataclasses-json](https://github.com/lidatong/dataclasses-json) was the go-to library for dataclass JSON serialization, but its maintainer has stepped away and the project is effectively abandoned: no releases since June 2024, no Python 3.13+ support, broken marshmallow compatibility, and 159+ open issues.

fieldmarshal is a clean replacement:

| | dataclasses-json | fieldmarshal |
|---|---|---|
| Dependencies | marshmallow, marshmallow-enum, typing-inspect | **None (stdlib only)** |
| Python support | 3.7–3.12 | **3.10+ (including 3.13+)** |
| Maintained | No (abandoned 2024) | **Yes** |
| Type resolution | typing-inspect (fragile) | stdlib introspection |
| API style | Mixin or decorator | Decorator only (cleaner) |

## Install

```bash
pip install fieldmarshal
```

## Quick Start

```python
from dataclasses import dataclass
from fieldmarshal import dataclass_json

@dataclass_json
@dataclass
class User:
    name: str
    age: int
    active: bool = True

user = User(name="Alice", age=30)
print(user.to_json())   # {"name": "Alice", "age": 30, "active": true}
print(user.to_dict())   # {"name": "Alice", "age": 30, "active": True}

user2 = User.from_json('{"name": "Bob", "age": 25, "active": false}')
user3 = User.from_dict({"name": "Carol", "age": 28})
```

## Nested Dataclasses

```python
@dataclass_json
@dataclass
class Address:
    street: str
    city: str

@dataclass_json
@dataclass
class Person:
    name: str
    address: Address

p = Person(name="Alice", address=Address(street="123 Main", city="NYC"))
print(p.to_json())
# {"name": "Alice", "address": {"street": "123 Main", "city": "NYC"}}

Person.from_dict({"name": "Alice", "address": {"street": "123 Main", "city": "NYC"}})
```

## Collection Types

`list`, `dict`, `set`, `tuple`, `Optional`, and `Union` are all supported:

```python
@dataclass_json
@dataclass
class Config:
    tags: list[str]
    scores: dict[str, int]
    unique_ids: set[int]
    coords: tuple[float, float]
    nickname: str | None = None
```

## Field Configuration

Rename fields, exclude fields, or use custom encoders/decoders via `FieldConfig`:

```python
from dataclasses import field
from fieldmarshal import FieldConfig

@dataclass_json
@dataclass
class Model:
    user_name: str = field(
        metadata={"fieldmarshal": FieldConfig(field_name="userName")}
    )
    password: str = field(
        metadata={"fieldmarshal": FieldConfig(exclude=True, default="secret")}
    )

m = Model(user_name="alice", password="hunter2")
print(m.to_dict())  # {"userName": "alice"}
```

### FieldConfig Options

| Option | Type | Description |
|--------|------|-------------|
| `field_name` | `str \| None` | Override the JSON key name |
| `exclude` | `bool` | Exclude field from serialization |
| `encoder` | `Callable \| None` | Custom encoder function |
| `decoder` | `Callable \| None` | Custom decoder function |
| `default` | `Any` | Default value when excluded or missing |

## Letter Case Conversion

Automatically convert field names to camelCase, PascalCase, snake_case, or kebab-case:

```python
from fieldmarshal import LetterCase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiResponse:
    first_name: str
    last_name: str
    is_active: bool = True

r = ApiResponse(first_name="Alice", last_name="Smith")
print(r.to_dict())  # {"firstName": "Alice", "lastName": "Smith", "isActive": true}
```

## Built-in Type Handlers

These types are automatically serialized/deserialized:

| Python Type | JSON Representation |
|-------------|-------------------|
| `datetime` | ISO 8601 string |
| `date` | ISO 8601 string |
| `time` | ISO 8601 string |
| `UUID` | String |
| `Decimal` | String |
| `Enum` | Value |
| `Path` | String |
| `bytes` | Base64 string |
| `set` / `frozenset` | Sorted list |

## Strict and Lenient Modes

By default, fieldmarshal uses strict mode — unknown fields and type mismatches raise errors:

```python
@dataclass_json(strict=True)   # default
@dataclass
class StrictModel:
    name: str
    age: int

# Raises ValueError: Unknown fields for StrictModel: {'extra'}
StrictModel.from_dict({"name": "A", "age": 1, "extra": True})

# Raises TypeError: Expected int, got str
StrictModel.from_dict({"name": "A", "age": "not_a_number"})
```

Lenient mode ignores unknown fields and does best-effort type coercion:

```python
@dataclass_json(strict=False)
@dataclass
class LenientModel:
    name: str
    age: int

m = LenientModel.from_dict({"name": "A", "age": "42", "extra": True})
# m.age == 42 (coerced from str), extra is ignored
```

## Migrating from dataclasses-json

fieldmarshal is a drop-in replacement for most dataclasses-json usage:

| dataclasses-json | fieldmarshal |
|-----------------|--------------|
| `@dataclass_json` | `@dataclass_json` |
| `.to_json()` | `.to_json()` |
| `.from_json(s)` | `.from_json(s)` |
| `.to_dict()` | `.to_dict()` |
| `.from_dict(d)` | `.from_dict(d)` |
| `DataClassJsonMixin` | `@dataclass_json` decorator |
| `config(field_name=...)` | `FieldConfig(field_name=...)` |
| `config(exclude=...)` | `FieldConfig(exclude=True)` |
| `config(encoder=..., decoder=...)` | `FieldConfig(encoder=..., decoder=...)` |
| `config(letter_case=...)` | `@dataclass_json(letter_case=LetterCase.CAMEL)` |
| marshmallow dependency | No dependencies |

### Before (dataclasses-json)

```python
from dataclasses_json import dataclass_json, config

@dataclass_json
@dataclass
class User:
    user_name: str = field(metadata=config(field_name="userName"))
```

### After (fieldmarshal)

```python
from fieldmarshal import dataclass_json, FieldConfig

@dataclass_json
@dataclass
class User:
    user_name: str = field(metadata={"fieldmarshal": FieldConfig(field_name="userName")})
```

## API Reference

### `@dataclass_json`

Decorator that adds serialization methods to a dataclass.

```python
@dataclass_json
@dataclass_json(letter_case=LetterCase.CAMEL, strict=True)
```

**Parameters:**
- `letter_case` (`LetterCase | None`) — automatic field name conversion
- `strict` (`bool`, default `True`) — raise on unknown fields and type mismatches

**Added methods:**
- `to_dict() -> dict` — convert to plain dict
- `to_json(**kwargs) -> str` — convert to JSON string (kwargs passed to `json.dumps`)
- `from_dict(data: dict) -> Self` — class method, reconstruct from dict
- `from_json(s: str, **kwargs) -> Self` — class method, reconstruct from JSON string

### `FieldConfig`

Per-field serialization configuration. Pass via `dataclasses.field(metadata={"fieldmarshal": FieldConfig(...)})`.

```python
@dataclass
class Model:
    name: str = field(metadata={"fieldmarshal": FieldConfig(field_name="Name")})
```

**Fields:**
- `field_name` (`str | None`) — override the JSON key name
- `exclude` (`bool`, default `False`) — exclude this field from serialization
- `encoder` (`Callable | None`) — custom encoder for this field
- `decoder` (`Callable | None`) — custom decoder for this field
- `default` (`Any`) — default value used when the field is excluded or missing during deserialization

### `LetterCase`

Enum for automatic field name case conversion.

| Value | Converts `first_name` to |
|-------|--------------------------|
| `LetterCase.CAMEL` | `firstName` |
| `LetterCase.PASCAL` | `FirstName` |
| `LetterCase.SNAKE` | `first_name` (no-op) |
| `LetterCase.KEBAB` | `first-name` |

### `GlobalConfig`

Internal configuration object stored on each decorated class as `__fieldmarshal_config__`. You do not normally need to use this directly — `@dataclass_json` parameters map onto it automatically. Exported for advanced use cases (e.g. inspecting a class's configuration at runtime).

```python
from fieldmarshal import GlobalConfig

cfg = MyModel.__fieldmarshal_config__  # GlobalConfig instance
print(cfg.letter_case)  # LetterCase.CAMEL or None
print(cfg.strict)       # True or False
```

**Fields:**
- `letter_case` (`LetterCase | None`) — active case conversion, or `None` for no conversion
- `strict` (`bool`, default `True`) — whether unknown fields and type mismatches raise errors

## License

MIT
