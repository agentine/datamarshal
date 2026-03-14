# fieldmarshal — Implementation Plan

## Target Library

**dataclasses-json** (lidatong/dataclasses-json)
- 75.5M downloads/month on PyPI
- 1,481 GitHub stars, 94K dependents
- Bus factor: 1 (lidatong: 230 commits, next contributor: 12)
- Last commit: June 2024, last release: v0.6.7 (June 2024)
- Maintainer publicly stepped away (issue #568 — support notice, Nov 2025)
- Archive request filed (issue #569, Dec 2025)
- No Python 3.13+ support
- Broken with recent marshmallow releases
- 159 open issues, 30+ open PRs

## Project Scope

A modern, lightweight Python library for serializing and deserializing `dataclasses` to/from JSON. Zero or minimal dependencies. Full Python 3.10+ support (including 3.13+).

### Core Features (MVP)

1. **`@dataclass_json` decorator** — opt-in serialization for dataclasses
2. **`to_json()` / `from_json()`** — instance and class methods for JSON conversion
3. **`to_dict()` / `from_dict()`** — dict conversion without JSON string step
4. **Nested dataclass support** — recursive serialization/deserialization
5. **Collection types** — `List`, `Dict`, `Set`, `Tuple`, `Optional`, `Union`
6. **Field configuration** — rename fields (camelCase, custom names), exclude fields, default values
7. **Built-in type handlers** — `datetime`, `date`, `time`, `UUID`, `Decimal`, `Enum`, `Path`
8. **Strict/lenient modes** — configurable handling of unknown fields and type mismatches

### Extended Features (Post-MVP)

9. **Schema generation** — JSON Schema output from dataclass definitions
10. **Custom encoders/decoders** — per-field or per-type hooks
11. **Letter case conversion** — camelCase, snake_case, kebab-case automatic conversion
12. **Performance optimization** — compiled serializers for hot paths

## Architecture Overview

```
fieldmarshal/
├── __init__.py          # Public API exports
├── core.py              # @dataclass_json decorator, to_json/from_json/to_dict/from_dict
├── config.py            # FieldConfig, GlobalConfig, letter case options
├── types.py             # Type resolution, generic handling, Union/Optional dispatch
├── encoders.py          # Built-in type encoders (datetime, UUID, Decimal, Enum, etc.)
├── decoders.py          # Built-in type decoders (reverse of encoders)
├── schema.py            # JSON Schema generation (post-MVP)
└── _compat.py           # Python version compatibility (3.10-3.13+)
```

### Design Principles

- **Zero required dependencies** — stdlib only for core functionality
- **Type-hint driven** — use `typing.get_type_hints()` and `dataclasses.fields()` for introspection
- **No marshmallow dependency** — unlike dataclasses-json, avoid marshmallow for schema validation
- **Modern Python** — target 3.10+ only, leverage `match` statements, `|` union syntax, `slots=True`
- **Performance** — cache type resolution and encoder/decoder lookups per class

### Key Differences from dataclasses-json

| Feature | dataclasses-json | fieldmarshal |
|---------|-----------------|--------------|
| Dependencies | marshmallow, marshmallow-enum, typing-inspect | None (stdlib only) |
| Python support | 3.7-3.12 | 3.10+ (including 3.13+) |
| Type resolution | typing-inspect (fragile) | stdlib typing introspection |
| Maintenance | Abandoned | Active |
| API style | Mixin or decorator | Decorator only (cleaner) |

## Deliverables

1. Core library with all MVP features
2. Comprehensive test suite (pytest)
3. README with usage examples and migration guide from dataclasses-json
4. Published on PyPI as `fieldmarshal`
5. CI/CD via GitHub Actions

## Verified Package Name

- **PyPI:** `fieldmarshal` — AVAILABLE (verified 2026-03-14)
