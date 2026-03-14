"""Field and global configuration for serialization behavior."""

from __future__ import annotations

import dataclasses
import re
from enum import Enum
from typing import Any, Callable


_MISSING = object()


class LetterCase(Enum):
    """Letter case conversion options for field names."""

    CAMEL = "camelCase"
    PASCAL = "PascalCase"
    SNAKE = "snake_case"
    KEBAB = "kebab-case"


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _to_pascal(name: str) -> str:
    return "".join(p.capitalize() for p in name.split("_"))


def _to_snake(name: str) -> str:
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1).lower()


def _to_kebab(name: str) -> str:
    return _to_snake(name).replace("_", "-")


_CASE_CONVERTERS: dict[LetterCase, Callable[[str], str]] = {
    LetterCase.CAMEL: _to_camel,
    LetterCase.PASCAL: _to_pascal,
    LetterCase.SNAKE: _to_snake,
    LetterCase.KEBAB: _to_kebab,
}


def convert_case(name: str, case: LetterCase) -> str:
    """Convert a field name to the specified letter case."""
    return _CASE_CONVERTERS[case](name)


@dataclasses.dataclass(frozen=True, slots=True)
class FieldConfig:
    """Per-field serialization configuration.

    Used via: dataclasses.field(metadata={"fieldmarshal": FieldConfig(...)})
    """

    field_name: str | None = None
    exclude: bool = False
    encoder: Callable[[Any], Any] | None = None
    decoder: Callable[[Any], Any] | None = None
    default: Any = _MISSING


@dataclasses.dataclass(frozen=True, slots=True)
class GlobalConfig:
    """Global serialization configuration for a decorated class."""

    letter_case: LetterCase | None = None
    strict: bool = True


def get_field_config(field: dataclasses.Field[Any]) -> FieldConfig | None:
    """Extract FieldConfig from a dataclass field's metadata."""
    val: FieldConfig | None = field.metadata.get("fieldmarshal")
    return val
