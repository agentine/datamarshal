"""A modern, lightweight dataclass serialization library for Python — the better alternative to dataclasses-json"""

from fieldmarshal.config import FieldConfig, GlobalConfig, LetterCase
from fieldmarshal.core import dataclass_json

__all__ = [
    "dataclass_json",
    "FieldConfig",
    "GlobalConfig",
    "LetterCase",
]
