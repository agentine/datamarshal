# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] — 2026-03-14

### Added
- `@dataclass_json` decorator for opt-in JSON serialization on dataclasses
- `to_dict()` / `to_json()` instance methods and `from_dict()` / `from_json()` class methods
- Nested dataclass serialization and deserialization
- Collection type support: `list`, `dict`, `set`, `tuple`, `Optional`, `Union`
- `FieldConfig` for per-field configuration: rename, exclude, custom encoder/decoder, default value
- `LetterCase` enum with `CAMEL`, `PASCAL`, `SNAKE`, `KEBAB` for automatic field name conversion
- `GlobalConfig` for per-class configuration (accessible via `__fieldmarshal_config__`)
- Built-in type handlers: `datetime`, `date`, `time`, `UUID`, `Decimal`, `Enum`, `Path`, `bytes`
- Strict mode (default): raises on unknown fields and type mismatches
- Lenient mode (`strict=False`): ignores unknown fields, coerces primitive types
- Per-class metadata cache for fast repeated serialization
- Full Python 3.10–3.13+ support with zero dependencies
